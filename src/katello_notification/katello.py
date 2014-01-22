from katello.client.api.system import SystemAPI
from katello.client import server
from katello.client.server import BasicAuthentication

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class Katello():
    def __init__(self):
        self.systemapi = SystemAPI()
        s = server.KatelloServer("10.16.79.132", "443", "https", "/sam")
        s.set_auth_method(BasicAuthentication('admin', 'admin'))
        server.set_active_server(s)

    def find_hypervisor(self, hypervisor_hostname)
        systems = system_api.systems_by_org(org_name, {'network.hostname': hypervisor_hostname})

        if len(systems) > 1:
            log.error("found too many systems for %s, name is ambiguous" % hypervisor_hostname)
            return
        if len(systems) == 0:
            log.error("found zero systems for %s" % hypervisor_hostname)
            return
            
        return systems[0]['uuid']

