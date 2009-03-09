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
import posixpath
import shutil

from stat import ST_MODE, S_IMODE, S_ISFIFO


def safe_change_mode(path, mode):
    if not posixpath.exists(path):
        raise Exception, "Path does not exist: %s" % path

    old_mode = os.stat(path)[ST_MODE]
    if mode != S_IMODE(old_mode):
        os.chmod(path, mode)

def safe_make_directory(path, mode=0755):
    if posixpath.exists(path):
        if not posixpath.isdir(path):
            raise Exception, "Path is not a directory: %s" % path
    else:
        os.makedirs(path, mode)

def safe_make_fifo(path, mode=0666):
    if posixpath.exists(path):
        mode = os.stat(path)[ST_MODE]
        if not S_ISFIFO(mode):
            raise Exception, "Path is not a FIFO: %s" % path
    else:
        os.mkfifo(path, mode)

def safe_remove_directory(path):
    if posixpath.exists(path):
        if not posixpath.isdir(path):
            raise Exception, "Path is not a directory: %s" % path

        shutil.rmtree(path)

def safe_remove_file(path):
    if posixpath.exists(path):
        if not posixpath.isfile(path):
            raise Exception, "Path is not a file: %s" % path

        os.remove(path)

def safe_rename(old, new):
    if old != new:
        if not posixpath.exists(old):
            raise Exception, "Old path does not exist: %s" % old
        if posixpath.exists(new):
            raise Exception, "New path exists already: %s" % new

        os.rename(old, new)

def safe_md5sum():
    try:
        import hashlib
        digest = hashlib.md5()
    except ImportError:
        # for Python << 2.5
        import md5
        digest = md5.new()

    return digest

def safe_md5sum_file(name):
    md5sum = None
    if posixpath.exists(name):
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
