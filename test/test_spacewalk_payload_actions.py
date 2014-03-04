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
import unittest
from katello_notification.spacewalk_payload_actions import SpacewalkPayloadActions


class TestSpacewalkPayloadActions(unittest.TestCase):

    @patch('katello_notification.spacewalk_wrapper.Spacewalk.__init__')
    def setUp(self, spacewalk_init):
        spacewalk_init.return_value = None
        self.spacewalk_payload_actions = SpacewalkPayloadActions()

    @patch('katello_notification.spacewalk_wrapper.Spacewalk.find_hypervisor')
    def test_find_or_create_hypervisor_no_hyp(self, mock_find_hypervisor):
        mock_find_hypervisor.return_value = None
        self.assertRaises(RuntimeError,
                          self.spacewalk_payload_actions.find_or_create_hypervisor,
                          {"host": "unknown_hypervisor"})

    @patch('katello_notification.spacewalk_wrapper.Spacewalk.find_hypervisor')
    def test_find_or_create_hypervisor_found_hyp(self, mock_find_hypervisor):
        mock_find_hypervisor.return_value = "1000001"
        self.assertEquals("1000001", self.spacewalk_payload_actions.find_or_create_hypervisor({"host": "known_hypervisor"}))

    @patch('katello_notification.spacewalk_wrapper.Spacewalk.associate_guest')
    def test_create_guest_mapping(self, mock_associate_guest):
        self.spacewalk_payload_actions.create_guest_mapping({"instance_id": "A6A2B164-A2EB-11E3-828C-D749BDF4F982"},
                                                            "CE223F92-A2EC-11E3-8C12-D749BDF4F982")
        mock_associate_guest.assert_called_once_with("A6A2B164-A2EB-11E3-828C-D749BDF4F982", "CE223F92-A2EC-11E3-8C12-D749BDF4F982")

    @patch('katello_notification.spacewalk_wrapper.Spacewalk.unassociate_guest')
    def test_delete_guest_mapping(self, mock_unassociate_guest):
        # note: this is fed through to the spacewalk wrapper, which no-ops
        self.spacewalk_payload_actions.delete_guest_mapping({"instance_id": "A6A2B164-A2EB-11E3-828C-D749BDF4F982"},
                                                            "CE223F92-A2EC-11E3-8C12-D749BDF4F982")
        mock_unassociate_guest.assert_called_once_with("A6A2B164-A2EB-11E3-828C-D749BDF4F982", "CE223F92-A2EC-11E3-8C12-D749BDF4F982")
