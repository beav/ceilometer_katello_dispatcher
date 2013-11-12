# -*- coding: utf-8 -*-
#
# Copyright © 2014 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

from mock import MagicMock, patch
from oslo.config import cfg
from ceilometer_katello_dispatcher import katello_dispatcher


class TestKatelloDispatcher():

    def setUp(self):
        self.dispatcher = katello_dispatcher.KatelloDispatcher(cfg.CONF)
        self.ctx = None

    @patch('katello.client.api.system.SystemAPI.register')
    def test_create(self, mock_register):
        self.dispatcher.record_metering_data(self.ctx, create_event)
        mock_register.assert_called_once_with(environment_id=None,
                                              uuid='a3ab1013-1b74-48df-9afd-89d7ea777dfc',
                                              installed_products=None,
                                              last_checkin=None,
                                              facts={'system.name': 'test2', 'virt.host_type': 'kvm',
                                                     'virt.is_guest': True,
                                                     'virt.uuid': 'a3ab1013-1b74-48df-9afd-89d7ea777dfc'},
                                              activation_keys=None, org=None, cp_type='system', name='test2')

    @patch('katello.client.api.system.SystemAPI.unregister')
    def test_terminate(self, mock_unregisterConsumer):
        self.dispatcher.record_metering_data(self.ctx, terminate_event)
        mock_unregisterConsumer.assert_called_once_with('bb52add2-9bbe-42d6-84e8-bfc7977049ef')

    def test_no_event_type(self):
        self.dispatcher.record_metering_data(self.ctx, no_event_type_event)

    def test_record_events(self):
        # test that nothing is returned
        assert not self.dispatcher.record_events(self.ctx, None)

# Events go here. Just copy 'em from collector.log for testing.
create_event = \
    [{'counter_name': 'instance',
      'user_id': 'a487ab66bd994cf5aa0c749caef13e27',
      'resource_id': 'a3ab1013-1b74-48df-9afd-89d7ea777dfc',
      'timestamp': '2013-11-07 03:00:35.697700',
      'message_signature': 'd478b52e1229e4755172fd78908c0c5713ab529e3b7762e10e8f028cd1d76c3c',
      'resource_metadata':
        {'state_description': '',
         'event_type': 'compute.instance.create.end',
         'availability_zone': 'nova',
         'terminated_at': '',
         'ephemeral_gb': 0,
         'instance_type_id': 6,
         'message': 'Success',
         'deleted_at': '',
         'fixed_ips':
            [{'floating_ips': [],
              'label': 'novanetwork',
              'version': 4,
              'meta': {},
              'address': '192.168.32.3',
              'type': 'fixed'}],
              'instance_id': 'a3ab1013-1b74-48df-9afd-89d7ea777dfc',
              'user_id': 'a487ab66bd994cf5aa0c749caef13e27',
              'reservation_id': 'r-jt4tlhsk',
              'hostname': 'test2',
              'state': 'active',
              'launched_at': '2013-11-07T03:00:35.166557',
              'metadata': [],
              'node': 'rdo',
              'ramdisk_id': '',
              'access_ip_v6': None,
              'disk_gb': 1,
              'access_ip_v4': None,
              'kernel_id': '',
              'image_name': 'cirros',
              'host': 'compute.rdo',
              'display_name': 'test2',
              'image_ref_url': 'http://192.168.122.43:9292/images/ec878d2d-202f-4910-810f-88d53fa524c3',
              'root_gb': 1,
              'tenant_id': '38a314df0985484684d536bb787610f1',
              'created_at': '2013-11-07T02:59:57.000000',
              'memory_mb': 256,
              'instance_type': 'mini',
              'vcpus': 1,
              'image_meta':{
                'min_disk': '1',
                'container_format': 'bare',
                'min_ram': '0',
                'disk_format': 'qcow2',
                'base_image_ref': 'ec878d2d-202f-4910-810f-88d53fa524c3'},
              'architecture': None,
              'os_type': None,
              'instance_flavor_id': '98c52d65-9780-40de-bc4e-c542955a4b61'},
    'source': 'openstack',
    'counter_unit': 'instance',
    'counter_volume': 1,
    'project_id': '38a314df0985484684d536bb787610f1',
    'message_id': 'c620a80a-4758-11e3-a2e9-525400770cf5',
    'counter_type': 'gauge'}]

terminate_event = \
[{u'counter_name': u'instance',
  u'user_id': u'a487ab66bd994cf5aa0c749caef13e27',
  u'resource_id': u'bb52add2-9bbe-42d6-84e8-bfc7977049ef',
  u'timestamp': u'2013-11-07 19:27:11.756999',
  u'message_signature': u'259dad84e7c37ebfe23e410eb9ab6ec0c6d44e61a431dcd8fe5c8ed0c87babcb',
  u'resource_metadata':
      {u'state_description': u'',
       u'event_type': u'compute.instance.delete.end',
       u'availability_zone': u'nova',
       u'terminated_at': u'2013-11-07T19:27:10.531295',
       u'ephemeral_gb': 0,
       u'instance_type_id': 6,
       u'deleted_at': u'',
       u'reservation_id': u'r-1zs4v113',
       u'instance_id': u'bb52add2-9bbe-42d6-84e8-bfc7977049ef',
       u'user_id': u'a487ab66bd994cf5aa0c749caef13e27',
       u'hostname': u'foo',
       u'state': u'deleted',
       u'launched_at': u'2013-11-07T19:26:30.000000',
       u'metadata': {},
       u'node': u'rdo',
       u'ramdisk_id': u'',
       u'access_ip_v6': None,
       u'disk_gb': 1,
       u'access_ip_v4': None,
       u'kernel_id': u'',
       u'host': u'compute.rdo',
       u'display_name': u'foo',
       u'image_ref_url': u'http://192.168.122.43:9292/images/ec878d2d-202f-4910-810f-88d53fa524c3',
       u'root_gb': 1,
       u'tenant_id': u'38a314df0985484684d536bb787610f1',
       u'created_at': u'2013-11-07 19:25:42+00:00',
       u'memory_mb': 256,
       u'instance_type': u'mini',
       u'vcpus': 1,
       u'image_meta':
         {u'min_disk': u'1',
         u'container_format': u'bare',
         u'min_ram': u'0',
         u'disk_format': u'qcow2',
         u'base_image_ref': u'ec878d2d-202f-4910-810f-88d53fa524c3'},
       u'architecture': None,
       u'os_type': None,
       u'instance_flavor_id': u'98c52d65-9780-40de-bc4e-c542955a4b61'},
     u'source': u'openstack',
     u'counter_unit': u'instance',
     u'counter_volume': 1,
     u'project_id': u'38a314df0985484684d536bb787610f1',
     u'message_id': u'99b419fc-47e2-11e3-a2e9-525400770cf5',
     u'counter_type': u'gauge'}]

# I haven't found one of these yet, I created this based on the error in collector.log
no_event_type_event =  \
[{u'counter_name': u'instance',
  u'user_id': u'a487ab66bd994cf5aa0c749caef13e27',
  u'resource_id': u'bb52add2-9bbe-42d6-84e8-bfc7977049ef',
  u'timestamp': u'2013-11-07 19:27:11.756999',
  u'message_signature': u'259dad84e7c37ebfe23e410eb9ab6ec0c6d44e61a431dcd8fe5c8ed0c87babcb',
  u'resource_metadata':
      {u'state_description': u'',
       u'availability_zone': u'nova',
       u'terminated_at': u'2013-11-07T19:27:10.531295'}
}]
