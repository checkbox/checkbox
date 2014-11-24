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
:mod:`plainbox.impl.connection` -- device connection APIs
=========================================================
"""
import logging
import urllib.parse

from plainbox.abc import IConnection
from plainbox.abc import IConnectionMethod
from plainbox.errors import UnsupportedConnectionScheme
from plainbox.i18n import gettext as _
from plainbox.impl.secure.plugins import PkgResourcesPlugInCollection

__all__ = ['open_connection', 'peek_connection']

_logger = logging.getLogger("plainbox.connection")


all_conn_methods = PkgResourcesPlugInCollection('plainbox.connection')


class ConnectionManager:
    """
    Intermediate class that allows setting up, checking and tearing down
    connections between the host machine and various test devices.
    """

    def __init__(self, url: str):
        """
        :param url:
            URL describing the device
        :raises ValueError:
            If the URL cannot be parsed in any way
        :raises LookupError:
            If the scheme used in the URL cannot be associated with any known
            connection method.
        """
        self._url = url
        self._method = self._get_conn_method()

    def peek(self) -> str:
        """
        Check the status of a connection

        :returns:
            A string that describes the status of the connection
        """
        return self._method.peek(self._url)

    def connect(self) -> IConnection:
        """
        Establish connection to the device

        :returns:
            The open connection
        :raises ConnectionError:
            If we cannot connect for any reason
        """
        return self._method.connect(self._url)

    def disconnect(self):
        """
        Close connection to the device

        :returns:
            The open connection
        :raises ConnectionError:
            If we cannot connect for any reason
        """
        return self._method.disconnect(self._url)

    def _get_conn_method(self) -> IConnectionMethod:
        all_conn_methods.load()
        split_url = urllib.parse.urlsplit(self._url)
        _logger.debug(
            _("Parsed connection URL %r to %r"), self._url, split_url)
        if split_url.scheme == '':
            raise ValueError(
                _("Value doesn't look like an URL: {!a}").format(self._url))
        try:
            conn_method_cls = all_conn_methods.get_by_name(
                split_url.scheme
            ).plugin_object
        except KeyError as exc:
            raise UnsupportedConnectionScheme(exc.args[0])
        _logger.debug(
            _("Selected connection method %s for url %r"),
            conn_method_cls, self._url)
        return conn_method_cls()
