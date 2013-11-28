#
# This file is part of Checkbox.
#
# Copyright 2011 Canonical Ltd.
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
#
import os
import errno
import select

from checkbox.lib.enum import Enum


__all__ = ["SelectorIO", "SelectorState", "Selector"]


SelectorIO = Enum(
    "READ",
    "WRITE",
    "EXCEPT")

SelectorState = Enum(
    "VIRGIN",
    "READY",
    "TIMED_OUT",
    "SIGNALED",
    "FAILED")


class Selector:
    __slots__ = ("_read_fds", "_write_fds", "_except_fds",
        "_save_read_fds", "_save_write_fds", "_save_except_fds",
        "_fd_set_size", "_timeout", "_state", "_errno")

    _fd_select_size = -1
    _cached_read_fds = None
    _cached_save_read_fds = None
    _cached_write_fds = None
    _cached_save_write_fds = None
    _cached_except_fds = None
    _cached_save_except_fds = None

    def __init__(self):
        if Selector._cached_read_fds:
            self._read_fds = Selector._cached_read_fds
            self._write_fds = Selector._cached_write_fds
            self._except_fds = Selector._cached_except_fds

            self._save_read_fds = Selector._cached_save_read_fds
            self._save_write_fds = Selector._cached_save_write_fds
            self._save_except_fds = Selector._cached_save_except_fds

            Selector._cached_read_fds = None
            Selector._cached_write_fds = None
            Selector._cached_except_fds = None

            Selector._cached_save_read_fds = None
            Selector._cached_save_write_fds = None
            Selector._cached_save_except_fds = None

        else:
            self._read_fds = []
            self._write_fds = []
            self._except_fds = []

            self._save_read_fds = []
            self._save_write_fds = []
            self._save_except_fds = []

        self.reset()

    def __del__(self):
        if Selector._cached_read_fds is None:
            Selector._cached_read_fds = self._read_fds
            Selector._cached_write_fds = self._write_fds
            Selector._cached_except_fds = self._except_fds

            Selector._cached_save_read_fds = self._save_read_fds
            Selector._cached_save_write_fds = self._save_write_fds
            Selector._cached_save_except_fds = self._save_except_fds

    def reset(self):
        self._errno = 0
        self._state = SelectorState.VIRGIN
        self._timeout = None
        self._save_read_fds = []
        self._save_write_fds = []
        self._save_except_fds = []

    @staticmethod
    def get_fd_select_size():
        if Selector._fd_select_size == -1:
            try:
                Selector._fd_select_size = os.sysconf("SC_OPEN_MAX")
            except (AttributeError, ValueError):
                Selector._fd_select_size = 1024

        return Selector._fd_select_size

    def get_errno(self):
        return self._errno

    def get_errstr(self):
        return os.strerror(self._errno)

    def set_timeout(self, timeout):
        self._timeout = timeout

    def unset_timeout(self):
        self._timeout = None

    def has_timed_out(self):
        return self._state == SelectorState.TIMED_OUT

    def has_signaled(self):
        return self._state == SelectorState.SIGNALED

    def has_failed(self):
        return self._state == SelectorState.FAILED

    def has_ready(self):
        return self._state == SelectorState.READY

    def add_fd(self, fd, interest):
        if fd < 0 or fd >= Selector.get_fd_select_size():
            raise Exception("File descriptor %d outside of range 0-%d"
                % (fd, Selector._fd_select_size))

        if interest == SelectorIO.READ:
            self._save_read_fds.append(fd)

        elif interest == SelectorIO.WRITE:
            self._save_write_fds.append(fd)

        elif interest == SelectorIO.EXCEPT:
            self._save_except_fds.append(fd)

    def remove_fd(self, fd, interest):
        if fd < 0 or fd >= Selector.get_fd_select_size():
            raise Exception("File descriptor %d outside of range 0-%d"
                % (fd, Selector._fd_select_size))

        if interest == SelectorIO.READ:
            self._save_read_fds.remove(fd)

        elif interest == SelectorIO.WRITE:
            self._save_write_fds.remove(fd)

        elif interest == SelectorIO.EXCEPT:
            self._save_except_fds.remove(fd)

    def execute(self):
        try:
            self._read_fds, self._write_fds, self._except_fds = select.select(
                self._save_read_fds, self._save_write_fds,
                self._save_except_fds, self._timeout)
        except select.error as e:
            self._errno = e.errno
            if e.errno == errno.EINTR:
                self._state = SelectorState.SIGNALED

            else:
                self._state = SelectorState.FAILED

            return

        # Just in case
        self._errno = 0
        if not self._read_fds \
           and not self._write_fds \
           and not self._except_fds:
            self._state = SelectorState.TIMED_OUT

        else:
            self._state = SelectorState.READY

    def is_fd_ready(self, fd, interest):
        if self._state != SelectorState.READY \
           and self._state != SelectorState.TIMED_OUT:
            raise Exception(
                "Selector requested descriptor not in ready state")

        if fd < 0 or fd >= Selector.get_fd_select_size():
            return False

        if interest == SelectorIO.READ:
            return fd in self._read_fds

        elif interest == SelectorIO.WRITE:
            return fd in self._write_fds

        elif interest == SelectorIO.EXCEPT:
            return fd in self._except_fds

        return False
