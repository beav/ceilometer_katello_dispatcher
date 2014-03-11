
from ConfigParser import SafeConfigParser
import xmlrpclib

import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class Spacewalk():
    def __init__(self):
        self._load_config()
        server = 'https://' + self.sw_host + ':' + self.sw_port
        log.debug("Initializing spacewalk connection to %s" % server)
        try:
            self.rpcserver = xmlrpclib.Server(server + '/rpc/api', verbose=0)
            self.xmlrpcserver = xmlrpclib.Server(server + '/XMLRPC', verbose=0)
        except Exception:
            raise SpacewalkError("Unable to connect to the spacewalk server")
            log.error("unable to connect to spacewalk server")
        self.key = self.rpcserver.auth.login('admin', 'nimda')
        log.info("Initialized spacewalk connection")

    def _load_config(self):
        CONF = '/etc/katello/katello-notification.conf'
        conf = SafeConfigParser()
        conf.readfp(open(CONF))
        self.sw_host = conf.get('spacewalk', 'host')
        self.sw_port = conf.get('spacewalk', 'port')
        self.sw_username = conf.get('spacewalk', 'username')
        self.sw_password = conf.get('spacewalk', 'password')

    def find_hypervisor(self, hypervisor_hostname):
        """
        returns a system ID based on hostname, returns None if no hypervisor is found
        """
        result = self.rpcserver.system.search.hostname(self.key, hypervisor_hostname)
        log.info(result)
        if len(result) > 1:
            raise RuntimeError("more than one system record found for hostname %s" % hypervisor_hostname)
        if len(result) == 1:
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
        guest_list = self.rpcserver.system.listVirtualGuests(self.key, sid)
        # strip the list to just the UUIDs
        uuids = map(lambda x: x['uuid'], guest_list)
        log.debug("guest list for %s: %s" % (sid, uuids))
        return uuids

    def associate_guest(self, instance_uuid, hypervisor_system_id):
        """
        important note: spacewalk does not ever delete guest records, see
        https://git.fedorahosted.org/cgit/spacewalk.git/tree/backend/server/rhnVirtualization.py#n263

        We can take advantage of this to avoid a race condition, since two
        concurrent runs of associate_guest will not clobber each other's plan. At worst,
        the "losing" guest list will have one item marked as "stopped" incorrectly.

        """

        guest_list = self._get_guest_uuid_list(hypervisor_system_id)
        guest_list.append(instance_uuid)
        #TODO: look up hypervisor info here to make plan more detailed?
        plan = self._assemble_plan(guest_list, hypervisor_system_id)
        log.debug("sending plan %s" % plan)
        systemid = self.rpcserver.system.downloadSystemId(self.key, hypervisor_system_id)
        self.xmlrpcserver.registration.virt_notify(systemid, plan)

    def unassociate_guest(self, instance_uuid, hypervisor_uuid):
        log.info("spacewalk does not support removing guests from hypervisors, no action taken")
