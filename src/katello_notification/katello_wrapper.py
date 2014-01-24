from katello.client.api.system import SystemAPI
from katello.client import server
from katello.client.server import BasicAuthentication
import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class Katello():
    def __init__(self):
        self.systemapi = SystemAPI()
        s = server.KatelloServer("10.3.11.129", "443", "https", "/sam")
        s.set_auth_method(BasicAuthentication('admin', 'admin'))
        server.set_active_server(s)

    def find_hypervisor(self, hypervisor_hostname):
        systems = self.systemapi.systems_by_org('ACME_Corporation', {'network.hostname': hypervisor_hostname})

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
            log.error("attempted to remove guest %s from list that does not contain entry" % instance_uuid)
            return

        log.info("sending guest list: %s" % params['guestIds'])
        self.systemapi.update(hypervisor_uuid, params)
