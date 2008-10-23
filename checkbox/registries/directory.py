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
import os
import logging

from checkbox.registry import Registry


class DirectoryRegistry(Registry):
    """Base registry for containing directories.

    The default behavior is to return the files within a directory
    separated by newlines.

    Subclasses should define a directory configuration parameter.
    """

    optional_attributes = ["directory"]

    def __init__(self, config, directory=None):
        super(DirectoryRegistry, self).__init__(config)
        self._directory = directory or self._config.directory

    def __str__(self):
        logging.info("Reading directory: %s", self._directory)
        return "\n".join(os.listdir(self._directory))

    def items(self):
        return []
