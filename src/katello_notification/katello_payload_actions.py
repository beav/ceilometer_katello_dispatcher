import logging
from katello_notification.katello_wrapper import Katello

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class KatelloPayloadActions():
    """
    payload wrapper to handle foreman calls
    """

    def __init__(self):
        log.info("initializing payload actions")
        self.katello = Katello()

    def find_or_create_hypervisor(self, payload):
        hyp_host = payload.get('host')
        log.info("looking for hypervisor consumer record for for %s" % hyp_host)
        hyp_consumer_uuid = self.katello.find_hypervisor(hyp_host)
        if not hyp_consumer_uuid:
            log.error("no hypervisor found for %s" % hyp_host)
            #TODO: optionally create a hypervisor here, based on config param
            raise RuntimeError("no hypervisor found for %s" % hyp_host)
        return hyp_consumer_uuid

    def create_guest_mapping(self, payload, hypervisor_consumer_uuid):
        instance_id = payload.get('instance_id')
        log.debug("associating guest %s with hypervisor %s" % (instance_id, hypervisor_consumer_uuid))
        self.katello.associate_guest(instance_id, hypervisor_consumer_uuid)

    def delete_guest_mapping(self, payload, hypervisor_consumer_uuid):
        instance_id = payload.get('instance_id')
        log.info("removing guest %s from hypervisor %s" % (instance_id, hypervisor_consumer_uuid))
        self.katello.unassociate_guest(instance_id, hypervisor_consumer_uuid)
