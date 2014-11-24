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
:mod:`plainbox.impl.connection.common` -- common code
=====================================================
"""
from subprocess import CalledProcessError
import collections
import logging
import os
import shlex
import uuid

from plainbox.abc import IConnection
from plainbox.abc import IExecutionController
from plainbox.abc import IProvider1
from plainbox.abc import IProviderBackend1
from plainbox.errors import DeviceOperationError
from plainbox.errors import FileSystemOperationError
from plainbox.errors import ProcessOperationError
from plainbox.errors import UnsupportedDeviceAPI
from plainbox.i18n import gettext as _
from plainbox.impl.decorators import raises
from plainbox.impl.signal import Signal
from plainbox.impl.unit.file import FileRole
from plainbox.impl.unit.job import JobDefinition

__all__ = [
    'RemoteExecutionController',
    'RemoteProvider1',
    'listdir_info',
    'probe_os',
]


_logger = logging.getLogger("plainbox.connection.common")


listdir_info = collections.namedtuple('listdir_info', 'name type')


class RemoteProvider1(IProvider1, IProviderBackend1):

    def __init__(self, local_provider, fs_api, base_dir, role_subdirs,
                 made_dirs, made_files):
        self._local_provider = local_provider
        self._fs_api = fs_api
        self._base_dir = base_dir
        self._role_subdirs = role_subdirs
        self._made_dirs = made_dirs
        self._made_files = made_files
        self._closed = False

    def __repr__(self):
        if self.is_closed:
            return "<{} closed>".format(self.__class__.__name__)
        else:
            return "<{} local_provider:{!r} base_dir:{!r}>".format(
                self.__class__.__name__, self._local_provider,
                self._base_dir)

    def close(self):
        if not self._closed:
            _logger.debug(_("Closing (removing) remote provider %r"), self)
            for filename in self._made_files:
                self._fs_api.remove(filename)
            for dirname in sorted(self._made_dirs, reverse=True):
                self._fs_api.rmdir(dirname)
            self._closed = True

    @property
    def is_closed(self):
        return self._closed

    @classmethod
    def from_local_provider(cls, local_provider, fs_api):
        base_dir = '/tmp/plainbox-{}'.format(uuid.uuid1())
        role_subdirs = {}
        made_dirs = set()
        made_files = set()

        def mkdir_p(dirname):
            _logger.debug("mkdir -p %r", dirname)
            _logger.debug("Checking if full dirname exits: %r", dirname)
            if not fs_api.isdir(dirname):
                _logger.debug("%s doesn't exit", dirname)
                head, tail = os.path.split(dirname)
                _logger.debug("mkdir_p %r -> %r %r", dirname, head, tail)
                _logger.debug("Checking if head exists: %r", head)
                if not fs_api.isdir(head):
                    _logger.debug("%s doesn't exit", head)
                    _logger.debug("Going to make head: %r", head)
                    mkdir_p(head)
                _logger.debug("Creating directory: %r", dirname)
                fs_api.mkdir(dirname)
                made_dirs.add(dirname)
        try:
            assert base_dir not in made_dirs
            mkdir_p(base_dir)
            for unit in local_provider._unit_list:
                if unit.Meta.name != 'file':
                    continue
                if not unit.is_needed_remotely:
                    continue
                if unit.role not in role_subdirs:
                    role_subdirs[unit.role] = unit.natural_subdirectory
                filename = os.path.join(
                    base_dir, unit.natural_subdirectory,
                    os.path.relpath(unit.path, unit.base))
                dirname = os.path.dirname(filename)
                if dirname not in made_dirs:
                    mkdir_p(dirname)
                assert filename not in made_files
                _logger.debug("Copying file: %r -> %r", unit.path, filename)
                fs_api.push(unit.path, filename)
                made_files.add(filename)
        except Exception:
            for filename in made_files:
                fs_api.remove(filename)
            for dirname in sorted(made_dirs, reverse=True):
                fs_api.rmdir(dirname)
            raise
        else:
            return cls(local_provider, fs_api, base_dir, role_subdirs,
                       made_dirs, made_files)

    @property
    def name(self):
        return self._local_provider.name

    @property
    def namespace(self):
        return self._local_provider.namespace

    @property
    def version(self):
        return self._local_provider.version

    @property
    def description(self):
        return self._local_provider.description

    def tr_description(self):
        return self._local_provider.tr_description()

    @property
    def units_dir(self):
        if FileRole.unit_source in self._role_subdirs:
            return os.path.join(
                self._base_dir, self._role_subdirs[FileRole.unit_source])

    @property
    def data_dir(self):
        if FileRole.data in self._role_subdirs:
            return os.path.join(
                self._base_dir, self._role_subdirs[FileRole.data])

    @property
    def bin_dir(self):
        if (FileRole.script in self._role_subdirs
                or FileRole.binary in self._role_subdirs):
            return os.path.join(
                self._base_dir, (
                    self._role_subdirs.get(FileRole.script) or
                    self._role_subdirs[FileRole.binary]))

    @property
    def locale_dir(self):
        return None

    @property
    def base_dir(self):
        return self._base_dir

    @property
    def build_bin_dir(self):
        return None

    @property
    def src_dir(self):
        return None

    @property
    def CHECKBOX_SHARE(self):
        return self.base_dir

    @property
    def extra_PYTHONPATH(self):
        return None

    @property
    def secure(self):
        return False

    @property
    def gettext_domain(self):
        return self._local_provider.gettext_domain

    def get_units(self):
        return self._local_provider.get_units()

    def get_translated_data(self, msgid):
        return self._local_provider.get_translated_data(msgid)

    def get_builtin_jobs(self):
        raise NotImplementedError()

    def get_builtin_whitelists(self):
        raise NotImplementedError()

    @property
    def jobs_dir(self):
        raise NotImplementedError()

    def load_all_jobs(self):
        raise NotImplementedError()

    def whitelists_dir(self):
        raise NotImplementedError()


class RemoteExecutionController(IExecutionController):

    def __init__(self, proc_api, fs_api, remote_provider_list):
        self._proc_api = proc_api
        self._fs_api = fs_api
        self._remote_provider_list = remote_provider_list

    def execute_job(self, job, config, session_dir, extcmd_popen):
        for remote_provider in self._remote_provider_list:
            if job.id in remote_provider._local_provider._id_map:
                break
        else:
            assert False, "no remote provider?"
        args, kwargs = self._proc_api.translate_cmd([
            'PATH={}:/sbin:/bin:/usr/sbin:/usr/bin'.format(
                ':'.join(rp.bin_dir for rp in self._remote_provider_list
                         if rp.bin_dir is not None)),
            'PLAINBOX_PROVIDER_DATA={}'.format(remote_provider.data_dir),
            'PLAINBOX_PROVIDER_UNITS={}'.format(remote_provider.units_dir),
            job.shell, '-c', shlex.quote(job.command)])
        _logger.debug("SSH command: %r", args)
        return extcmd_popen.call(*args, **kwargs)

    @Signal.define
    def on_leftover_files(self, job, config, cwd_dir, leftovers):
        pass

    def get_score(self, job):
        if isinstance(job, JobDefinition):
            return 1

    def get_warm_up_for_job(self, job):
        pass


class AbstractConnection(IConnection):

    def __init__(self, url):
        self._url = url

    @property
    def url(self):
        return self._url

    @raises(UnsupportedDeviceAPI)
    def api(self, name: str) -> object:
        api_map = self.api_map
        if name in api_map:
            return api_map[name]
        else:
            raise UnsupportedDeviceAPI(name)

    def close(self):
        pass

    def __enter__(self) -> IConnection:
        return self

    def __exit__(self, *args):
        self.close()


@raises(UnsupportedDeviceAPI, DeviceOperationError)
def probe_os(conn: IConnection) -> dict:
    """
    Probe a device and determine operating system meta-data

    :param conn:
        A connected IConnection object
    :returns:
        A dictionary with collected meta-data. This meta-data is modelled after
        the /etc/os-release file but it also includes other features. See below
        for details.
    :raises UnsupportedDeviceAPI:
        If a required API is unavailable. In practice the connection is
        expected to support both the process execution API and the filesystem
        API.
    :raises DeviceOperationError:
        If some sort of unexpected device operation fails. Some operation
        errors are handled internally but this can still happen and should
        be handled by the caller.

    This function is capable of detecting modern (2014-era) Linux
    distributions. At least Ubuntu, Debian, Fedora, Red Hat and SUSE were
    successfully probed during development.

    In addition, a few non-Linux systems were probed, though just for fun as
    we're not supporting that.  Probing capability depends on the set of APIs
    supported by the probed conn.

    The returned meta-data dictionary may have the following keys:

    ``os``:
        Lower-case name of the operating system. Typically this is 'linux'.
    ``id``:
        Identifier of the operating system name (or vendor)
    ``version_id``:
        Version of the operating system, specific to ``id``
    ``arch``:
        Processor architecture name
    ``name``:
        Human readable version of "id + version_id"

    .. note::
        This function never "fails", at the very least it will return::
            {"os": "unknown"}.
    """
    try:
        uname_s = get_oneline_cmd(conn, ['uname', '-s'])
    except ProcessOperationError:
        # If we have no uname maybe we're looking at windows?
        if conn.api(IConnection.API_FILE_SYSTEM).isdir('C:\\'):
            _logger.debug("It's a Windows box!")
            return probe_windows(conn)
        raise
    else:
        if uname_s == 'Linux':
            _logger.debug("It's a Linux box!")
            return probe_linux(conn)
        elif uname_s.endswith == 'BSD' or uname_s == 'Darwin':
            _logger.debug("It's a BSD or Darwin box!")
            return probe_bsd(conn, uname_s)
        else:
            _logger.warning(_("Probing OS %r is unsupported"), uname_s)
            return {'os': 'unknown'}


@raises(UnsupportedDeviceAPI)
def probe_linux(conn: IConnection) -> dict:
    """
    Probe a system running Linux.

    :param conn:
        Device conn object that is connected to a machine running Linux
    :returns:
        Dictionary with device meta-data
    :raises UnsupportedDeviceAPI:
        If the conn doesn't support the file system and process APIs

    This function uses ``uname(1)``, ``os-release(5)`` or ``lsb_release(1)`` to
    figure out where it is currently running on. It should work on all 2014-era
    distributions.

    Typical return values are:
        {'os': 'linux', 'id': 'debian', 'version_id': '7', 'arch': 'amd64'}
        {'os': 'linux', 'id': 'ubuntu', 'version_id': '14.04', 'arch': 'amd64'}
        {'os': 'linux', 'id': 'ubuntu', 'version_id': '14.09', 'arch': 'amd64'}
        {'os': 'linux', 'id': 'fedora', 'version_id': '20', 'arch': 'x86_64'}
    """
    # Try to probe the basics in one of few supported ways
    for probe_fn in (probe_linux_via_os_release, probe_linux_via_lsb_release):
        metadata = probe_fn(conn)
        if metadata is not None:
            break
    else:
        metadata = {
            'os': 'linux',
            'id': 'unknown',
        }
    # Try to get the CPU architecture
    try:
        metadata['arch'] = get_oneline_cmd(conn, ['uname', '-m'])
    except ProcessOperationError:
        _logger.warning(_("unable to probe processor architecture"))
        pass
    # Try to get the machine specific identifier
    try:
        metadata['machine_id'] = get_machine_id(conn)
    except FileSystemOperationError:
        pass  # It's okay not to have it, it's pretty recent
    except ValueError as exc:
        _logger.warning(_("/etc/machine-id is corrupted: %r"), exc)
    # Return all that we have got thus far
    return metadata


@raises(UnsupportedDeviceAPI)
def probe_linux_via_lsb_release(conn: IConnection) -> dict:
    for name in 'lsb', 'fedora', 'debian', 'openwrt':
        filename = '/etc/{}-release'.format(name)
        try:
            lsb_release = get_key_value_file(conn, name)
        except FileSystemOperationError:
            continue
        except (UnicodeDecodeError, ValueError) as exc:
            _logger.warning("%s is corrupted: %r", exc)
        else:
            _logger.info(_("Using %s to identify Linux-based OS"), filename)
            return {
                'os': 'linux',
                'id': lsb_release.get("DISTRIB_ID", "Linux").lower(),
                'version_id': lsb_release.get(
                    "DISTRIB_RELEASE", "").lower(),
                'name': lsb_release.get("DISTRIB_DESCRIPTION", ""),
            }


@raises(UnsupportedDeviceAPI)
def probe_linux_via_os_release(conn: IConnection) -> dict:
    try:
        os_release = get_key_value_file(conn, '/etc/os-release')
    except FileSystemOperationError:
        return None
    except (UnicodeDecodeError, ValueError) as exc:
        _logger.warning("/etc/os-release is corrupted: %r", exc)
    else:
        return {
            'os': 'linux',
            'id': os_release.get("ID").lower(),
            'version_id': os_release.get("VERSION_ID", ""),
            'name': os_release.get("PRETTY_NAME", ""),
        }


@raises(UnsupportedDeviceAPI)
def probe_windows(conn: IConnection) -> dict:
    """
    Probe a system running Microsoft Windows.

    :param conn:
        Device conn object that is connected to a machine running Windows
    :raises UnsupportedDeviceAPI:
        If the process API is unavailable.
    :returns:
        Dictionary with device meta-data
    """
    metadata = {
        'os': 'windows',
        'id': 'windows',
    }
    # Try to access os.Version
    try:
        metadata['version_id'] = get_oneline_cmd(
            conn, ['wmic', 'os', 'get', 'Version', '//value']
        ).split('=', 1)[1]
    except ProcessOperationError as exc:
        _logger.warning(_("Unable to access WMI %r: %r"), 'os.Version', exc)
    except (UnicodeDecodeError, ValueError) as exc:
        _logger.warning(_("Corrupted output from wmic: %r"), exc)
    # Try to access os.OSArchitecture
    try:
        metadata['arch'] = get_oneline_cmd(
            conn, ['wmic', 'os', 'get', 'OSArchitecture', '//value']
        ).split('=', 1)[1]
    except ProcessOperationError as exc:
        _logger.warning(
            _("Unable to access WMI %r: %r"), 'os.OSArchitecture', exc)
    except (UnicodeDecodeError, ValueError) as exc:
        _logger.warning(_("Corrupted output from wmic: %r"), exc)
    # Try to access os.Caption
    try:
        metadata['name'] = get_oneline_cmd(
            conn, ['wmic', 'os', 'get', 'Caption', '//value']
        ).split('=', 1)[1],
    except ProcessOperationError as exc:
        _logger.warning(_("Unable to access WMI %r: %r"), 'Caption', exc)
    except (UnicodeDecodeError, ValueError) as exc:
        _logger.warning(_("Corrupted output from wmic: %r"), exc)
    # Return whatever we got
    return metadata


@raises(UnsupportedDeviceAPI)
def probe_bsd(conn: IConnection, uname_s: str=None) -> dict:
    """
    Probe a system running {Free,Open,Net,*}BSD or Darwin (OS X).

    :param conn:
        Device conn object that is connected to a machine running some variant
        of BSD
    :param uname_s:
        The "cleaned up" version of ``uname -s`` (as text, without newlines).
        This field is optional. If it is left out an identical query is made
        via the process API
    :returns:
        Dictionary with device meta-data
    :raises UnsupportedDeviceAPI:
        If the process API is unavailable.

    .. note::
        This was briefly tested against OpenBDS 5.5 running on amd64
    """
    if uname_s is None:
        uname_s = get_oneline_cmd(conn, ['uname', '-s'])
    return {
        'os': uname_s,
        'id': uname_s,
        'version_id': get_oneline_cmd(conn, ['uname', '-r']),
        'arch': get_oneline_cmd(conn, ['uname', '-m'])
    }


@raises(UnsupportedDeviceAPI, ProcessOperationError, UnicodeDecodeError,
        CalledProcessError)
def get_oneline_cmd(conn: IConnection, cmd: 'List[str]',
                    encoding: str='UTF-8') -> str:
    """
    Run a command that returns a single line of output

    :param conn:
        The conn to use. It must support the process API
    :param cmd:
        The command to run.
    :param encoding:
        The (optional, defaulting to UTF-8) encoding to use to interpret the
        output.
    :returns:
        The output of the command
    :raises UnsupportedDeviceAPI:
        If the conn doesn't support the process API
    :raises ProcessOperationError:
        If we have issues running the remote process
    :raises UnicodeDecodeError:
        If we have issues interpreting the output bytes
    :raises CalledProcessError:
        If we run the remote process but it exits with a non-zero exit code
    """
    proc_api = conn.api(IConnection.API_PROCESS)
    output = proc_api.check_output(cmd)
    return output.decode(encoding).strip()


@raises(UnsupportedDeviceAPI, FileSystemOperationError, UnicodeDecodeError,
        ValueError)
def get_key_value_file(conn: IConnection, path) -> dict:
    """
    Read and parse shell-source-able

    :param conn:
        The conn to use. It must support the file system API
    :param path:
        Name of the file to load
    :returns:
        A dictionary with parsed data
    :raises UnsupportedDeviceAPI:
        If the conn doesn't support the file system API
    :raises FileSystemOperationError:
        If we have issues accessing remote files
    :raises UnicodeDecodeError:
        If we have issues interpreting the bytes as text
    :raises ValueError:
        If we have problems with parsing the text
    """
    fs_api = conn.api(IConnection.API_FILE_SYSTEM)
    text = fs_api.read(path)
    text = text.decode("UTF-8")
    return {
        key: value
        for key, value in (
            entry.split('=', 1) for entry in shlex.split(text)
        )
    }


@raises(UnsupportedDeviceAPI, FileSystemOperationError, UnicodeDecodeError)
def get_machine_id(conn: IConnection, path: str='/etc/machine-id') -> str:
    """
    Read and parse ``machine-id(5)`` file

    :param conn:
        The conn to use. It must support the file system API
    :raises UnsupportedDeviceAPI:
        If the conn doesn't support the file system API
    :raises FileSystemOperationError:
        If we have issues accessing remote files
    :raises UnicodeDecodeError:
        If we have issues interpreting the bytes as text
    :raises ValueError:
        If the machine identifier is not a 32 byte long hexadecimal string
    """
    fs_api = conn.api(IConnection.API_FILE_SYSTEM)
    text = fs_api.read(path)
    text = text.decode("ASCII")
    machine_id = text.strip()
    if len(machine_id) != 32:
        raise ValueError(_("Truncated machine-id"))
    return machine_id
