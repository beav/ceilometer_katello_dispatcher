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
from tempfile import NamedTemporaryFile
from katello_notification.katello_wrapper import Katello
import StringIO

TEST_CONFIG = """
[main]
autoregister_hypervisors = false

[katello]
host = some.hostname
port = 443
scheme = https
path = /sam
default_org = ACME_Corporation
username = admin
password = admin
"""

TEST_CONFIG_AUTOREGISTER = """
[main]
autoregister_hypervisors = true

[katello]
host = some.hostname
port = 443
scheme = https
path = /sam
default_org = ACME_Corporation
username = admin
password = admin
"""


class TestKatelloWrapper(unittest.TestCase):

    @patch('__builtin__.open')
    def setUp(self, mock_open):
        mock_open.return_value = StringIO.StringIO(TEST_CONFIG)
        self.kw = Katello()

    @patch('katello.client.api.system.SystemAPI.systems_by_org')
    def test_katello_find_hypervisor(self, mock_systems_by_org):
        # test no hypervisors found
        mock_systems_by_org.return_value = []
        self.assertEquals(self.kw.find_hypervisor('fake_hypervisor_hostname'), None)

        # test >1 hypervisors found
        mock_systems_by_org.return_value = ['hyper1', 'hyper2']
        self.assertEquals(self.kw.find_hypervisor('fake_hypervisor_hostname'), None)

        # test 1 hypervisor found
        mock_systems_by_org.return_value = [{'uuid': '4ced494a-884c-11e3-aa46-ce96db0f677b'}]
        self.assertEquals(self.kw.find_hypervisor('fake_hypervisor_hostname'), '4ced494a-884c-11e3-aa46-ce96db0f677b')

    @patch('__builtin__.open')
    @patch('katello.client.api.system.SystemAPI.register')
    @patch('katello.client.api.system.SystemAPI.checkin')
    @patch('katello.client.api.system.SystemAPI.systems_by_org')
    def test_katello_find_hypervisor_autoregister(self, mock_systems_by_org, mock_checkin, mock_register, mock_open):

        # use a different katello_wrapper
        old_kw = self.kw
        mock_open.return_value = StringIO.StringIO(TEST_CONFIG_AUTOREGISTER)
        self.kw = Katello()

        # test no hypervisors found, create a hypervisor
        mock_systems_by_org.return_value = []
        mock_register.return_value = {"uuid": '2AAFE962-AB8A-11E3-A989-0DFFF048AC65'}
        self.assertEquals(self.kw.find_hypervisor('fake_hypervisor_hostname'), '2AAFE962-AB8A-11E3-A989-0DFFF048AC65')

        # test >1 hypervisors found
        mock_systems_by_org.return_value = ['hyper1', 'hyper2']
        self.assertEquals(self.kw.find_hypervisor('fake_hypervisor_hostname'), None)

        # test 1 hypervisor found
        mock_systems_by_org.return_value = [{'uuid': '4ced494a-884c-11e3-aa46-ce96db0f677b'}]
        self.assertEquals(self.kw.find_hypervisor('fake_hypervisor_hostname'), '4ced494a-884c-11e3-aa46-ce96db0f677b')

        # reload old config
        self.kw = old_kw

    @patch('katello.client.api.system.SystemAPI.system')
    @patch('katello.client.api.system.SystemAPI.update')
    def test_katello_associate_guest(self, mock_update, mock_system):
        self.kw.associate_guest('40e3380c-884d-11e3-aa46-ce96db0f677b', '500c57b4-884d-11e3-aa46-ce96db0f677b')
        mock_system.assert_called_once_with('500c57b4-884d-11e3-aa46-ce96db0f677b')
        mock_update.assert_called_once()

    @patch('katello.client.api.system.SystemAPI.system')
    @patch('katello.client.api.system.SystemAPI.update')
    def test_katello_unassociate_guest(self, mock_update, mock_system):
        mock_system.return_value = {'name': 'hypervisor1', 'guestIds': [{'guestId': '20fd8046-8853-11e3-a7b4-ce96db0f677b'}]}
        self.kw.unassociate_guest('20fd8046-8853-11e3-a7b4-ce96db0f677b', '500c57b4-884d-11e3-aa46-ce96db0f677b')
        mock_system.assert_called_once_with('500c57b4-884d-11e3-aa46-ce96db0f677b')
        mock_update.assert_called_once('500c57b4-884d-11e3-aa46-ce96db0f677b', [])
