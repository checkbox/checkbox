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
:mod:`plainbox.errors` -- Exceptions and Error Classes
======================================================
"""
from plainbox.i18n import gettext as _


class ConnectionError(Exception):
    """
    Base class for all errors related to device connections
    """


class UnsupportedConnectionScheme(LookupError, ConnectionError):
    """
    Exception raised when connection to an URL with unsupported scheme
    is attempted.
    """

    def __init__(self, scheme):
        self.scheme = scheme

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.scheme)

    def __str__(self):
        return _(
            "Device connection scheme {!a} is unsupported"
        ).format(self.scheme)


class UnsupportedDeviceAPI(KeyError):
    """
    Exception raised when attempting to use a device connection API that is not
    supported over a particular connection.
    """


class DeviceOperationError(ConnectionError):
    """
    Base class for all device API operation failures.

    This class is shared by :class:`FileSystemOperationError` and
    :class:`ProcessOperationError`.

    :attr op:
        Name of the operation that failed (this is always a string)
    :attr args:
        Arguments to the operation. All the arguments are retained in
        their original form but will be converted to strings for
        display.
    :attr msg:
        An optional customized message that is specific to this error.
        This message may be provided to improve the readability of the
        final exception text.
    """

    def __init__(self, op, args, msg=None):
        self.op = op
        self.args = args
        self.msg = msg

    def __repr__(self):
        return "{}({!r}, {!r}, {!r})".format(
            self.__class__.__name__, self.op, self.args, self.msg)

    def __str__(self):
        return "{}: {} {}".format(
            self.msg or self.get_stock_msg(),
            self.op, ' '.join(ascii(arg) for arg in self.args))

    def get_stock_msg(self):
        return _("Device operation failed")


class FileSystemOperationError(DeviceOperationError):
    """
    Exception raised when a filesystem operation, based on the
    :class:`~plainbox.abc.IFileSystemAPI` interface, fails in some way.
    """

    def get_stock_msg(self):
        return _("File system operation failed")


class ProcessOperationError(DeviceOperationError):
    """
    Exception raised when a process execution operation, based on the
    :class:`~plainbox.abc.IProcessAPI` interface, fails in some way.

    .. note::
        Some process operations may fail due to remote process control
        complexities. This exception class is reserved for such cases.

        In other cases a *standard* ``subprocess.CalledProcessError``
        exception is raised, whenever the process interface is
        mimicking the subprocess APIs.
    """

    def get_stock_msg(self):
        return _("Process operation failed")
