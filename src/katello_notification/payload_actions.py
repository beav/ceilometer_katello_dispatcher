import logging
from katello_notification.consumer_map import ConsumerMap
from katello_notification.katello import Katello

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
            uuid = self.katello.find_hypervisor(hyp_host)

            # call foreman to get hypervisor record by hostname
            log.info("hypervisor consumer for %s not found, creating new consumer record" % hyp_host)
            #TODO: remove hack
            hyp_consumer_uuid = "a532de5a-7dfa-11e3-94dc-d81928d43830"
            self.consumer_map.add_hypervisor_consumer_uuid(local_identifier=hyp_host, hyp_uuid = hyp_consumer_uuid)
            log.info("saved uuid %s for hypervisor %s" % (hyp_consumer_uuid, hyp_host))

        return hyp_consumer_uuid

    def create_guest_mapping(self, payload, hypervisor_consumer_uuid):
        instance_id = payload.get('instance_id')
        log.info("associating guest %s with hypervisor %s" % (instance_id, hypervisor_consumer_uuid))

    # not used
    def update_guest(self, payload):
        instance_id = payload.get('instance_id')
        log.info("updating %s with latest checkin" % (instance_id))

    def delete_guest(self, payload):
        instance_id = payload.get('instance_id')
        log.info("removing %s" % (instance_id))
