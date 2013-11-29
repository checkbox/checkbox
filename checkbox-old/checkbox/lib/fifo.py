#
# This file is part of Checkbox.
#
# Copyright 2010 Canonical Ltd.
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
import struct
import logging

from checkbox.contrib.bpickle import dumps, loads
from checkbox.lib.selector import Selector, SelectorIO


class FifoBase:

    flags = None

    def __init__(self, path, timeout=None):
        self.path = path
        self.fileno = os.open(path, self.flags)
        self._timeout = timeout

    def __del__(self):
        self.close()

    def close(self):
        try:
            os.close(self.fileno)
        except OSError as e:
            logging.warning("Problem closing the fifo")
            logging.warning(e)

    def wait_for(self, operation):
        if self._timeout is not None:
            selector = Selector()
            selector.set_timeout(self._timeout)
            selector.add_fd(self.fileno, operation)

            selector.execute()

            if not selector.has_ready():
                return False
        return True


class FifoReader(FifoBase):

    flags = os.O_RDWR

    def read_bytes(self):
        # Check if a connection arrived within the timeout
        if not self.wait_for(SelectorIO.READ):
            return None

        size = struct.calcsize("i")
        length_bytes = os.read(self.fileno, size)
        if not length_bytes:
            return b""

        length = struct.unpack(">i", length_bytes)[0]
        return os.read(self.fileno, length)

    def read_object(self):
        _bytes = self.read_bytes()
        if not _bytes:
            return None

        return loads(_bytes)


class FifoWriter(FifoBase):

    flags = os.O_RDWR | os.O_CREAT | os.O_TRUNC

    def write_bytes(self, _bytes):

        # Wait until I can write
        if not self.wait_for(SelectorIO.WRITE):
            return None

        length = len(_bytes)
        length_bytes = struct.pack(">i", length)
        os.write(self.fileno, length_bytes)
        os.write(self.fileno, _bytes)
        return length

    def write_object(self, object):
        _bytes = dumps(object)
        return self.write_bytes(_bytes)


def create_fifo(path, mode=0o666):
    os.mkfifo(path, mode)
    return path
