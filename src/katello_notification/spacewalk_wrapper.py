
from ConfigParser import SafeConfigParser
import xmlrpclib

import logging

logger = logging.getLogger('katello_notification')


class Spacewalk():
    def __init__(self):
        self._load_config()
        # do this now just so we can print an error on startup of the connection info is wrong
        rpcserver, xmlrpcserver, key = self._create_conns()
        if self.autoregister_hypervisors:
            logger.info("hypervisor autoregistration is enabled")
        else:
            logger.info("hypervisor autoregistration is disabled")

    def _create_conns(self):
        """
        return a tuple with rpcserver, xmlrpcserver, and key. This needs to be
        initialized per-use so we don't time out if there's lots of time between calls
        to spacewalk.
        """
        server = 'https://' + self.sw_host + ':' + self.sw_port
        logger.debug("Initializing spacewalk connection to %s" % server)
        try:
            rpcserver = xmlrpclib.Server(server + '/rpc/api', verbose=0)
            xmlrpcserver = xmlrpclib.Server(server + '/XMLRPC', verbose=0)
        except Exception:
            raise SpacewalkError("Unable to connect to the spacewalk server")
            logger.error("unable to connect to spacewalk server")
        key = rpcserver.auth.login(self.sw_username, self.sw_password)
        logger.debug("Initialized spacewalk connection")
        return (rpcserver, xmlrpcserver, key)

    def _load_config(self):
        CONF = '/etc/katello/katello-notification.conf'
        conf = SafeConfigParser()
        conf.readfp(open(CONF))
        self.sw_host = conf.get('spacewalk', 'host')
        self.sw_port = conf.get('spacewalk', 'port')
        self.sw_username = conf.get('spacewalk', 'username')
        self.sw_password = conf.get('spacewalk', 'password')
        self.autoregister_hypervisors = conf.getboolean('main', 'autoregister_hypervisors')

    def _create_hypervisor(self, hypervisor_hostname):
        rpcserver, xmlrpcserver, key = self._create_conns()
        logger.debug("creating new system in spacewalk")
        new_system = xmlrpcserver.registration.new_system_user_pass(hypervisor_hostname,
                        "unknown", "6Server", "x86_64", self.sw_username, self.sw_password, {})
        xmlrpcserver.registration.refresh_hw_profile(new_system['system_id'], [])
        logger.debug("done creating new system in spacewalk, parsing systemid from xml: %s" % new_system['system_id'])
        # a bit obtuse, but done the same way in rhn client tools (the '3:' strips the 'ID-')
        system_id = xmlrpclib.loads(new_system['system_id'])[0][0]['system_id'][3:]
        # make sure we get an int here, not the str
        return system_id

    def find_hypervisor(self, hypervisor_hostname):
        """
        returns a system ID based on hostname, returns None if no hypervisor is found
        """
        # We are using hypervisor hostname as profile name, to avoid querying lucene.
        # Lucene searches were causing race conditions where we'd create a hypervisor in one thread,
        # then search for it in another and fail, and re-create.

        # beware! there is still a race condition here! We can query in 2
        # threads for the ID and create the system profile twice. Avoiding
        # lucene just tightens the window but does not remove it.
        rpcserver, xmlrpcserver, key = self._create_conns()

        # XXX: HORRIBLE HACK HERE! need to figure out how to make spacewalk reject duplicate registrations
        #import time
        #import random
        #sleeptime = random.randint(0, 20)
        #logger.info("sleeping for %s" % sleeptime)
        #time.sleep(sleeptime)
        # end of hack

        result = rpcserver.system.getId(key, hypervisor_hostname)
        if len(result) == 0 and self.autoregister_hypervisors:
            logger.info("no hypervisor found for %s, creating new record in spacewalk" % hypervisor_hostname)
            system_id = self._create_hypervisor(hypervisor_hostname)
            logger.info("created systemid %s for new hypervisor %s" % (system_id, hypervisor_hostname))
            return system_id
        if len(result) > 1:
            raise RuntimeError("more than one system record found for profile name %s. Please remove extraneous system records in spacewalk." % hypervisor_hostname)
        if len(result) == 1:
            logger.info("found system %s for hostname %s" % (result[0]['id'], hypervisor_hostname))
            return result[0]['id']

    def _assemble_plan(self, guests, hypervisor_name):
        """
        create a plan that can be sent to spacewalk (originally from virt-who)
        """

        events = []

        # the stub_instance_info is not used by the report. When the guest system checks in, it will provide
        # actual hardware info
        stub_instance_info = {
            'vcpus': 1,
            'memory_size': 0,
            'virt_type': 'fully_virtualized',
            'state': 'running',
        }

        # again, remove dashes
        guest_uuids = []
        for g_uuid in guests:
            guest_uuids.append(str(g_uuid).replace("-", ""))

        # TODO: spacewalk wants all zeroes for the hypervisor uuid?
        events.append([0, 'exists', 'system', {'identity': 'host', 'uuid': '0000000000000000'}])

        events.append([0, 'crawl_began', 'system', {}])
        for guest_uuid in guest_uuids:
            stub_instance_info['uuid'] = guest_uuid
            stub_instance_info['name'] = "VM from hypervisor %s" % hypervisor_name
            events.append([0, 'exists', 'domain', stub_instance_info.copy()])

        events.append([0, 'crawl_ended', 'system', {}])

        return events

    def _get_guest_uuid_list(self, sid):
        rpcserver, xmlrpcserver, key = self._create_conns()
        guest_list = rpcserver.system.listVirtualGuests(key, int(sid))
        # strip the list to just the UUIDs
        uuids = map(lambda x: x['uuid'], guest_list)
        logger.debug("guest list for %s: %s" % (sid, uuids))
        return uuids

    def associate_guest(self, instance_uuid, hypervisor_system_id):
        """
        important note: spacewalk does not ever delete guest records, see
        https://git.fedorahosted.org/cgit/spacewalk.git/tree/backend/server/rhnVirtualization.py#n263

        We can take advantage of this to avoid a race condition, since two
        concurrent runs of associate_guest will not clobber each other's plan. At worst,
        the "losing" guest list will have one item marked as "stopped" incorrectly.

        """
        rpcserver, xmlrpcserver, key = self._create_conns()
        logger.debug("searching for guest uuids for %s" % hypervisor_system_id)
        guest_list = self._get_guest_uuid_list(hypervisor_system_id)
        guest_list.append(instance_uuid)
        # TODO: look up hypervisor info here to make plan more detailed?
        plan = self._assemble_plan(guest_list, hypervisor_system_id)
        logger.debug("sending plan %s" % plan)
        systemid = rpcserver.system.downloadSystemId(key, int(hypervisor_system_id))
        xmlrpcserver.registration.virt_notify(systemid, plan)

    def unassociate_guest(self, instance_uuid, hypervisor_uuid):
        logger.info("spacewalk does not support removing guests from hypervisors, no action taken")
