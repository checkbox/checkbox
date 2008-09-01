#
# Copyright (c) 2008 Canonical
#
# Written by Marc Tardif <marc@interunion.ca>
#
# This file is part of Checkbox.
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

from checkbox.registry import Registry


class FileRegistry(Registry):
    """Base registry for containing files.

    The default behavior is to return the content of the file.

    Subclasses should define a filename configuration parameter.
    """

    optional_attributes = ["filename"]

    def __init__(self, config, filename=None):
        super(FileRegistry, self).__init__(config)
        self.filename = filename or self.config.filename

    def __str__(self):
        logging.info("Reading filename: %s", self.filename)
        return open(self.filename, "r").read()

    def items(self):
        return []
