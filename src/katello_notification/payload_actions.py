import logging
from katello_notification.consumer_map import ConsumerMap
from katello_notification.katello_wrapper import Katello

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class PayloadActions():
    """
    payload wrapper to handle foreman calls
    """

    def __init__(self):
        log.info("initializing payload actions")
        self.consumer_map = ConsumerMap("/tmp/hyp.json")
        self.katello = Katello()

    def find_or_create_hypervisor(self, payload):
        hyp_host = payload.get('host')
        # look up hypervisor in hypervisor hostname/uuid dict
        try:
            hyp_consumer_uuid = self.consumer_map.find_hypervisor_consumer_uuid(local_identifier=hyp_host)
            log.info("hypervisor consumer %s found, uuid is %s" % (hyp_host, hyp_consumer_uuid))
        except KeyError:
            log.info("hypervisor consumer for %s not found locally, looking for record" % hyp_host)
            hyp_consumer_uuid = self.katello.find_hypervisor(hyp_host)
            if not hyp_consumer_uuid:
                log.error("no hypervisor found for %s" % hyp_host)
                raise RuntimeError("no hypervisor found for %s" % hyp_host)
            self.consumer_map.add_hypervisor_consumer_uuid(local_identifier=hyp_host, hyp_uuid=hyp_consumer_uuid)
            log.info("saved uuid %s for hypervisor %s" % (hyp_consumer_uuid, hyp_host))
        return hyp_consumer_uuid

    def create_guest_mapping(self, payload, hypervisor_consumer_uuid):
        instance_id = payload.get('instance_id')
        log.info("associating guest %s with hypervisor %s" % (instance_id, hypervisor_consumer_uuid))
        self.katello.associate_guest(instance_id, hypervisor_consumer_uuid)

    def delete_guest_mapping(self, payload, hypervisor_consumer_uuid):
        instance_id = payload.get('instance_id')
        log.info("removing guest %s from hypervisor %s" % (instance_id, hypervisor_consumer_uuid))
        self.katello.unassociate_guest(instance_id, hypervisor_consumer_uuid)
