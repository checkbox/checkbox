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
import logging

from checkbox.properties import Path
from checkbox.registry import Registry


class FilenameRegistry(Registry):
    """Base registry for containing files.

    The default behavior is to return the content of the file.

    Subclasses should define a filename parameter.
    """

    filename = Path()

    def __init__(self, filename=None):
        super(FilenameRegistry, self).__init__()
        if filename is not None:
            self.filename = filename

    def __str__(self):
        logging.info("Reading filename: %s", self.filename)
        return open(self.filename, "r").read()

    def items(self):
        return []
