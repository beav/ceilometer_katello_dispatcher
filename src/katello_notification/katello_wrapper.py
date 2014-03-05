from katello.client.api.system import SystemAPI
from katello.client import server
from katello.client.server import BasicAuthentication
from ConfigParser import SafeConfigParser

import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class Katello():
    def __init__(self):
        self.systemapi = SystemAPI()
        self._load_config()
        log.info("connecting to %s://%s:%s%s" % (self.kt_scheme, self.kt_host, self.kt_port, self.kt_path))
        s = server.KatelloServer(self.kt_host, self.kt_port, self.kt_scheme, self.kt_path)
        s.set_auth_method(BasicAuthentication(self.kt_username, self.kt_password))
        server.set_active_server(s)

    def _load_config(self):
        CONFIG_FILENAME = '/etc/katello/katello-notification.conf'
        conf = SafeConfigParser()
        conf.readfp(open(CONFIG_FILENAME))
        self.kt_host = conf.get('katello', 'host')
        self.kt_port = conf.get('katello', 'port')
        self.kt_scheme = conf.get('katello', 'scheme')
        self.kt_path = conf.get('katello', 'path')
        self.kt_org = conf.get('katello', 'default_org')
        # this will be oauth in later versions of katello
        self.kt_username = conf.get('katello', 'username')
        self.kt_password = conf.get('katello', 'password')

    def find_hypervisor(self, hypervisor_hostname):
        # TODO: use owner/{owner}/hypervisors, passing in hypervisor_id (aka hostname)
        #   if no hypervisor, search by hostname
        #   if no record, then optionally create a hypervisor type consumer and add hypervisor_id
        systems = self.systemapi.systems_by_org(self.kt_org, {'search': "network.hostname:%s" % hypervisor_hostname})

        if len(systems) > 1:
            log.error("found too many systems for %s, name is ambiguous" % hypervisor_hostname)
            return
        if len(systems) == 0:
            log.error("found zero systems for %s" % hypervisor_hostname)
            return

        log.info("found %s for hostname %s!" % (systems[0]['uuid'], hypervisor_hostname))
        return systems[0]['uuid']

    def associate_guest(self, instance_uuid, hypervisor_uuid):
        """
        NB: instance uuid is a system uuid, hypervisor uuid is a consumer uuid

        this method has a race condition, since it grabs the guest list, then sends an updated version.
        """

        log.info("finding system record for %s" % hypervisor_uuid)
        system = self.systemapi.system(hypervisor_uuid)
        log.info("existing guest list: %s" % system['guestIds'])

        # the data that "update" expects is different than what is pulled down
        params = {}
        params['name'] = system['name']

        raw_guestlist = system['guestIds']
        guests = []

        for rg in raw_guestlist:
            guests.append(rg['guestId'])

        if guests and instance_uuid not in guests:
            guests.append(instance_uuid)
            params['guestIds'] = guests
        elif guests and instance_uuid in guests:
            # guest is already associated, no-op (this can happen from instance.exists messages)
            log.debug("guest %s is already associated with hypervisor %s" % (instance_uuid, hypervisor_uuid))
            return
        elif not guests:
            params['guestIds'] = [instance_uuid]

        log.info("sending guest list: %s" % params['guestIds'])
        self.systemapi.update(hypervisor_uuid, params)

    def unassociate_guest(self, instance_uuid, hypervisor_uuid):
        log.info("finding system record for %s" % hypervisor_uuid)
        system = self.systemapi.system(hypervisor_uuid)
        log.info("existing guest list: %s" % system['guestIds'])

        # the data that "update" expects is different than what is pulled down
        params = {}
        params['name'] = system['name']

        raw_guestlist = system['guestIds']
        guests = []

        for rg in raw_guestlist:
            guests.append(rg['guestId'])

        if guests and instance_uuid in guests:
            guests.remove(instance_uuid)
            params['guestIds'] = guests
        else:
            log.debug("attempted to remove already-removed guest %s from hypervisor %s" % (instance_uuid, hypervisor_uuid))
            return

        log.info("sending guest list: %s" % params['guestIds'])
        self.systemapi.update(hypervisor_uuid, params)
