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
:mod:`plainbox.impl.connection.ssh` -- ssh connection method
============================================================
"""
import logging
import os
import re
import subprocess
import tempfile
import urllib.parse

from plainbox.abc import IConnection
from plainbox.abc import IConnectionMethod
from plainbox.abc import IFileSystemAPI
from plainbox.abc import IOperatingSystemAPI
from plainbox.abc import IProcessAPI
from plainbox.errors import ConnectionError
from plainbox.errors import FileSystemOperationError
from plainbox.errors import UnsupportedDeviceAPI
from plainbox.i18n import gettext as _
from plainbox.impl.connection.common import RemoteExecutionController
from plainbox.impl.connection.common import RemoteProvider1
from plainbox.impl.connection.common import listdir_info
from plainbox.impl.decorators import raises
from plainbox.impl.os_probe import probe_os

_logger = logging.getLogger("plainbox.connection.ssh")


class SecureShellMaster:

    _SOCKET = '/tmp/plainbox_ssh_master_%h_%p_%r'

    def __init__(self, netloc, port=22, extra_options=None):
        self._netloc = netloc
        self._port = port
        self._extra_options = extra_options

    def __repr__(self):
        return "{}({!r}, {!r})".format(
            self.__class__.__name__, self._netloc, self._port)

    @property
    def ssh_options(self) -> 'List[str]':
        options = [
            '-o', 'Port={}'.format(self.port),
            '-o', 'ControlPath={}'.format(self._SOCKET)]
        if self.extra_options is not None:
            options.extend(self.extra_options)
        return options

    @property
    def netloc(self) -> str:
        return self._netloc

    @property
    def port(self) -> int:
        return self._port

    @property
    def extra_options(self):
        return self._extra_options

    @extra_options.setter
    def extra_options(self, extra_options):
        self._extra_options = extra_options

    def run(self):
        _logger.debug("%r.run() -> ...", self)
        # -M: Enable ssh master mode
        # -S: use this master control socket
        # -N: Do not run shell commands
        # -f: Run in the background after setting up the connection
        _logger.info(_("Starting master SSH connection to %s, port %d"),
                     self.netloc, self.port)
        args = ['ssh', '-M', '-S', self._SOCKET, '-N', '-f']
        if self.extra_options is not None:
            args.extend(self.extra_options)
        args.extend(['-p', str(self.port), self.netloc])
        _logger.debug(_("Running SSH: %r"), ' '.join(args))
        subprocess.check_call(args)
        _logger.info(_("Master SSH connection established"))
        _logger.debug("%r.run()", self)

    def exit(self):
        _logger.debug("%r.exit() -> ...", self)
        # -S: use this master control socket
        # -O: execute control command
        _logger.info(_("Closing master SSH connection to %s, port %d"),
                     self.netloc, self.port)
        args = ['ssh', '-S', self._SOCKET, '-O', 'exit']
        if self.extra_options is not None:
            args.extend(self.extra_options)
        args.extend(['-p', str(self.port), self.netloc])
        _logger.debug(_("Running SSH: %r"), ' '.join(args))
        try:
            subprocess.check_output(args, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            if exc.returncode == 255:
                _logger.debug(_("Got 255 exit code from ssh, general failure"))
                _logger.debug(_("SSH said: %r"), exc.output)
            else:
                raise
        _logger.debug("%r.exit()", self)

    def is_running(self):
        # -S: use this master control socket
        # -O: execute control command
        _logger.debug("%r.is_running() -> ...", self)
        _logger.info(_("Checking master SSH connection to %s, port %d"),
                     self.netloc, self.port)
        args = ['ssh', '-S', self._SOCKET, '-O', 'check']
        if self.extra_options is not None:
            args.extend(self.extra_options)
        args.extend(['-p', str(self.port), self.netloc])
        _logger.debug(_("Running SSH: %r"), ' '.join(args))
        is_running = False
        try:
            status = subprocess.check_output(args, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            if exc.returncode == 255:
                _logger.debug(_("Got 255 exit code from ssh, general failure"))
                _logger.debug(_("SSH said: %r"), exc.output)
            else:
                raise
        else:
            _logger.debug(_("SSH said: %r"), status)
            # NOTE: I've checked openssh 6.6p1 and that's how it behaves
            # note that this status is printed to stderr, not stdout but
            # that's irrelevant since we combine both.
            #
            # The message also has a PID but we don't need it
            if status.startswith(b"Master running"):
                is_running = True
        _logger.debug(_("%r.is_running() -> %r"), self, is_running)
        return is_running


class SecureShellConnectionMethod(IConnectionMethod):

    def __init__(self):
        self._persist = None  # None is different from False, see connect()
        self._master = None

    def connect(self, url):
        self._parse_url(url)
        # Check if the master is running
        if self._master.is_running():
            # If the master was running, don't kill it unless we were asked not
            # to persist explicitly (then _persist would have been set to
            # False)
            if self._persist is None:
                self._persist = True
        else:
            # If not, start the master now
            self._master.run()
            # If it's still not running, connection has failed
            if not self._master.is_running():
                raise ConnectionError(_("Unable to connect"))
        try:
            conn = SecureShellConnection(self._master, url)
        except:
            _logger.exception(_("Aborting due to initialization failure"))
            self._master.exit()
            raise
        else:
            # Apply the desired persistence flag to the connection
            conn.persist = self._persist
        return conn

    def disconnect(self, url):
        self._parse_url(url)
        self._master.exit()

    def peek(self, url):
        self._parse_url(url)
        try:
            if self._master.is_running():
                return IConnection.STATUS_CONNECTED
            else:
                return IConnection.STATUS_DISCONNECTED
        except subprocess.CalledProcessError:
            _logger.exception(_("Unable to check status of SSH master"))
            return IConnection.STATUS_ERROR

    def get_hints(self):
        # cat ~/.ssh/known_hosts | cut -f 1 -d ' ' | grep -v '^|1|'
        # | tr ',' '\n' | sort | uniq
        hints = set()
        known_hosts = os.path.expanduser('~/.ssh/known_hosts')
        with open(known_hosts, 'rt', encoding='UTF-8') as stream:
            for line in stream:
                if line.startswith('|1|'):
                    continue
                for host in line.split(' ')[0].split(','):
                    hints.add('ssh://{}'.format(host))
        return hints

    def _parse_url(self, url):
        urlsplit_result = urllib.parse.urlsplit(url)
        if urlsplit_result.scheme != 'ssh':
            raise ValueError(
                "unsupported scheme: {}".format(urlsplit_result.scheme))
        if ":" in urlsplit_result.netloc:
            user_host, port = urlsplit_result.netloc.split(":", 1)
            port = int(port)
        else:
            user_host, port = urlsplit_result.netloc, 22
        extra_options = []
        for opt_name, opt_value in urllib.parse.parse_qsl(
                urlsplit_result.query):
            if opt_name == 'persist' and opt_value == 'yes':
                self._persist = True
            elif opt_name == 'persist' and opt_value == 'no':
                self._persist = False
            elif opt_name in ('CheckHostIP',
                              'StrictHostKeyChecking',
                              'UserKnownHostsFile', 'LogLevel',
                              'KbdInteractiveAuthentication',
                              'PasswordAuthentication'):
                extra_options.append('-o')
                extra_options.append('{}={}'.format(opt_name, opt_value))
            else:
                _logger.warning(
                    _("Unsupported option %s=%r"), opt_name, opt_value)
        self._master = SecureShellMaster(user_host, port, extra_options)


class SecureShellConnection(IConnection, IProcessAPI, IFileSystemAPI,
                            IOperatingSystemAPI):

    def __init__(self, master, url):
        self._provider_list = []
        self._master = master
        self._url = url
        self._persist = False
        self._os_metadata = None  # do that lazily

    def __repr__(self):
        return "<{} url:{!r}>".format(
            self.__class__.__name__,
            self._url)

    def __str__(self):
        return self._url

    # Connection API

    @property
    def url(self):
        return self._url

    @raises(UnsupportedDeviceAPI)
    def api(self, name: str) -> object:
        return self

    @property
    def api_set(self):
        if self.os_metadata.get('os') == 'linux':
            return {'fs': self, 'os': self, 'proc': self, 'provider': self}
        else:
            return {'fs': self, 'os': self, 'proc': self}

    def close(self):
        _logger.debug("%s.close()", self.__class__.__name__)
        for remote_provider in self._provider_list:
            remote_provider.close()
        if self._persist:
            _logger.debug(_("Not shutting down master SSH connection in"
                            " persistent mode"))
        else:
            if self._master is not None:
                self._master.exit()
                self._master = None

    @property
    def persist(self):
        return self._persist

    @persist.setter
    def persist(self, value):
        self._persist = value

    def status(self):
        try:
            if self._master.is_running():
                return self.STATUS_CONNECTED
            else:
                return self.STATUS_DISCONNECTED
        except subprocess.CalledProcessError:
            _logger.exception(_("Unable to check status of SSH master"))
            return self.STATUS_ERROR

    def __enter__(self) -> IConnection:
        return self

    def __exit__(self, *args):
        self.close()

    # Proc API

    def translate_cmd(self, *args, **kwargs):
        args, kwargs = self._translate_ssh_call(args, kwargs)
        return args, kwargs

    def popen(self, *args, **kwargs):
        _logger.debug("popen(%r, %r)",  args, kwargs)
        args, kwargs = self._translate_ssh_call(args, kwargs)
        _logger.debug(_("popen(...) translated to %r, %r"), args, kwargs)
        return subprocess.Popen(*args, **kwargs)

    def call(self, *args, **kwargs):
        _logger.debug("call(%r, %r)",  args, kwargs)
        args, kwargs = self._translate_ssh_call(args, kwargs)
        _logger.debug(_("call(...) translated to %r, %r"), args, kwargs)
        retval = subprocess.call(*args, **kwargs)
        _logger.debug(_("call(...) -> %r"), retval)
        return retval

    def check_output(self, *args, **kwargs):
        _logger.debug("check_output(%r, %r)",  args, kwargs)
        args, kwargs = self._translate_ssh_call(args, kwargs)
        _logger.debug(_("check_output(...) translated to %r, %r"),
                      args, kwargs)
        retval = subprocess.check_output(*args, **kwargs)
        _logger.debug(_("check_output(...) -> %r"), retval)
        return retval

    def check_call(self, *args, **kwargs):
        _logger.debug("check_call(%r, %r)",  args, kwargs)
        args, kwargs = self._translate_ssh_call(args, kwargs)
        _logger.debug(_("check_call(...) translated to %r, %r"), args, kwargs)
        return subprocess.check_call(*args, **kwargs)

    # FileSystem API

    def read(self, filename: str) -> bytes:
        _logger.debug("read(%r)", filename)
        with tempfile.TemporaryDirectory() as tempdir:
            local_filename = os.path.join(tempdir, 'file-to-read')
            self.pull(filename, local_filename)
            with open(local_filename, 'rb') as stream:
                data = stream.read()
                _logger.debug("read(...) -> %r", data)
                return data

    def write(self, filename: str, data: bytes) -> int:
        _logger.debug("write(%r, <data size %d>)", filename, len(data))
        with tempfile.TemporaryDirectory() as tempdir:
            local_filename = os.path.join(tempdir, 'file-to-write')
            with open(local_filename, 'wb') as stream:
                num_written = stream.write(data)
                _logger.debug("write(...) wrote %s bytes", num_written)
            self.push(local_filename, filename)
            return num_written

    def remove(self, filename: str):
        _logger.debug("remove(%r)", filename)
        self._run_sftp_cmd(['rm', filename])

    def symlink(self, name: str, target: str) -> None:
        _logger.debug("symlink(%r, %r)", name, target)
        self._run_sftp_cmd(['ln', '-s', target, name])

    def listdir(self, dirname: str) -> list:
        _logger.debug("listdir(%r)", dirname)
        return [self._parse_sftp_ls_l(line)
                for line in self._run_sftp_cmd(['ls', '-l', dirname])]

    def exists(self, pathname: str) -> bool:
        _logger.debug("exists(%r) -> ...", pathname)
        dirname, filename = os.path.split(pathname)
        try:
            result = any(info.name == filename
                         for info in self.listdir(dirname))
        except FileSystemOperationError:
            result = False
        _logger.debug("exists(%r) -> %r", pathname, result)
        return result

    def isdir(self, pathname: str) -> bool:
        _logger.debug("isdir(%r) -> ...", pathname)
        result = self._is_type(pathname, IFileSystemAPI.TYPE_DIRECTORY)
        _logger.debug("isdir(%r) -> %r", pathname, result)
        return result

    def isfile(self, pathname: str) -> bool:
        _logger.debug("isfile(%r) -> ...", pathname)
        result = self._is_type(pathname, IFileSystemAPI.TYPE_FILE)
        _logger.debug("isfile(%r) -> %r", pathname, result)
        return result

    def islink(self, pathname: str) -> bool:
        _logger.debug("islink(%r) -> ...", pathname)
        result = self._is_type(pathname, IFileSystemAPI.TYPE_SYMLINK)
        _logger.debug("islink(%r) -> %r", pathname, result)
        return result

    def mkdir(self, dirname: str) -> None:
        _logger.debug("mkdir(%r)", dirname)
        self._run_sftp_cmd(['mkdir', dirname])

    def rmdir(self, dirname: str) -> None:
        _logger.debug("rmdir(%r)", dirname)
        self._run_sftp_cmd(['rmdir', dirname])

    def push(self, local_path: str, remote_path: str) -> None:
        _logger.debug("push(%r, %r)", local_path, remote_path)
        self._run_sftp_cmd(['put', local_path, remote_path])

    def pull(self, remote_path: str, local_path: str) -> None:
        _logger.debug("pull(%r, %r)", remote_path, local_path)
        self._run_sftp_cmd(['get', remote_path, local_path])

    # OperatingSystem API

    @property
    def abi_cookie(self) -> str:
        return "&".join(
            '{}={}'.format(key, value)
            for key, value in sorted(self.os_metadata.items()))

    @property
    def os_metadata(self) -> dict:
        if self._os_metadata is None:
            self._os_metadata = self._probe_os_metadata()
        return self._os_metadata

    # ProviderConsumer API

    def push_provider(self, provider):
        self._provider_list.append(
            RemoteProvider1.from_local_provider(provider, self))

    def get_execution_controller_list(self) -> 'List[IExecutionController]':
        return [
            RemoteExecutionController(self, self, self._provider_list)
        ]

    # Private implementation details

    def _run_sftp_cmd(self, cmd_list) -> 'List[str]':
        """
        Run a sftp(1) command

        :param cmd_list:
            An interactive sftp command to run
        :returns:
            A list of lines printed by sftp, except for the first line which
            echoes the command itself.
        :raises FileSystemOperationError:
            If the sftp command fails
        :raises subprocess.CalledProcessError:
            If the sftp command fails
        """
        # NOTE: This method has fairly high overhead. It would be much better
        # if the sftp process monitoring was moved somewhere else and we had
        # used one process (one sftp bootstrap cost) for all operations.
        _logger.debug("Running SFTP command: %r", cmd_list)
        args = (['sftp', '-v', '-b', '-'] + self._master.ssh_options
                + [self._master.netloc])
        sftp_cmd = ' '.join(cmd_list).encode('UTF-8')
        _logger.debug(_("SFTP command translated to: %r"), ' '.join(args))
        proc = subprocess.Popen(args, stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        stdout, stderr = proc.communicate(input=sftp_cmd)
        if proc.returncode != 0:
            _logger.debug("SFTP command failed: %r", sftp_cmd)
            _logger.debug("SFTP stdout\n%s", stdout.decode("UTF-8", "replace"))
            _logger.debug("SFTP stderr\n%s", stderr.decode("UTF-8", "replace"))
            raise FileSystemOperationError(
                cmd_list[0], cmd_list[1:], "SFTP command failed")
        return stdout.decode("UTF-8").splitlines()[1:]

    def _translate_ssh_call(self, args, kwargs) -> 'Tuple[tuple, dict]':
        """
        Identify and remove the subprocess.Popen(args, ..)

        :param args:
            Positional argument list as if passed to subprocess.Popen(*args)
        :param kwargs:
            Keyword argument list as if passed to subprocess.Popen(**kwargs)
        :returns:
            A pair (args, kwargs) after translation
        :raises ValueError:
            If the first argument is not available
        """
        args = list(args)
        kwargs = dict(kwargs)
        if len(args) >= 1:
            remote_args = args.pop(0)
        elif 'args' in kwargs:
            remote_args = kwargs.pop('args')
        else:
            raise ValueError("unable to infer command line argument")
        # Combine common_args and remote_args
        args.insert(
            0, ['ssh'] + self._master.ssh_options + [self._master.netloc, '--']
            + remote_args)
        return tuple(args), kwargs

    def _probe_os_metadata(self):
        return probe_os(self)

    def _parse_sftp_ls_l(self, line):
        # NOTE: A typical sftp 'ls -l' output looks like this:
        #
        # drwxr-xr-x    4 zyga     zyga         4096 Mar 26  2014 Documents
        #
        # The fields are, in order:
        # 0: type and permissions, aka mode
        # 1: number of hard links
        # 2: user name
        # 3: group name
        # 4: size
        # 5: modification month
        # 6: modification day
        # 7: modification hour OR year?!?!
        # 8: name (including files with spaces)
        #
        # Hence we need to use maxsplit=9 to get at most nine fields
        field_list = re.split(' +', line, 9)
        entry_name = field_list[8]
        entry_type = self._ls_dash_l_lookup_map.get(
            field_list[0][0], IFileSystemAPI.TYPE_UNKNOWN)
        return listdir_info(entry_name, entry_type)

    _ls_dash_l_lookup_map = {
        '-': IFileSystemAPI.TYPE_FILE,
        'b': IFileSystemAPI.TYPE_BLOCK_DEVICE,
        'c': IFileSystemAPI.TYPE_CHARACTER_DEVICE,
        'd': IFileSystemAPI.TYPE_DIRECTORY,
        'l': IFileSystemAPI.TYPE_SYMLINK,
        'p': IFileSystemAPI.TYPE_NAMED_PIPE,
        's': IFileSystemAPI.TYPE_SOCKET,
    }

    def _is_type(self, pathname: str, type: str) -> bool:
        dirname, filename = os.path.split(pathname)
        try:
            return any((info.name == filename
                        and info.type == type)
                       for info in self.listdir(dirname))
        except FileSystemOperationError:
            return False
