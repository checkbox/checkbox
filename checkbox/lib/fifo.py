#
# This file is part of Checkbox.
#
# Copyright 2010 Canonical Ltd.
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
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

from checkbox.contrib.bpickle import dumps, loads
from checkbox.lib.selector import Selector, SelectorIO

class FifoBase:

    mode = None

    def __init__(self, path, timeout=None):
        self.path = path
        self.file = open(path, self.mode)
        self._timeout = timeout

    def __del__(self):
        self.close()

    def close(self):
        self.file.close()

    def wait_for(self, operation):
        if self._timeout is not None:
            selector = Selector()
            selector.set_timeout(self._timeout)
            selector.add_fd(self.file.fileno(), operation)

            selector.execute()

            if not selector.has_ready():
                return False
        return True

class FifoReader(FifoBase):

    #on Linux, opening a FIFO in read-write mode is non-blocking and
    #succeeds even if other end is not open as per FIFO(7)
    mode = "w+"

    def read_string(self):
        # Check if a connection arrived within the timeout
        if not self.wait_for(SelectorIO.READ):
            return None

        size = struct.calcsize("i")
        length_string = self.file.read(size)
        if not length_string:
            return ""

        length = struct.unpack(">i", length_string)[0]
        return self.file.read(length)

    def read_object(self):
        string = self.read_string()
        if not string:
            return None

        return loads(string)


class FifoWriter(FifoBase):

    #on Linux, opening a FIFO in read-write mode is non-blocking and
    #succeeds even if other end is not open as per FIFO(7)
    mode = "w+"

    def write_string(self, string):

        # Wait until I can write 
        if not self.wait_for(SelectorIO.WRITE):
            return None 

        length = len(string)
        length_string = struct.pack(">i", length)
        self.file.write(length_string)
        self.file.write(string)
        self.file.flush()
        return length

    def write_object(self, object):
        string = dumps(object)
        return self.write_string(string)


def create_fifo(path, mode=0o666):
    os.mkfifo(path, mode)
    return path
