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
from katello_notification.spacewalk_wrapper import Spacewalk
import StringIO

TEST_CONFIG = """
[main]
autoregister_hypervisors = false

[spacewalk]
host = some.hostname
port = 443
scheme = https
username = admin
password = admin
"""

TEST_CONFIG_AUTOREG = """
[main]
autoregister_hypervisors = true

[spacewalk]
host = some.hostname
port = 443
scheme = https
username = admin
password = admin
"""

#this is missing unused values
TEST_SYSID = {"system_id": '<?xml version="1.0"?><params><param><value>' +
                           '<struct><member><name>system_id</name><value>' +
                           '<string>ID-1000010007</string></value></member>' +
                           '</struct></value></param></params>'}


class StubServer():
    """
    there must be a better way to stub/mock this.
    """

    class StubObj():
        pass

    def _registration_new_system_user_pass(self, unused1, unused2, unused3,
                                           unused4, unused5, unused6, unused7):
        return TEST_SYSID

    def _registration_refresh_hw_profile(self, unused1, unused2):
        return

    def _auth_login(self, unused1, unused2):
        return "some_key"

    def _registration_virt_notify(self, unused1, unused2):
        return

    def _system_getId(self, unused1, unused2):
        return self.sshr

    def _system_downloadSystemId(self, unused1, unused2):
        return "some_id"

    def _system_listVirtualGuests(self, unused1, unused2):
        return [{"uuid": "3F6403F6-A88E-11E3-BCC6-161DBDF4F982"},
                {"uuid": "4AA0D2EE-A88E-11E3-8997-161DBDF4F982"}]

    def __init__(self):
        self.auth = self.StubObj()
        self.auth.login = self._auth_login
        self.system = self.StubObj()
        self.system.downloadSystemId = self._system_downloadSystemId
        self.system.listVirtualGuests = self._system_listVirtualGuests
        self.system.getId = self._system_getId
        self.registration = self.StubObj()
        self.registration.new_system_user_pass = self._registration_new_system_user_pass
        self.registration.refresh_hw_profile = self._registration_refresh_hw_profile
        self.registration.virt_notify = self._registration_virt_notify

    def set_system_get_id_result(self, res):
        self.sshr = res


class TestSpacewalkWrapper(unittest.TestCase):

    @patch('xmlrpclib.Server')
    @patch('__builtin__.open')
    def setUp(self, mock_open, mock_xmlrpclib):
        self.stubserver = StubServer()
        mock_open.return_value = StringIO.StringIO(TEST_CONFIG)
        mock_xmlrpclib.return_value = self.stubserver
        self.sw = Spacewalk()

    def test_spacewalk_find_hypervisor(self):
        self.stubserver.set_system_get_id_result([])
        self.assertEquals(None, self.sw.find_hypervisor('unknown_hostname'))

        self.stubserver.set_system_get_id_result(["sys1", "sys2"])
        self.assertRaises(RuntimeError, self.sw.find_hypervisor, 'multi_match_hostname')

        self.stubserver.set_system_get_id_result([{'id': '1234'}])
        self.assertEquals('1234', self.sw.find_hypervisor('single_match_hostname'))

    @patch('xmlrpclib.Server')
    @patch('__builtin__.open')
    def test_spacewalk_find_hypervisor_autoregister(self, mock_open, mock_xmlrpclib):

        # save the old spacewalk wrapper so we can reset it later
        old_sw = self.sw

        self.stubserver = StubServer()
        mock_open.return_value = StringIO.StringIO(TEST_CONFIG_AUTOREG)
        mock_xmlrpclib.return_value = self.stubserver
        self.sw = Spacewalk()

        self.stubserver.set_system_get_id_result([])
        self.assertEquals('1000010007', self.sw.find_hypervisor('unknown_hostname'))

        self.stubserver.set_system_get_id_result(["sys1", "sys2"])
        self.assertRaises(RuntimeError, self.sw.find_hypervisor, 'multi_match_hostname')

        self.stubserver.set_system_get_id_result([{'id': '1234'}])
        self.assertEquals('1234', self.sw.find_hypervisor('single_match_hostname'))

        self.sw = old_sw

    def test_spacewalk_associate_guest(self):
        self.sw.associate_guest('B048F7F8-A310-11E3-8E5D-D749BDF4F982', '1234')

    def test_katello_unassociate_guest(self):
        #assert(False)
        pass
