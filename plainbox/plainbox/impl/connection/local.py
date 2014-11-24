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
:mod:`plainbox.impl.connection.local` -- local connection method
================================================================
"""
import logging
import os
import shutil
import stat
import subprocess
import urllib.parse

from plainbox.abc import IConnection
from plainbox.abc import IConnectionMethod
from plainbox.abc import IFileSystemAPI
from plainbox.abc import IOperatingSystemAPI
from plainbox.abc import IProcessAPI
from plainbox.abc import IProviderConsumerAPI
from plainbox.errors import FileSystemOperationError
from plainbox.errors import UnsupportedDeviceAPI
from plainbox.i18n import gettext as _
from plainbox.impl.connection.common import AbstractConnection
from plainbox.impl.connection.common import listdir_info
from plainbox.impl.decorators import raises
from plainbox.impl.os_probe import probe_os


_logger = logging.getLogger("plainbox.connection.local")


class LocalConnectionMethod(IConnectionMethod):
    """
    Class representing a "connection method" to the local device
    """

    URL = "local://"

    def connect(self, url):
        self._parse_url(url)
        return LocalConnection()

    def peek(self, url):
        return self.STATUS_CONNECTED

    def disconnect(self, url):
        pass

    def get_hints(self):
        return [self.URL]

    def _parse_url(self, url):
        urlsplit_result = urllib.parse.urlsplit(url)
        if urlsplit_result.scheme != 'local':
            raise ValueError("unsupported scheme: {!r}".format(url))
        for opt_name, opt_value in urllib.parse.parse_qsl(
                urlsplit_result.query):
            if opt_name == 'persist' and opt_value in ('yes', 'no'):
                pass  # just ignore it
            else:
                _logger.warning(
                    _("Unsupported option %s=%r"), opt_name, opt_value)


class LocalFileSystem(IFileSystemAPI):

    @raises(FileSystemOperationError)
    def read(self, filename: str) -> bytes:
        try:
            with open(filename, 'rb') as stream:
                return stream.read()
        except (IOError, OSError) as exc:
            raise FileSystemOperationError('read', [filename], str(exc))

    @raises(FileSystemOperationError)
    def write(self, filename: str, data: bytes) -> int:
        try:
            with open(filename, 'wb') as stream:
                return stream.write(data)
        except (IOError, OSError) as exc:
            raise FileSystemOperationError('write', [filename], str(exc))

    @raises(FileSystemOperationError)
    def remove(self, filename: str) -> None:
        try:
            os.remove(filename)
        except (IOError, OSError) as exc:
            raise FileSystemOperationError('remove', [filename], str(exc))

    @raises(FileSystemOperationError)
    def symlink(self, name: str, target: str) -> None:
        try:
            os.symlink(target, name)
        except (IOError, OSError) as exc:
            raise FileSystemOperationError('symlink', [name, target], str(exc))

    @raises(FileSystemOperationError)
    def listdir(self, dirname: str) -> list:
        entry_list = []
        try:
            for entry_name in os.listdir(dirname):
                filename = os.path.join(dirname, entry_name)
                stat_result = os.lstat(filename)
                entry_type = st_mode_to_entry_type(stat_result.st_mode)
                entry_list.append(listdir_info(entry_name, entry_type))
        except (IOError, OSError) as exc:
            raise FileSystemOperationError('listdir', [filename], str(exc))
        else:
            return entry_list

    @raises(FileSystemOperationError)
    def mkdir(self, dirname: str) -> None:
        try:
            os.mkdir(dirname)
        except (IOError, OSError) as exc:
            raise FileSystemOperationError('dirname', [dirname], str(exc))

    @raises(FileSystemOperationError)
    def rmdir(self, dirname: str) -> None:
        try:
            os.rmdir(dirname)
        except (IOError, OSError) as exc:
            raise FileSystemOperationError('rmdir', [dirname], str(exc))

    @raises(FileSystemOperationError)
    def exists(self, pathname: str) -> bool:
        try:
            return os.path.exists(pathname)
        except FileSystemOperationError:
            return False

    def isdir(self, pathname: str) -> bool:
        try:
            return os.path.isdir(pathname)
        except FileSystemOperationError:
            return False

    def isfile(self, pathname: str) -> bool:
        try:
            return os.path.isfile(pathname)
        except FileSystemOperationError:
            return False

    def islink(self, pathname: str) -> bool:
        try:
            return os.path.islink(pathname)
        except FileSystemOperationError:
            return False

    @raises(FileSystemOperationError)
    def push(self, local_path: str, remote_path: str) -> None:
        try:
            shutil.copyfile(local_path, remote_path)
        except (IOError, OSError) as exc:
            raise FileSystemOperationError(
                'push', [local_path, remote_path], str(exc))

    @raises(FileSystemOperationError)
    def pull(self, remote_path: str, local_path: str) -> None:
        try:
            shutil.copyfile(remote_path, local_path)
        except (IOError, OSError) as exc:
            raise FileSystemOperationError(
                'pull', [remote_path, local_path], str(exc))


class LocalProcess(IProcessAPI):

    def popen(self, *args, **kwargs):
        return subprocess.Popen(*args, **kwargs)

    def check_output(self, *args, **kwargs):
        return subprocess.check_output(*args, **kwargs)

    def check_call(self, *args, **kwargs):
        return subprocess.check_call(*args, **kwargs)


class LocalOperatingSystem(IOperatingSystemAPI):

    def __init__(self, os_metadata):
        self._os_metadata = os_metadata

    @property
    def abi_cookie(self) -> str:
        return "&".join(
            '{}={}'.format(key, self.os_metadata[key])
            for key in ('os', 'id', 'version_id', 'arch'))

    @property
    def os_metadata(self) -> dict:
        return self._os_metadata


class LocalProviderConsumer(IProviderConsumerAPI):

    def __init__(self, os_api):
        self._provider_list = []
        self._os_api = os_api

    def push_provider(self, provider):
        # TODO: check ABI cookie
        self._provider_list.append(provider)

    def get_execution_controller_list(self) -> 'List[IExecutionController]':
        os_type = self._os_api.os_metadata.get('os', 'unknown')
        if os_type == 'linux':
            from plainbox.impl.ctrl import RootViaPkexecExecutionController
            from plainbox.impl.ctrl import RootViaPTL1ExecutionController
            from plainbox.impl.ctrl import RootViaSudoExecutionController
            from plainbox.impl.ctrl import UserJobExecutionController
            return [
                RootViaPTL1ExecutionController(self._provider_list),
                RootViaPkexecExecutionController(self._provider_list),
                # XXX: maybe this one should be only used on command line
                RootViaSudoExecutionController(self._provider_list),
                UserJobExecutionController(self._provider_list),
            ]
        elif os_type == 'win32':
            from plainbox.impl.ctrl import UserJobExecutionController
            return [UserJobExecutionController(self._provider_list)]
        else:
            _logger.warning(_("Unsupported Operating System: %s"), os_type)
            return []


class LocalConnection(AbstractConnection):
    """
    Class representing a "connection" to the local device
    """

    __slots__ = ('_fs_api', '_proc_api', '_os_api', '_provider_cosumer_api',
                 '_url')

    _API_SET = {
        IConnection.API_FILE_SYSTEM,
        IConnection.API_OPERATING_SYSTEM,
        IConnection.API_PROCESS,
        IConnection.API_PROVIDER_CONSUMER,
    }

    def __init__(self):
        super().__init__('local://')
        self._fs_api = None
        self._proc_api = None
        self._os_api = None
        self._provider_consumer_api = None

    @property
    def api_set(self):
        return self._API_SET

    @raises(UnsupportedDeviceAPI)
    def api(self, name):
        if name == IConnection.API_FILE_SYSTEM:
            if self._fs_api is None:
                self._fs_api = LocalFileSystem()
            return self._fs_api
        if name == IConnection.API_OPERATING_SYSTEM:
            if self._os_api is None:
                os_metadata = probe_os(self)
                self._os_api = LocalOperatingSystem(os_metadata)
            return self._os_api
        if name == IConnection.API_PROCESS:
            if self._proc_api is None:
                self._proc_api = LocalProcess()
            return self._proc_api
        if name == IConnection.API_PROVIDER_CONSUMER:
            if self._provider_consumer_api is None:
                self._provider_consumer_api = LocalProviderConsumer(
                    self.api(IConnection.API_OPERATING_SYSTEM))
            return self._provider_consumer_api
        raise UnsupportedDeviceAPI(name)

    @property
    def persist(self):
        return True

    @persist.setter
    def persist(self, value):
        if value is not True:
            raise ValueError(_("Local connections are always persistent"))

    def status(self):
        return self.STATUS_CONNECTED


def st_mode_to_entry_type(st_mode: int) -> int:
    """
    Convert ``stat.stat_result.st_mode`` to ``IFileSystemAPI.TYPE_`` constant
    """
    if stat.S_ISREG(st_mode):
        return IFileSystemAPI.TYPE_FILE
    elif stat.S_ISDIR(st_mode):
        return IFileSystemAPI.TYPE_DIRECTORY
    elif stat.S_ISLNK(st_mode):
        return IFileSystemAPI.TYPE_SYMLINK
    elif stat.S_ISBLK(st_mode):
        return IFileSystemAPI.TYPE_BLOCK_DEVICE
    elif stat.S_ISCHR(st_mode):
        return IFileSystemAPI.TYPE_CHARACTER_DEVICE
    elif stat.S_ISFIFO(st_mode):
        return IFileSystemAPI.TYPE_NAMED_PIPE
    elif stat.S_ISSOCK(st_mode):
        return IFileSystemAPI.TYPE_SOCKET
    else:
        return IFileSystemAPI.TYPE_UNKNOWN
