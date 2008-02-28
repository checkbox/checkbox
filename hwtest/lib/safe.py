#
# Copyright (c) 2008 Canonical
#
# Written by Marc Tardif <marc@interunion.ca>
#
# This file is part of HWTest.
#
# HWTest is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HWTest is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HWTest.  If not, see <http://www.gnu.org/licenses/>.
#
import os


def safe_make_directory(path, mode=0777):
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise Exception, "Path is not a directory: %s" % path

        os.chmod(path, mode)
    else:
        os.makedirs(path, mode)

def safe_remove_directory(path):
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise Exception, "Path is not a directory: %s" % path

        os.removedirs(path)

def safe_remove_file(path):
    if os.path.exists(path):
        if not os.path.isfile(path):
            raise Exception, "Path is not a file: %s" % path

        os.remove(path)
