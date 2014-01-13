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
from katello_notification.consumer_map import ConsumerMap
import unittest
from tempfile import NamedTemporaryFile


class TestConsumerMap(unittest.TestCase):

    def setUp(self):
        self.temp_json = NamedTemporaryFile(delete=False)
        self.consumer_map = ConsumerMap(self.temp_json.name)


    def test_no_hypervisor_found(self):
        self.consumer_map = ConsumerMap('/unused/path/name')
        with self.assertRaises(KeyError):
            self.consumer_map.find_hypervisor_consumer_uuid(local_identifier="some_hostname")


    @patch('katello_notification.consumer_map.ConsumerMap._load_consumer_map')
    def test_hypervisor_found(self, mock_load_map):
        mock_load_map.return_value = {'some_hostname': 'a575563c-7c8c-11e3-b6bd-40d7db0f677b'}
        self.consumer_map = ConsumerMap('/unused/path/name')
        self.assertEquals(self.consumer_map.find_hypervisor_consumer_uuid(local_identifier="some_hostname"), 'a575563c-7c8c-11e3-b6bd-40d7db0f677b')

    @patch('katello_notification.consumer_map.ConsumerMap._save_consumer_map')
    @patch('katello_notification.consumer_map.ConsumerMap._load_consumer_map')
    def test_remove_hypervisor(self, mock_load_map, mock_save_map):
        mock_load_map.return_value = {'some_hostname': 'a575563c-7c8c-11e3-b6bd-40d7db0f677b'}
        self.consumer_map = ConsumerMap('/unused/path/name')
        self.consumer_map.remove_hypervisor_consumer_uuid(local_identifier="some_hostname")
        mock_save_map.assert_called_once_with(data={}, fname='/unused/path/name')


    @patch('katello_notification.consumer_map.ConsumerMap._save_consumer_map')
    @patch('katello_notification.consumer_map.ConsumerMap._load_consumer_map')
    def test_add_hypervisor(self, mock_load_map, mock_save_map):
        # confirm that we overwrite the existing uuid
        mock_load_map.return_value = {'some_hostname': 'a575563c-7c8c-11e3-b6bd-40d7db0f677b'}
        self.consumer_map = ConsumerMap('/unused/path/name')
        self.consumer_map.add_hypervisor_consumer_uuid(local_identifier="some_hostname", hyp_uuid='9eddc386-7c91-11e3-99b6-40d7db0f677b')
        mock_save_map.assert_called_once_with(data={'some_hostname': '9eddc386-7c91-11e3-99b6-40d7db0f677b'}, fname='/unused/path/name')

        # confirm that we add a value now
        self.consumer_map.add_hypervisor_consumer_uuid(local_identifier="some_hostname_two", hyp_uuid='3d07466c-7c9d-11e3-bba9-40d7db0f677b')
        mock_save_map.assert_called_with(data={'some_hostname': '9eddc386-7c91-11e3-99b6-40d7db0f677b',
                                               'some_hostname_two': '3d07466c-7c9d-11e3-bba9-40d7db0f677b'},
                                         fname='/unused/path/name')

