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

class SysctlRegistry(RecursiveDirectoryRegistry):
    """Registry for files contained in /etc/modprobe.d."""

    directory = Path(default="/etc/sysctl.d")
    filename = Path(default="/etc/sysctl.conf")

    def items(self):
        items = []

        # Convert filenames to full paths
        files = [posixpath.join(str(self.directory), f) for f in 
            self.split("\n")]

        # Special case for sysctl.conf
        files.insert(0, self.filename)

        for file in files:
            info = FilenameRegistry(file)
            info.filename = file
            items.append(info)

        return items


factory = SysctlRegistry
