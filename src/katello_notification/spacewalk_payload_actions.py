import logging
import xmlrpclib

from katello_notification.spacewalk_wrapper import Spacewalk

log = logging.getLogger(__name__)

#TODO: make configurable
logging.basicConfig(level=logging.DEBUG)


class SpacewalkPayloadActions():
    """
    payload wrapper to handle spacewalk calls
    """

    def __init__(self):
        log.info("initializing payload actions for spacewalk")
        self.spacewalk = Spacewalk()

    def find_or_create_hypervisor(self, payload):
        hyp_host = payload.get('host')
        # look up hypervisor in hypervisor hostname/systemid dict
        log.info("hypervisor system for %s not found locally, looking in spacewalk for record" % hyp_host)
        hyp_system_id = self.spacewalk.find_hypervisor(hyp_host)
        if not hyp_system_id:
            log.error("no hypervisor found for %s - perhaps it needs to be registered to spacewalk?" % hyp_host)
            raise RuntimeError("no hypervisor found for %s" % hyp_host)
        return hyp_system_id

    def create_guest_mapping(self, payload, hypervisor_consumer_uuid):
        instance_id = payload.get('instance_id')
        log.info("associating guest %s with hypervisor %s" % (instance_id, hypervisor_consumer_uuid))
        self.spacewalk.associate_guest(instance_id, hypervisor_consumer_uuid)

    def delete_guest_mapping(self, payload, hypervisor_consumer_uuid):
        instance_id = payload.get('instance_id')
        log.info("removing guest %s from hypervisor %s" % (instance_id, hypervisor_consumer_uuid))
        self.spacewalk.unassociate_guest(instance_id, hypervisor_consumer_uuid)