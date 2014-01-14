# -*- encoding: utf-8 -*-
#
# Copyright © 2012-2013 eNovance <licensing@enovance.com>
#
# Author: Julien Danjou <julien@danjou.info>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo.config import cfg
from stevedore import extension

from ceilometer.event import converter as event_converter
from ceilometer.openstack.common import context
from ceilometer.openstack.common.gettextutils import _  # noqa
from ceilometer.openstack.common import log
from ceilometer.openstack.common.rpc import service as rpc_service
from ceilometer.openstack.common import service as os_service
from ceilometer import pipeline
from ceilometer import service
from ceilometer.storage import models
from ceilometer import transformer


LOG = log.getLogger(__name__)


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


class NotificationService(service.DispatchedService, rpc_service.Service):

    NOTIFICATION_NAMESPACE = 'katello.notification'

    def start(self):
        super(NotificationService, self).start()
        # Add a dummy thread to have wait() working
        self.tg.add_timer(604800, lambda: None)

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
            for topic in exchange_topic.topics:
                try:
                    self.conn.join_consumer_pool(
                        callback=self.process_notification,
                        pool_name=topic,
                        topic=topic,
                        exchange_name=exchange_topic.exchange,
                        ack_on_error=ack_on_error)
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
        LOG.info(_('notification %r'), notification.get('event_type'))
        if notification.get('event_type') == 'compute.instance.create.end':
            LOG.info("instance created! id is %s, host is %s" % (notification.get('payload').get('instance_id'), notification.get('payload').get('host')))
            # look up hypervisor in hypervisor hostname/uuid dict
            # look up instance in katello based on virt uuid



def agent():
    service.prepare_service()
    os_service.launch(NotificationService(
        cfg.CONF.host,
        'katello.agent.notification')).wait()

if __name__ == "__main__":
    agent()
