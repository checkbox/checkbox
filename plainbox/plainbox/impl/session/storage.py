# This file is part of Checkbox.
#
# Copyright 2012, 2013 Canonical Ltd.
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
:mod:`plainbox.impl.session.storage` -- storage for sessions
============================================================

This module contains storage support code for handling sessions. Using the
:class:`SessionStorageRepository` one can enumerate sessions at a particular
location. Each location is wrapped by a :class:`SessionStorage` instance. That
latter class be used to create (allocate) and remove all of the files
associated with a particular session.
"""

import errno
import logging
import os
import shutil
import stat
import sys
import tempfile

from plainbox.i18n import gettext as _, ngettext

logger = logging.getLogger("plainbox.session.storage")


class SessionStorageRepository:
    """
    Helper class to enumerate filesystem artefacts of current or past Sessions

    This class collaborates with :class:`SessionStorage`. The basic
    use-case is to open a well-known location and enumerate all the sessions
    that are stored there. This allows to create :class:`SessionStorage`
    instances to further manage each session (such as remove them by calling
    :meth:SessionStorage.remove()`)
    """

    _LAST_SESSION_SYMLINK = "last-session"

    def __init__(self, location=None):
        """
        Initialize new repository at the specified location.

        The location does not have to be an existing directory. It will be
        created on demand. Typically it should be instantiated with the default
        location.
        """
        if location is None:
            location = self.get_default_location()
        self._location = location

    @property
    def location(self):
        """
        pathname of the repository
        """
        return self._location

    def get_last_storage(self):
        """
        Find the last session storage object created in this repository.

        :returns:
            SessionStorage object associated with the last session created in
            this repository using legacy mode.

        .. note::
            This will only return storage objects that were created using
            legacy mode. Nonlegacy storage objects will not be returned this
            way.
        """
        pathname = os.path.join(self.location, self._LAST_SESSION_SYMLINK)
        try:
            last_storage = os.readlink(pathname)
        except OSError:
            # The symlink can be gone or not be a real symlink
            # in that case just ignore it and return None
            return None
        else:
            # The link may be relative so let's ensure we know the full
            # pathname for the subsequent check (which may be performed
            # from another directory)
            last_storage = os.path.join(self._location, last_storage)
        # If the link points to a directory, assume it's okay
        if os.path.isdir(last_storage):
            return SessionStorage(last_storage)

    def get_storage_list(self):
        """
        Enumerate stored sessions in the repository.

        If the repository directory is not present then an empty list is
        returned.

        :returns:
            list of :class:`SessionStorage` representing discovered sessions
        """
        logger.debug(_("Enumerating sessions in %s"), self._location)
        try:
            # Try to enumerate the directory
            item_list = os.listdir(self._location)
        except OSError as exc:
            # If the directory does not exist,
            # silently return empty collection
            if exc.errno == errno.ENOENT:
                return []
            # Don't silence any other errors
            raise
        session_list = []
        # Check each item by looking for directories
        for item in item_list:
            pathname = os.path.join(self.location, item)
            # Make sure not to follow any symlinks here
            stat_result = os.lstat(pathname)
            # Consider non-hidden directories that end with the word .session
            if (not item.startswith(".") and item.endswith(".session")
                    and stat.S_ISDIR(stat_result.st_mode)):
                logger.debug(_("Found possible session in %r"), pathname)
                session = SessionStorage(pathname)
                session_list.append(session)
        # Return the full list
        return session_list

    def __iter__(self):
        """
        Same as :meth:`get_storage_list()`
        """
        return iter(self.get_storage_list())

    @classmethod
    def get_default_location(cls):
        """
        Get the default location of the session state repository

        The default location is defined by ``$PLAINBOX_SESSION_REPOSITORY``
        which must be a writable directory (created if needed) where plainbox
        will keep its session data. The default location, if the environment
        variable is not provided, is
        ``${XDG_CACHE_HOME:-$HOME/.cache}/plainbox/sessions``
        """
        repo_dir = os.environ.get('PLAINBOX_SESSION_REPOSITORY')
        if repo_dir is not None:
            repo_dir = os.path.abspath(repo_dir)
        else:
            # Pick XDG_CACHE_HOME from environment
            xdg_cache_home = os.environ.get('XDG_CACHE_HOME')
            # If not set or empty use the default ~/.cache/
            if not xdg_cache_home:
                xdg_cache_home = os.path.join(
                    os.path.expanduser('~'), '.cache')
            # Use a directory relative to XDG_CACHE_HOME
            repo_dir = os.path.join(xdg_cache_home, 'plainbox', 'sessions')
        if (repo_dir is not None and os.path.exists(repo_dir)
                and not os.path.isdir(repo_dir)):
            logger.warning(
                _("Session repository %s it not a directory"), repo_dir)
            repo_dir = None
        if (repo_dir is not None and os.path.exists(repo_dir)
                and not os.access(repo_dir, os.W_OK)):
            logger.warning(
                _("Session repository %s is read-only"), repo_dir)
            repo_dir = None
        if repo_dir is None:
            repo_dir = tempfile.mkdtemp()
            logger.warning(
                _("Using temporary directory %s as session repository"),
                repo_dir)
        return repo_dir


class LockedStorageError(IOError):
    """
    Exception raised when SessionStorage.save_checkpoint() finds an existing
    'next' file from a (presumably) previous call to save_checkpoint() that
    got interrupted
    """


class SessionStorage:
    """
    Abstraction for storage area that is used by :class:`SessionState` to
    keep some persistent and volatile data.

    This class implements functions performing input/output operations
    on session checkpoint data. The location property can be used for keeping
    any additional files or directories but keep in mind that they will
    be removed by :meth:`SessionStorage.remove()`

    This class indirectly collaborates with :class:`SessionSuspendHelper` and
    :class:`SessionResumeHelper`.
    """

    _SESSION_FILE = 'session'

    _SESSION_FILE_NEXT = 'session.next'

    def __init__(self, location):
        """
        Initialize a :class:`SessionStorage` with the given location.

        The location is not created. If you want to ensure that it exists
        call :meth:`create()` instead.
        """
        self._location = location

    def __repr__(self):
        return "<{} location:{!r}>".format(
            self.__class__.__name__, self.location)

    @property
    def location(self):
        """
        location of the session storage
        """
        return self._location

    @property
    def id(self):
        """
        identifier of the session storage (name of the random directory)
        """
        return os.path.splitext(os.path.basename(self.location))[0]

    @property
    def session_file(self):
        """
        pathname of the session state file
        """
        return os.path.join(self._location, self._SESSION_FILE)

    @classmethod
    def create(cls, base_dir, legacy_mode=False):
        """
        Create a new :class:`SessionStorage` in a random subdirectory
        of the specified base directory. The base directory is also
        created if necessary.

        :param base_dir:
            Directory in which a random session directory will be created.
            Typically the base directory should be obtained from
            :meth:`SessionStorageRepository.get_default_location()`

        :param legacy_mode:
            If False (defaults to True) then the caller is expected to
            handle multiple sessions by itself.

        .. note::
            Legacy mode is where applications using PlainBox API can only
            handle one session. Creating another session replaces whatever was
            stored before. In non-legacy mode applications can enumerate
            sessions, create arbitrary number of sessions at the same time
            and remove sessions once they are no longer necessary.

            Legacy mode is implemented with a symbolic link called
            'last-session' that keeps track of the last session created using
            ``legacy_mode=True``. When a new legacy-mode session is created
            the target of that symlink is read and recursively removed.
        """
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        location = tempfile.mkdtemp(
            prefix='pbox-', suffix='.session', dir=base_dir)
        logger.debug(_("Created new storage in %r"), location)
        self = cls(location)
        if legacy_mode:
            self._replace_legacy_session(base_dir)
        return self

    def _replace_legacy_session(self, base_dir):
        """
        Remove the previous legacy session and update the 'last-session'
        symlink so that it points to this session storage directory.
        """
        symlink_pathname = os.path.join(
            base_dir, SessionStorageRepository._LAST_SESSION_SYMLINK)
        # Try to read and remove the storage referenced to by last-session
        # symlink. This can fail if the link file is gone (which is harmless)
        # or when it is not an actual symlink (which means that the
        # repository is corrupted).
        try:
            symlink_target = os.readlink(symlink_pathname)
        except OSError as exc:
            if exc.errno == errno.ENOENT:
                pass
            elif exc.errno == errno.EINVAL:
                logger.warning(
                    _("%r is not a symlink, repository %r must be corrupted"),
                    symlink_pathname, base_dir)
            else:
                logger.warning(
                    _("Unable to read symlink target from %r: %r"),
                    symlink_pathname, exc)
        else:
            logger.debug(
                _("Removing storage associated with last session %r"),
                symlink_target)
            # Remove the old session, note that the symlink may be broken so
            # let's ignore any errors here
            shutil.rmtree(symlink_target, ignore_errors=True)
            # Remove the last-session symlink itself
            logger.debug(
                _("Removing symlink associated with last session: %r"),
                symlink_pathname)
            os.unlink(symlink_pathname)
        finally:
            # Finally put the last-session synlink that points to this storage
            logger.debug(
                _("Linking storage %r to last session"), self.location)
            try:
                os.symlink(self.location, symlink_pathname)
            except OSError as exc:
                logger.error(
                    _("Cannot link %r as %r: %r"),
                    self.location, symlink_pathname, exc)

    def remove(self):
        """
        Remove all filesystem entries associated with this instance.
        """
        logger.debug(_("Removing session storage from %r"), self._location)
        shutil.rmtree(self._location)

    def load_checkpoint(self):
        """
        Load checkpoint data from the filesystem

        :returns: data from the most recent checkpoint
        :rtype: bytes

        :raises IOError, OSError:
            on various problems related to accessing the filesystem

        :raises NotImplementedError:
            when openat(2) is not available on this platform. Should never
            happen on Linux or Windows where appropriate checks divert to a
            correct implementation that is not using them.
        """
        if sys.platform == 'linux' or sys.platform == 'linux2':
            if sys.version_info[0:2] >= (3, 3):
                return self._load_checkpoint_unix_py33()
            else:
                return self._load_checkpoint_unix_py32()
        elif sys.platform == 'win32':
            return self._load_checkpoint_win32_py33()
        raise NotImplementedError(
            "platform/python combination is not supported: {} + {}".format(
                sys.version, sys.platform))

    def save_checkpoint(self, data):
        """
        Save checkpoint data to the filesystem.

        The directory associated with this :class:`SessionStorage` must already
        exist. Typically the instance should be obtained by calling
        :meth:`SessionStorage.create()` which will ensure that this is already
        the case.

        :raises TypeError:
            if data is not a bytes object.

        :raises LockedStorageError:
            if leftovers from previous save_checkpoint() have been detected.
            Normally those should never be here but in certain cases that is
            possible. Callers might want to call :meth:`break_lock()`
            to resolve the problem and try again.

        :raises IOError, OSError:
            on various problems related to accessing the filesystem.
            Typically permission errors may be reported here.

        :raises NotImplementedError:
            when openat(2), renameat(2), unlinkat(2) are not available on this
            platform. Should never happen on Linux or Windows where appropriate
            checks divert to a correct implementation that is not using them.
        """
        if sys.platform == 'linux' or sys.platform == 'linux2':
            if sys.version_info[0:2] >= (3, 3):
                return self._save_checkpoint_unix_py33(data)
            else:
                return self._save_checkpoint_unix_py32(data)
        elif sys.platform == 'win32':
            if sys.version_info[0:2] >= (3, 3):
                return self._save_checkpoint_win32_py33(data)
        raise NotImplementedError(
            "platform/python combination is not supported: {} + {}".format(
                sys.version, sys.platform))

    def break_lock(self):
        """
        Forcibly unlock the storage by removing a file created during
        atomic filesystem operations of save_checkpoint().

        This method might be useful if save_checkpoint()
        raises LockedStorageError. It removes the "next" file that is used
        for atomic rename.
        """
        _next_session_pathname = os.path.join(
            self._location, self._SESSION_FILE_NEXT)
        logger.debug(
            # TRANSLATORS: unlinking as in deleting a file
            # Please keep the 'next' string untranslated
            _("Forcibly unlinking 'next' file %r"), _next_session_pathname)
        os.unlink(_next_session_pathname)

    def _load_checkpoint_win32_py33(self):
        logger.debug(_("Loading checkpoint (%s)"), "Windows")
        _session_pathname = os.path.join(self._location, self._SESSION_FILE)
        try:
            # Open the current session file in the location directory
            session_fd = os.open(_session_pathname, os.O_RDONLY | os.O_BINARY)
            logger.debug(
                _("Opened session state file %r as descriptor %d"),
                _session_pathname, session_fd)
            # Stat the file to know how much to read
            session_stat = os.fstat(session_fd)
            logger.debug(
                # TRANSLATORS: stat is a system call name, don't translate it
                _("Stat'ed session state file: %s"), session_stat)
            try:
                # Read session data
                logger.debug(ngettext(
                    "Reading %d byte of session state",
                    "Reading %d bytes of session state",
                    session_stat.st_size), session_stat.st_size)
                data = os.read(session_fd, session_stat.st_size)
                logger.debug(ngettext(
                    "Read %d byte of session state",
                    "Read %d bytes of session state", len(data)), len(data))
                if len(data) != session_stat.st_size:
                    raise IOError(_("partial read?"))
            finally:
                # Close the session file
                logger.debug(_("Closed descriptor %d"), session_fd)
                os.close(session_fd)
        except IOError as exc:
            if exc.errno == errno.ENOENT:
                # Treat lack of 'session' file as an empty file
                return b''
            raise
        else:
            return data

    def _load_checkpoint_unix_py32(self):
        _session_pathname = os.path.join(self._location, self._SESSION_FILE)
        # Open the location directory
        location_fd = os.open(self._location, os.O_DIRECTORY)
        logger.debug(
            _("Opened session directory %r as descriptor %d"),
            self._location, location_fd)
        try:
            # Open the current session file in the location directory
            session_fd = os.open(_session_pathname, os.O_RDONLY)
            logger.debug(
                _("Opened session state file %r as descriptor %d"),
                _session_pathname, session_fd)
            # Stat the file to know how much to read
            session_stat = os.fstat(session_fd)
            logger.debug(
                # TRANSLATORS: stat is a system call name, don't translate it
                _("Stat'ed session state file: %s"), session_stat)
            try:
                # Read session data
                logger.debug(ngettext(
                    "Reading %d byte of session state",
                    "Reading %d bytes of session state",
                    session_stat.st_size), session_stat.st_size)
                data = os.read(session_fd, session_stat.st_size)
                logger.debug(ngettext(
                    "Read %d byte of session state",
                    "Read %d bytes of session state", len(data)), len(data))
                if len(data) != session_stat.st_size:
                    raise IOError(_("partial read?"))
            finally:
                # Close the session file
                logger.debug(_("Closed descriptor %d"), session_fd)
                os.close(session_fd)
        except IOError as exc:
            if exc.errno == errno.ENOENT:
                # Treat lack of 'session' file as an empty file
                return b''
            raise
        else:
            return data
        finally:
            # Close the location directory
            logger.debug(_("Closed descriptor %d"), location_fd)
            os.close(location_fd)

    def _load_checkpoint_unix_py33(self):
        # Open the location directory
        location_fd = os.open(self._location, os.O_DIRECTORY)
        try:
            # Open the current session file in the location directory
            session_fd = os.open(
                self._SESSION_FILE, os.O_RDONLY, dir_fd=location_fd)
            # Stat the file to know how much to read
            session_stat = os.fstat(session_fd)
            try:
                # Read session data
                data = os.read(session_fd, session_stat.st_size)
                if len(data) != session_stat.st_size:
                    raise IOError(_("partial read?"))
            finally:
                # Close the session file
                os.close(session_fd)
        except IOError as exc:
            if exc.errno == errno.ENOENT:
                # Treat lack of 'session' file as an empty file
                return b''
            raise
        else:
            return data
        finally:
            # Close the location directory
            os.close(location_fd)

    def _save_checkpoint_win32_py33(self, data):
        # NOTE: this is like _save_checkpoint_py32 but without location_fd
        # wich cannot be opened on windows (no os.O_DIRECTORY)
        #
        # NOTE: The windows version is relatively new and under-tested
        # but then again we don't expect to run tests *on* windows, only
        # *from* windows so hard data retention requirements are of lesser
        # importance.
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")
        logger.debug(ngettext(
            "Saving %d byte of data (%s)",
            "Saving %d bytes of data (%s)",
            len(data)), len(data), "Windows")
        # Helper pathnames, needed because we don't have *at functions
        _next_session_pathname = os.path.join(
            self._location, self._SESSION_FILE_NEXT)
        _session_pathname = os.path.join(self._location, self._SESSION_FILE)
        # Open the "next" file in the location_directory
        #
        # Use "write" + "create" + "exclusive" flags so that no race
        # condition is possible.
        #
        # This will never return -1, it throws IOError when anything is
        # wrong. The caller has to catch this.
        #
        # As a special exception, this code handles EEXISTS and converts
        # that to LockedStorageError that can be especially handled by
        # some layer above.
        try:
            next_session_fd = os.open(
                _next_session_pathname,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_BINARY, 0o644)
        except IOError as exc:
            if exc.errno == errno.EEXISTS:
                raise LockedStorageError()
            else:
                raise
        logger.debug(
            _("Opened next session file %s as descriptor %d"),
            _next_session_pathname, next_session_fd)
        try:
            # Write session data to disk
            #
            # I cannot find conclusive evidence but it seems that
            # os.write() handles partial writes internally. In case we do
            # get a partial write _or_ we run out of disk space, raise an
            # explicit IOError.
            num_written = os.write(next_session_fd, data)
            logger.debug(ngettext(
                "Wrote %d byte of data to descriptor %d",
                "Wrote %d bytes of data to descriptor %d",
                num_written), num_written, next_session_fd)
            if num_written != len(data):
                raise IOError(_("partial write?"))
        except Exception as exc:
            logger.warning(_("Unable to complete write: %s"), exc)
            # If anything goes wrong we should unlink the next file.
            # TRANSLATORS: unlinking as in deleting a file
            logger.warning(_("Unlinking %r: %r"), _next_session_pathname, exc)
            os.unlink(_next_session_pathname)
        else:
            # If the write was successful we must flush kernel buffers.
            #
            # We want to be sure this data is really on disk by now as we
            # may crash the machine soon after this method exits.
            logger.debug(
                # TRANSLATORS: please don't translate fsync()
                _("Calling fsync() on descriptor %d"), next_session_fd)
            try:
                os.fsync(next_session_fd)
            except OSError as exc:
                logger.warning(_("Cannot synchronize file %r: %s"),
                               _next_session_pathname, exc)
        finally:
            # Close the new session file
            logger.debug(_("Closing descriptor %d"), next_session_fd)
            os.close(next_session_fd)
        # Rename FILE_NEXT over FILE.
        logger.debug(_("Renaming %r to %r"),
                     _next_session_pathname, _session_pathname)
        try:
            os.replace(_next_session_pathname, _session_pathname)
        except Exception as exc:
            # Same as above, if we fail we need to unlink the next file
            # otherwise any other attempts will not be able to open() it
            # with O_EXCL flag.
            logger.warning(
                _("Unable to rename/overwrite %r to %r: %r"),
                _next_session_pathname, _session_pathname, exc)
            # TRANSLATORS: unlinking as in deleting a file
            logger.warning(_("Unlinking %r"), _next_session_pathname)
            os.unlink(_next_session_pathname)

    def _save_checkpoint_unix_py32(self, data):
        # NOTE: this is like _save_checkpoint_py33 but without all the
        # *at() functions (openat, renameat)
        #
        # Since we cannot use those functions there is an implicit race
        # condition on all open() calls with another process that renames
        # any of the directories that are part of the opened path.
        #
        # I don't think we can really do anything about this in userspace
        # so this, python 3.2 specific version, just does the best effort
        # implementation. Some of the comments were redacted but
        # but keep in mind that the rename race is always there.
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")
        logger.debug(ngettext(
            "Saving %d byte of data (%s)",
            "Saving %d bytes of data (%s)",
            len(data)), len(data), "UNIX, python 3.2 or older")
        # Helper pathnames, needed because we don't have *at functions
        _next_session_pathname = os.path.join(
            self._location, self._SESSION_FILE_NEXT)
        _session_pathname = os.path.join(self._location, self._SESSION_FILE)
        # Open the location directory, we need to fsync that later
        # XXX: this may fail, maybe we should keep the fd open all the time?
        location_fd = os.open(self._location, os.O_DIRECTORY)
        logger.debug(
            _("Opened %r as descriptor %d"), self._location, location_fd)
        try:
            # Open the "next" file in the location_directory
            #
            # Use "write" + "create" + "exclusive" flags so that no race
            # condition is possible.
            #
            # This will never return -1, it throws IOError when anything is
            # wrong. The caller has to catch this.
            #
            # As a special exception, this code handles EEXISTS and converts
            # that to LockedStorageError that can be especially handled by
            # some layer above.
            try:
                next_session_fd = os.open(
                    _next_session_pathname,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
            except IOError as exc:
                if exc.errno == errno.EEXISTS:
                    raise LockedStorageError()
                else:
                    raise
            logger.debug(
                _("Opened next session file %s as descriptor %d"),
                _next_session_pathname, next_session_fd)
            try:
                # Write session data to disk
                #
                # I cannot find conclusive evidence but it seems that
                # os.write() handles partial writes internally. In case we do
                # get a partial write _or_ we run out of disk space, raise an
                # explicit IOError.
                num_written = os.write(next_session_fd, data)
                logger.debug(ngettext(
                    "Wrote %d byte of data to descriptor %d",
                    "Wrote %d bytes of data to descriptor %d",
                    num_written), num_written, next_session_fd)
                if num_written != len(data):
                    raise IOError(_("partial write?"))
            except Exception as exc:
                logger.warning(_("Unable to complete write: %r"), exc)
                # If anything goes wrong we should unlink the next file.
                # TRANSLATORS: unlinking as in deleting a file
                logger.warning(_("Unlinking %r"), _next_session_pathname)
                os.unlink(_next_session_pathname)
            else:
                # If the write was successful we must flush kernel buffers.
                #
                # We want to be sure this data is really on disk by now as we
                # may crash the machine soon after this method exits.
                logger.debug(
                    # TRANSLATORS: please don't translate fsync()
                    _("Calling fsync() on descriptor %d"), next_session_fd)
                try:
                    os.fsync(next_session_fd)
                except OSError as exc:
                    logger.warning(_("Cannot synchronize file %r: %s"),
                                   _next_session_pathname, exc)
            finally:
                # Close the new session file
                logger.debug(_("Closing descriptor %d"), next_session_fd)
                os.close(next_session_fd)
            # Rename FILE_NEXT over FILE.
            logger.debug(_("Renaming %r to %r"),
                         _next_session_pathname, _session_pathname)
            try:
                os.rename(_next_session_pathname, _session_pathname)
            except Exception as exc:
                # Same as above, if we fail we need to unlink the next file
                # otherwise any other attempts will not be able to open() it
                # with O_EXCL flag.
                logger.warning(
                    _("Unable to rename/overwrite %r to %r: %r"),
                    _next_session_pathname, _session_pathname, exc)
                # Same as above, if we fail we need to unlink the next file
                # otherwise any other attempts will not be able to open() it
                # with O_EXCL flag.
                # TRANSLATORS: unlinking as in deleting a file
                logger.warning(_("Unlinking %r"), _next_session_pathname)
                os.unlink(_next_session_pathname)
            # Flush kernel buffers on the directory.
            #
            # This should ensure the rename operation is really on disk by now.
            # As noted above, this is essential for being able to survive
            # system crash immediately after exiting this method.

            # TRANSLATORS: please don't translate fsync()
            logger.debug(_("Calling fsync() on descriptor %d"), location_fd)
            try:
                os.fsync(location_fd)
            except OSError as exc:
                logger.warning(_("Cannot synchronize directory %r: %s"),
                               self._location, exc)
        finally:
            # Close the location directory
            logger.debug(_("Closing descriptor %d"), location_fd)
            os.close(location_fd)

    def _save_checkpoint_unix_py33(self, data):
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")
        logger.debug(ngettext(
            "Saving %d byte of data (%s)",
            "Saving %d bytes of data (%s)",
            len(data)), len(data), "UNIX, python 3.3 or newer")
        # Open the location directory, we need to fsync that later
        # XXX: this may fail, maybe we should keep the fd open all the time?
        location_fd = os.open(self._location, os.O_DIRECTORY)
        logger.debug(
            _("Opened %r as descriptor %d"), self._location, location_fd)
        try:
            # Open the "next" file in the location_directory
            #
            # Use openat(2) to ensure we always open a file relative to the
            # directory we already opened above. This is essential for fsync(2)
            # calls made below.
            #
            # Use "write" + "create" + "exclusive" flags so that no race
            # condition is possible.
            #
            # This will never return -1, it throws IOError when anything is
            # wrong. The caller has to catch this.
            #
            # As a special exception, this code handles EEXISTS
            # (FIleExistsError) and converts that to LockedStorageError
            # that can be especially handled by some layer above.
            try:
                next_session_fd = os.open(
                    self._SESSION_FILE_NEXT,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644,
                    dir_fd=location_fd)
            except FileExistsError:
                raise LockedStorageError()
            logger.debug(
                _("Opened next session file %s as descriptor %d"),
                self._SESSION_FILE_NEXT, next_session_fd)
            try:
                # Write session data to disk
                #
                # I cannot find conclusive evidence but it seems that
                # os.write() handles partial writes internally. In case we do
                # get a partial write _or_ we run out of disk space, raise an
                # explicit IOError.
                num_written = os.write(next_session_fd, data)
                logger.debug(ngettext(
                    "Wrote %d byte of data to descriptor %d",
                    "Wrote %d bytes of data to descriptor %d", num_written),
                    num_written, next_session_fd)
                if num_written != len(data):
                    raise IOError(_("partial write?"))
            except Exception as exc:
                logger.warning(_("Unable to complete write: %r"), exc)
                # If anything goes wrong we should unlink the next file. As
                # with the open() call above we use unlinkat to prevent race
                # conditions.
                # TRANSLATORS: unlinking as in deleting a file
                logger.warning(_("Unlinking %r"), self._SESSION_FILE_NEXT)
                os.unlink(self._SESSION_FILE_NEXT, dir_fd=location_fd)
            else:
                # If the write was successful we must flush kernel buffers.
                #
                # We want to be sure this data is really on disk by now as we
                # may crash the machine soon after this method exits.
                logger.debug(
                    # TRANSLATORS: please don't translate fsync()
                    _("Calling fsync() on descriptor %d"), next_session_fd)
                try:
                    os.fsync(next_session_fd)
                except OSError as exc:
                    logger.warning(_("Cannot synchronize file %r: %s"),
                                   self._SESSION_FILE_NEXT, exc)
            finally:
                # Close the new session file
                logger.debug(_("Closing descriptor %d"), next_session_fd)
                os.close(next_session_fd)
            # Rename FILE_NEXT over FILE.
            #
            # Use renameat(2) to ensure that there is no race condition if the
            # location (directory) is being moved
            logger.debug(
                _("Renaming %r to %r"),
                self._SESSION_FILE_NEXT, self._SESSION_FILE)
            try:
                os.rename(self._SESSION_FILE_NEXT, self._SESSION_FILE,
                          src_dir_fd=location_fd, dst_dir_fd=location_fd)
            except Exception as exc:
                # Same as above, if we fail we need to unlink the next file
                # otherwise any other attempts will not be able to open() it
                # with O_EXCL flag.
                logger.warning(
                    _("Unable to rename/overwrite %r to %r: %r"),
                    self._SESSION_FILE_NEXT, self._SESSION_FILE, exc)
                # TRANSLATORS: unlinking as in deleting a file
                logger.warning(_("Unlinking %r"), self._SESSION_FILE_NEXT)
                os.unlink(self._SESSION_FILE_NEXT, dir_fd=location_fd)
            # Flush kernel buffers on the directory.
            #
            # This should ensure the rename operation is really on disk by now.
            # As noted above, this is essential for being able to survive
            # system crash immediately after exiting this method.

            # TRANSLATORS: please don't translate fsync()
            logger.debug(_("Calling fsync() on descriptor %d"), location_fd)
            try:
                os.fsync(location_fd)
            except OSError as exc:
                logger.warning(_("Cannot synchronize directory %r: %s"),
                               self._location, exc)
        finally:
            # Close the location directory
            logger.debug(_("Closing descriptor %d"), location_fd)
            os.close(location_fd)
