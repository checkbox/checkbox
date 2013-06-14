#
# This file is part of Checkbox.
#
# Copyright 2008 Canonical Ltd.
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
import hashlib
import shutil

from stat import ST_MODE, S_IMODE, S_ISFIFO


def safe_change_mode(path, mode):
    if not os.path.exists(path):
        raise Exception("Path does not exist: %s" % path)

    old_mode = os.stat(path)[ST_MODE]
    if mode != S_IMODE(old_mode):
        os.chmod(path, mode)

def safe_make_directory(path, mode=0o755):
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise Exception("Path is not a directory: %s" % path)
    else:
        os.makedirs(path, mode)

def safe_make_fifo(path, mode=0o666):
    if os.path.exists(path):
        mode = os.stat(path)[ST_MODE]
        if not S_ISFIFO(mode):
            raise Exception("Path is not a FIFO: %s" % path)
    else:
        os.mkfifo(path, mode)

def safe_remove_directory(path):
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise Exception("Path is not a directory: %s" % path)

        shutil.rmtree(path)

def safe_remove_file(path):
    if os.path.exists(path):
        if not os.path.isfile(path):
            raise Exception("Path is not a file: %s" % path)

        os.remove(path)

def safe_rename(old, new):
    if old != new:
        if not os.path.exists(old):
            raise Exception("Old path does not exist: %s" % old)
        if os.path.exists(new):
            raise Exception("New path exists already: %s" % new)

        os.rename(old, new)

class safe_md5sum:

    def __init__(self):
        self.digest = hashlib.md5()
        self.hexdigest = self.digest.hexdigest

    def update(self, string):
        self.digest.update(string.encode("utf-8"))

def safe_md5sum_file(name):
    md5sum = None
    if os.path.exists(name):
        file = open(name)
        digest = safe_md5sum()
        while 1:
            buf = file.read(4096)
            if buf == "":
                break
            digest.update(buf)
        file.close()
        md5sum = digest.hexdigest()

    return md5sum

def safe_close(file, safe=True):
    if safe:
        file.flush()
        os.fsync(file.fileno())
    file.close()
