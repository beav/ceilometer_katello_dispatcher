# -*- encoding: utf-8 -*-
#
# Author: Chris Duryee <cduryee@redhat.com>
# based on file.py
#

import logging
import logging.handlers
from oslo.config import cfg
from ceilometer.collector import dispatcher

from rhsm.connection import UEPConnection

katello_dispatcher_opts = [
    cfg.StrOpt('log_file_path',
               default=None,
               help='Log file for katello dispatcher'),
    cfg.IntOpt('max_bytes',
               default=0,
               help='max bytes per logfile'),
    cfg.IntOpt('backup_count',
               default=0,
               help='number of backup logfiles'),
    cfg.StrOpt('default_owner',
               default=None,
               help='owner to use when registering systems'),
    # this should be using oauth
    cfg.StrOpt('katello_login',
               default=None,
               help='katello login'),
    cfg.StrOpt('katello_pw',
               default=None,
               help='katello passwd'),
]

cfg.CONF.register_opts(katello_dispatcher_opts, group="dispatcher_katello")


class KatelloDispatcher(dispatcher.Base):
    '''Dispatcher class for recording metering data to katello.

    to deploy:
     add "katello = ceilometer_katello_dispatcher.katello:KatelloDispatcher" to /usr/lib/python2.6/site-packages/ceilometer-2013.2-py2.6.egg-info/entry_points.txt

    example entries in ceilometer.conf:

    [dispatcher_katello]
    log_file_path = /var/log/ceilometer/katello.log
    default_owner = ACME_Corporation

    To enable this dispatcher, the following section needs to be present in
    ceilometer.conf file

    [collector]
    dispatchers = katello 
    '''

    def __init__(self, conf):
        super(KatelloDispatcher, self).__init__(conf)

        self.cp = UEPConnection(username="admin", password="admin", insecure=True)

        self.log = None

        # if the directory and path are configured, then log to the file
        if self.conf.dispatcher_katello.log_file_path:
            dispatcher_logger = logging.Logger('dispatcher.katello')
            dispatcher_logger.setLevel(logging.INFO)
            # create rotating file handler which logs meters
            rfh = logging.handlers.RotatingFileHandler(
                self.conf.dispatcher_katello.log_file_path,
                maxBytes=self.conf.dispatcher_katello.max_bytes,
                backupCount=self.conf.dispatcher_katello.backup_count,
                encoding='utf8')

            rfh.setLevel(logging.INFO)
            # Only wanted the meters to be saved in the file, not the
            # project root logger.
            dispatcher_logger.propagate = False
            dispatcher_logger.addHandler(rfh)
            self.log = dispatcher_logger

    def record_metering_data(self, context, data):
        # TODO: i'm not sure if its ok to send facts up, we always want the client's facts to win.
        if not self.log:
            return
        for d in data:
            if d['counter_name'] == 'instance':
                if d['resource_metadata']['event_type'] == 'compute.instance.exists':
                    self.log.info("system checkin for %s" % d['resource_id'])
                elif d['resource_metadata']['event_type'] == 'compute.instance.delete.end':
                    self.cp.unregisterConsumer(d['resource_id'])
                    self.log.info("system deletion for %s" % d['resource_id'])
                elif d['resource_metadata']['event_type'] == 'compute.instance.create.end':
                    facts = {'system.name': d['resource_metadata']['display_name'],
                             'virt.host_type': 'kvm',
                             'virt.is_guest': True,
                             'virt.uuid': d['resource_id']}
                    self.cp.registerConsumer(d['resource_metadata']['display_name'], "system",
                                             owner="ACME_Corporation", uuid=d['resource_id'],
                                             installed_products=[{"productId": 601, "productName": 'OSP_guest_slot'}],
                                             facts = facts)
                    self.log.info("system created for %s" % d['resource_id'])
                    self.log.info("facts: %s" % facts)
                self.log.info(d)
            else:
                self.log.info("not instance: %s" % d['counter_name'])


    def record_events(self, events):
        if self.log:
            self.log.info(events)
        return []
