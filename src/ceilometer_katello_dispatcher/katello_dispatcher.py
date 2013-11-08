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

from katello.client import server
from katello.client.api.system import SystemAPI
from katello.client.server import BasicAuthentication


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
    cfg.StrOpt('hostname',
               default=None,
               help='katello hostname'),
    cfg.StrOpt('port',
               default=None,
               help='katello port'),
    cfg.StrOpt('proto',
               default=None,
               help='katello proto (http or https)'),
    cfg.StrOpt('api_url',
               default=None,
               help='katello api url'),
]

cfg.CONF.register_opts(katello_dispatcher_opts, group="dispatcher_katello")


class KatelloDispatcher(dispatcher.Base):
    '''
    Dispatcher class for recording metering data to katello.
    '''

    def __init__(self, conf):
        super(KatelloDispatcher, self).__init__(conf)
        self.systemapi = SystemAPI()
        self.kt = server.KatelloServer(host=self.conf.dispatcher_katello.hostname,
                                       port=self.conf.dispatcher_katello.port,
                                       path_prefix=self.conf.dispatcher_katello.api_url)
        self.kt.set_auth_method(BasicAuthentication(self.conf.dispatcher_katello.kt_username, self.conf.dispatcher_katello.kt_pass))
        server.set_active_server(self.kt)

    def record_metering_data(self, context, data):
        # TODO: i'm not sure if its ok to send facts up, we always want the client's facts to win.
        for d in data:
            if d['counter_name'] == 'instance':
                if d['resource_metadata']['event_type'] == 'compute.instance.delete.end':
                    self.systemapi.unregister(d['resource_id'])
                    LOG.info("sent system deletion for %s" % d['resource_id'])

                elif d['resource_metadata']['event_type'] == 'compute.instance.create.end':
                    facts = {'system.name': d['resource_metadata']['display_name'],
                             'virt.host_type': 'kvm',
                             'virt.is_guest': True,
                             'virt.uuid': d['resource_id']}
                    #installed_products=[{"productId": 999, "productName": 'example_product'}],
                    self.systemapi.register(name=d['resource_metadata']['display_name'],
                                            org=self.conf.dispatcher_katello.default_owner, environment_id=None,
                                            facts=facts, activation_keys=None, cp_type='system', installed_products=None,
                                            last_checkin=None, uuid=d['resource_id'])
                    LOG.info("sent system creation for %s" % d['resource_id'])

    def record_events(self, context, data):
        # we only care about metering data right now
        return []
