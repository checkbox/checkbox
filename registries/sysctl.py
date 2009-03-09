#
# This file is part of Checkbox.
#
# Copyright 2009 Canonical Ltd.
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
import posixpath

from checkbox.lib.path import path_expand

from checkbox.properties import Path
from checkbox.registry import Registry
from checkbox.registries.directory import RecursiveDirectoryRegistry
from checkbox.registries.filename import FilenameRegistry


class SysctlRegistry(Registry):
    """Registry for files contained in /etc/modprobe.d."""

    path = Path(default="/etc/sysctl.*")

    def items(self):
        items = []

        paths = path_expand(self.path)
        for path in paths:
            key = posixpath.basename(path)
            if posixpath.isfile(path):
                value = FilenameRegistry(path)
            elif posixpath.isdir(path):
                value = RecursiveDirectoryRegistry(path)
            else:
                logging.info("Unknown sysctl path: %s", path)
                continue

            items.append((key, value))

        return items


factory = SysctlRegistry
