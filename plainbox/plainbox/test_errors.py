# This file is part of Checkbox.
#
# Copyright 2012-2014 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.
#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.

"""
plainbox.test_errors
====================
"""
from unittest import TestCase

from plainbox.errors import ConnectionError
from plainbox.errors import DeviceOperationError
from plainbox.errors import FileSystemOperationError
from plainbox.errors import ProcessOperationError
from plainbox.errors import UnsupportedConnectionScheme
from plainbox.errors import UnsupportedDeviceAPI


class ConnectionErrorTests(TestCase):

    def test_base_class(self):
        self.assertTrue(issubclass(ConnectionError, Exception))


class UnsupportedConnectionSchemeTests(TestCase):

    SCHEME = "scheme"

    def setUp(self):
        self.obj = UnsupportedConnectionScheme(self.SCHEME)

    def test_base_class(self):
        self.assertTrue(issubclass(UnsupportedConnectionScheme, LookupError))
        self.assertTrue(issubclass(UnsupportedConnectionScheme, ConnectionError))

    def test_repr(self):
        self.assertEqual(
            repr(self.obj), "UnsupportedConnectionScheme('scheme')")

    def test_str(self):
        self.assertEqual(
            str(self.obj), "Device connection scheme 'scheme' is unsupported")
