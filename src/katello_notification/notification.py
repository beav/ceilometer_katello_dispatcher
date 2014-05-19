#!/usr/bin/python
from oslo.config import cfg
from oslo import messaging
from ConfigParser import SafeConfigParser

from katello_notification.katello_payload_actions import KatelloPayloadActions
from katello_notification.spacewalk_payload_actions import SpacewalkPayloadActions

import logging

logger = logging.getLogger('katello_notification')

LOG_LOCATION = "/var/log/katello_notification/katello_notification.log"
CONFIG_FILENAME = "/etc/katello/katello-notification.conf"


class NotificationEndpoint(object):

    def __init__(self, payload_actions):
        self.payload_actions = payload_actions

    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        """
        endpoint for notification messages

        When another service sends a notification over the message
        bus, this method receives it. See _setup_subscription().

        """
        # we only care about creates, deletes, and migrates
        try:
            # handle exists events
            if event_type == 'compute.instance.exists':
                if payload['state'] == 'deleted':
                    logger.debug("received instance.exists deletion event")
                    hypervisor_id = self.payload_actions.find_or_create_hypervisor(payload)
                    self.payload_actions.delete_guest_mapping(payload, hypervisor_id)
                else:
                    logger.debug("received instance.exists event")
                    hypervisor_id = self.payload_actions.find_or_create_hypervisor(payload)
                    self.payload_actions.create_guest_mapping(payload, hypervisor_id)
            # handle creates and deletes
            elif event_type == 'compute.instance.create.end':
                logger.debug("received instance.create.end event")
                hypervisor_id = self.payload_actions.find_or_create_hypervisor(payload)
                self.payload_actions.create_guest_mapping(payload, hypervisor_id)
            elif event_type == 'compute.instance.delete.end':
                logger.debug("received instance.delete.end event")
                hypervisor_id = self.payload_actions.find_or_create_hypervisor(payload)
                self.payload_actions.delete_guest_mapping(payload, hypervisor_id)
        except Exception, e:
            logger.exception(e)


class KatelloMain():
    def _katello_or_spacewalk(self):
        conf = SafeConfigParser()
        conf.readfp(open(CONFIG_FILENAME))
        return conf.get('main', 'mgmt_server')

    def _get_loglevel(self):
        conf = SafeConfigParser()
        conf.readfp(open(CONFIG_FILENAME))
        return conf.get('main', 'loglevel')

    def _get_amqp_url(self):
        conf = SafeConfigParser()
        conf.readfp(open(CONFIG_FILENAME))
        return conf.get('main', 'amqp_url')

    def main(self):

        # TODO: clean up and make more configurable!
        logger = logging.getLogger('katello_notification')
        logger.setLevel(self._get_loglevel())
        handler = logging.FileHandler(LOG_LOCATION)
        formatter = logging.Formatter('%(asctime)s - %(name)s - @%(filename)s %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # quick config check
        mgmt_server = self._katello_or_spacewalk()

        if mgmt_server == 'katello':
            payload_actions = KatelloPayloadActions()
        elif mgmt_server == 'spacewalk':
            payload_actions = SpacewalkPayloadActions()
        else:
            logger.error("mgmt server not set to 'katello' or 'spacewalk', aborting")

        # set up transport and listener
        transport = messaging.get_transport(cfg.CONF, url=self._get_amqp_url())

        targets = [
            messaging.Target(topic='subscription_notifications', exchange='nova'),
        ]
        endpoints = [
            NotificationEndpoint(payload_actions),
        ]
        server = messaging.get_notification_listener(transport, targets, endpoints)
        logger.info("listener initialized")
        server.start()
        server.wait()

if __name__ == "__main__":
    km = KatelloMain()
    km.main()
