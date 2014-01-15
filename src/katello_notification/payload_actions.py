import logging
from katello_notification.consumer_map import ConsumerMap

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class PayloadActions():
    """
    payload wrapper to handle foreman calls
    """

    def __init__(self):
        log.info("initializing payload actions")
        self.consumer_map = ConsumerMap("/tmp/hyp.json")

    def find_or_create_hypervisor(self, payload):
        hyp_host = payload.get('host')
        # look up hypervisor in hypervisor hostname/uuid dict
        try:
            hyp_consumer_uuid = self.consumer_map.find_hypervisor_consumer_uuid(local_identifier=hyp_host)
            log.info("hypervisor consumer %s found, uuid is %s" % (hyp_host, hyp_consumer_uuid))
        except KeyError:
            log.info("hypervisor consumer for %s not found, creating new consumer record" % hyp_host)
            # call foreman to get create hypervisor record
            #TODO: remove hack
            hyp_consumer_uuid = "a532de5a-7dfa-11e3-94dc-d81928d43830"
            self.consumer_map.add_hypervisor_consumer_uuid(local_identifier=hyp_host, hyp_uuid = hyp_consumer_uuid)
            log.info("saved uuid %s for hypervisor %s" % (hyp_consumer_uuid, hyp_host))

        return hyp_consumer_uuid
