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
import posixpath

from checkbox.properties import Path
from checkbox.registries.directory import RecursiveDirectoryRegistry
from checkbox.registries.filename import FilenameRegistry

class ModprobeRegistry(RecursiveDirectoryRegistry):
    """Registry for files contained in /etc/modprobe.d."""

    directory = Path(default="/etc/modprobe.d")

    def items(self):
        items = []
        for file in self.split("\n"):
            filename = posixpath.join(str(self.directory), file)
            info = FilenameRegistry(filename)
            info.filename = filename
            key = len(items)
            items.append((key, info))

        return items


factory = ModprobeRegistry
