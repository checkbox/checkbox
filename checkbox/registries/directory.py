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
import logging

from checkbox.properties import Path
from checkbox.registry import Registry


class DirectoryRegistry(Registry):
    """Base registry for containing directories.

    The default behavior is to return the files within a directory
    separated by newlines.

    Subclasses should define a directory parameter.
    """

    directory = Path()

    def __init__(self, directory=None):
        super(DirectoryRegistry, self).__init__()
        if directory is not None:
            self.directory = directory

    def __str__(self):
        logging.info("Reading directory: %s", self.directory)
        return "\n".join(os.listdir(self.directory))

    def items(self):
        return []


class RecursiveDirectoryRegistry(DirectoryRegistry):
    """Variant of the DirectoryRegistry that recurses into subdirectories."""

    def __str__(self):
        logging.info("Reading directory: %s", self.directory)
        return "\n".join(self._listdir(self.directory))

    def _listdir(self, root, path=""):
        files = []
        try:
            for file in os.listdir(os.path.join(root, path)):
                pathname = os.path.join(path, file)
                if os.path.isdir(os.path.join(root, pathname)):
                    files.extend(self._listdir(root, pathname))
                else:
                    files.append(pathname)
        except OSError:
            pass
        return files
