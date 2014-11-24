# This file is part of Checkbox.
#
# Copyright 2014 Canonical Ltd.
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
:mod:`plainbox.impl.connection.phablet` -- phablet connection method
====================================================================
"""
import logging
import urllib.parse

from plainbox.abc import IConnectionMethod
from plainbox.i18n import gettext as _
from plainbox.impl.connection.ssh import SecureShellConnectionMethod
from plainbox.vendor.phablet import Phablet

_logger = logging.getLogger("plainbox.connection.ssh")


class PhabletConnectionMethod(IConnectionMethod):

    def __init__(self):
        self._persist = None
        self._phablet = None
        self._ssh_meth = None

    @property
    def _ssh_url(self):
        return 'ssh://phablet@localhost:{}/?{}'.format(
            self._phablet.port,
            '&'.join([
                'CheckHostIP=no',
                'StrictHostKeyChecking=no',
                'UserKnownHostsFile=/dev/null',
                'LogLevel=quiet',
                'KbdInteractiveAuthentication=no',
                'PasswordAuthentication=no']))

    def connect(self, url):
        self._parse_url(url)
        self._phablet.connect()
        self._ssh_meth = SecureShellConnectionMethod()
        return self._ssh_meth.connect(self._ssh_url)

    def disconnect(self, url):
        # This is kind of silly
        self._parse_url(url)
        self._ssh_meth = SecureShellConnectionMethod()
        self._ssh_meth.disconnect(self._ssh_url)

    def peek(self, url):
        self._parse_url(url)
        self._phablet.connect()
        self._ssh_meth = SecureShellConnectionMethod()
        self._ssh_meth.peek(self._ssh_url)

    def get_hints(self):
        return []

    def _parse_url(self, url):
        urlsplit_result = urllib.parse.urlsplit(url)
        if urlsplit_result.scheme != 'phablet':
            raise ValueError(
                "unsupported scheme: {}".format(urlsplit_result.scheme))
        self._serial = urlsplit_result.netloc or None
        self._phablet = Phablet(self._serial)
        for opt_name, opt_value in urllib.parse.parse_qsl(
                urlsplit_result.query):
            if opt_name == 'persist' and opt_value == 'yes':
                self._persist = True
            elif opt_name == 'persist' and opt_value == 'no':
                self._persist = False
            else:
                _logger.warning(
                    _("Unsupported option %s=%r"), opt_name, opt_value)
