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
[spacewalk]
host = some.hostname
port = 443
scheme = https
username = admin
password = admin
"""


class StubServer():
    """
    there must be a better way to stub/mock this.
    """

    class StubObj():
        pass

    def _auth_login(self, unused1, unused2):
        return "some_key"

    def _registration_virt_notify(self, unused1, unused2):
        return

    def _system_search_hostname(self, unused1, unused2):
        return self.sshr

    def _system_downloadSystemId(self, unused1, unused2):
        return "some_id"

    def __init__(self):
        self.auth = self.StubObj()
        self.auth.login = self._auth_login
        self.system = self.StubObj()
        self.system.downloadSystemId = self._system_downloadSystemId
        self.system.search = self.StubObj()
        self.system.search.hostname = self._system_search_hostname
        self.registration = self.StubObj()
        self.registration.virt_notify = self._registration_virt_notify

    def set_system_search_hostname_result(self, res):
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
        self.stubserver.set_system_search_hostname_result([])
        self.assertEquals(None, self.sw.find_hypervisor('unknown_hostname'))

        self.stubserver.set_system_search_hostname_result(["sys1", "sys2"])
        self.assertRaises(RuntimeError, self.sw.find_hypervisor, 'multi_match_hostname')

        self.stubserver.set_system_search_hostname_result([{'id': '1234'}])
        self.assertEquals('1234', self.sw.find_hypervisor('single_match_hostname'))

    def test_spacewalk_associate_guest(self):
        self.sw.associate_guest('B048F7F8-A310-11E3-8E5D-D749BDF4F982', '1234')

    def test_katello_unassociate_guest(self):
        #assert(False)
        pass
