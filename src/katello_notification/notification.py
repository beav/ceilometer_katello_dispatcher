#!/usr/bin/python
from oslo.config import cfg
from stevedore import extension
from ConfigParser import SafeConfigParser

from ceilometer.openstack.common.gettextutils import _  # noqa
from ceilometer.openstack.common.rpc import service as rpc_service
from ceilometer.openstack.common import service as os_service
from ceilometer import service

from katello_notification.katello_payload_actions import KatelloPayloadActions
from katello_notification.spacewalk_payload_actions import SpacewalkPayloadActions
import logging

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

OPTS = [
    cfg.BoolOpt('ack_on_event_error',
                default=True,
                deprecated_group='collector',
                help='Acknowledge message when event persistence fails'),
    cfg.BoolOpt('store_events',
                deprecated_group='collector',
                default=False,
                help='Save event details'),
]

cfg.CONF.register_opts(OPTS, group="notification")


class UnableToSaveEventException(Exception):
    """Thrown when we want to requeue an event.

    Any exception is fine, but this one should make debugging
    a little easier.
    """


class KatelloNotificationService(service.DispatchedService, rpc_service.Service):

    NOTIFICATION_NAMESPACE = 'katello.notification'
    # this needs to be set, otherwise events will be stolen from ceilometer
    TOPIC_OVERRIDE = 'subscription_notifications.info'

    def _katello_or_spacewalk(self):
        CONFIG_FILENAME = '/etc/katello/katello-notification.conf'
        conf = SafeConfigParser()
        conf.readfp(open(CONFIG_FILENAME))
        return conf.get('main', 'mgmt_server')

    def start(self):
        super(KatelloNotificationService, self).start()
        # Add a dummy thread to have wait() working
        self.tg.add_timer(604800, lambda: None)
        mgmt_server = self._katello_or_spacewalk()

        if mgmt_server == 'katello':
            self.payload_actions = KatelloPayloadActions()
        elif mgmt_server == 'spacewalk':
            self.payload_actions = SpacewalkPayloadActions()
        else:
            log.error("mgmt server not set to 'katello' or 'spacewalk', aborting")

    def initialize_service_hook(self, service):
        '''Consumers must be declared before consume_thread start.'''
        self.notification_manager = \
            extension.ExtensionManager(
                namespace=self.NOTIFICATION_NAMESPACE,
                invoke_on_load=True,
            )

        if not list(self.notification_manager):
            LOG.warning(_('Failed to load any notification handlers for %s'),
                        self.NOTIFICATION_NAMESPACE)
        self.notification_manager.map(self._setup_subscription)

    def _setup_subscription(self, ext, *args, **kwds):
        """Connect to message bus to get notifications

        Configure the RPC connection to listen for messages on the
        right exchanges and topics so we receive all of the
        notifications.

        Use a connection pool so that multiple notification agent instances
        can run in parallel to share load and without competing with each
        other for incoming messages.

        """
        handler = ext.obj
        ack_on_error = cfg.CONF.notification.ack_on_event_error
        LOG.info(_('Event types from %(name)s: %(type)s'
                    ' (ack_on_error=%(error)s)') %
                  {'name': ext.name,
                   'type': ', '.join(handler.event_types),
                   'error': ack_on_error})

        for exchange_topic in handler.get_exchange_topics(cfg.CONF):
            LOG.info("exchange: %s" % exchange_topic.exchange)
            for topic in exchange_topic.topics:
                topic = self.TOPIC_OVERRIDE
                LOG.info("joining consumer pool for %r" % topic)
                try:
                    self.conn.join_consumer_pool(
                        callback=self.process_notification,
                        pool_name=topic,
                        topic=topic,
                        exchange_name=exchange_topic.exchange,
                        ack_on_error=ack_on_error)
                    LOG.info("joined consumer pool for %r" % topic)
                except Exception:
                    LOG.exception(_('Could not join consumer pool'
                                    ' %(topic)s/%(exchange)s') %
                                  {'topic': topic,
                                   'exchange': exchange_topic.exchange})

    def process_notification(self, notification):
        """RPC endpoint for notification messages

        When another service sends a notification over the message
        bus, this method receives it. See _setup_subscription().

        """
        # we only care about creates, deletes, and migrates
        # note: this will get cleaned up a bit when we move to oslo.messaging libs
        try:

            # handle exists events
            if notification.get('event_type') == 'compute.instance.exists':
                if notification.get('payload')['state'] == 'deleted':
                    LOG.debug("received instance.exists deletion event")
                    hypervisor_id = self.payload_actions.find_or_create_hypervisor(notification.get('payload'))
                    self.payload_actions.delete_guest_mapping(notification.get('payload'), hypervisor_id)
                else:
                    LOG.debug("received instance.exists event")
                    hypervisor_id = self.payload_actions.find_or_create_hypervisor(notification.get('payload'))
                    self.payload_actions.create_guest_mapping(notification.get('payload'), hypervisor_id)
            # handle creates and deletes
            elif notification.get('event_type') == 'compute.instance.create.end':
                LOG.debug("received instance.create.end event")
                hypervisor_id = self.payload_actions.find_or_create_hypervisor(notification.get('payload'))
                self.payload_actions.create_guest_mapping(notification.get('payload'), hypervisor_id)
            elif notification.get('event_type') == 'compute.instance.delete.end':
                LOG.debug("received instance.delete.end event")
                hypervisor_id = self.payload_actions.find_or_create_hypervisor(notification.get('payload'))
                self.payload_actions.delete_guest_mapping(notification.get('payload'), hypervisor_id)
        except Exception, e:
            LOG.exception(e)


def agent():
    service.prepare_service()
    os_service.launch(KatelloNotificationService(
        cfg.CONF.host, 'katello.agent.notification')).wait()

if __name__ == "__main__":
    agent()
