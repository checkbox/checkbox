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
from checkbox.lib.cache import cache
from checkbox.lib.conversion import string_to_type

from checkbox.registries.file import FileRegistry
from checkbox.registries.map import MapRegistry


class MtabRegistry(FileRegistry):
    """Registry for mtab information.

    Each item contained in this registry consists information about
    the mount point.
    """

    @cache
    def items(self):
        keys = ["file_system", "mount_point", "type", "options", "dump", "pass"]
        items = []
        for line in [l for l in self.split("\n") if l]:
            values = [string_to_type(v) for v in line.split(" ")]
            map = dict(zip(keys, values))
            value = MapRegistry(None, map)
            items.append((map["mount_point"], value))

        return items


factory = MtabRegistry
