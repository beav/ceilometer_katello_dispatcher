# -*- encoding: utf-8 -*-
#
# Author: Chris Duryee <cduryee@redhat.com>
# based on file.py
#

import logging
import logging.handlers
from oslo.config import cfg
from ceilometer.collector import dispatcher
from ceilometer.openstack.common import log

from rhsm.connection import UEPConnection

LOG = log.getLogger(__name__)


katello_dispatcher_opts = [
    cfg.StrOpt('default_owner',
               default=None,
               help='owner to use when registering systems'),
    # this should be using oauth
    cfg.StrOpt('kt_username',
               default=None,
               help='katello login'),
    cfg.StrOpt('kt_pass',
               default=None,
               help='katello passwd'),
]

cfg.CONF.register_opts(katello_dispatcher_opts, group="dispatcher_katello")


class KatelloDispatcher(dispatcher.Base):
    '''
    Dispatcher class for recording metering data to katello.
    '''

    def __init__(self, conf):
        super(KatelloDispatcher, self).__init__(conf)

        self.cp = UEPConnection(username=self.conf.dispatcher_katello.kt_username,
                                password=self.conf.dispatcher_katello.kt_pass)

    def record_metering_data(self, context, data):
        # TODO: i'm not sure if its ok to send facts up, we always want the client's facts to win.
        for d in data:
            if d['counter_name'] == 'instance':
                if d['resource_metadata']['event_type'] == 'compute.instance.exists':
                    LOG.info("recording system checkin for %s" % d['resource_id'])
                elif d['resource_metadata']['event_type'] == 'compute.instance.delete.end':
                    self.cp.unregisterConsumer(d['resource_id'])
                    LOG.info("sent system deletion for %s" % d['resource_id'])
                elif d['resource_metadata']['event_type'] == 'compute.instance.create.end':
                    facts = {'system.name': d['resource_metadata']['display_name'],
                             'virt.host_type': 'kvm',
                             'virt.is_guest': True,
                             'virt.uuid': d['resource_id']}
                    self.cp.registerConsumer(d['resource_metadata']['display_name'], "system",
                                             owner=self.conf.dispatcher_katello.default_owner, uuid=d['resource_id'],
                                             installed_products=[{"productId": 601, "productName": 'OSP_guest_slot'}],
                                             facts = facts)
                    LOG.info("sent system creation for %s" % d['resource_id'])

    def record_events(self, context, data):
        # we only care about metering data right now
        return []
