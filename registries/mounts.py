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
from checkbox.lib.cache import cache
from checkbox.lib.conversion import string_to_type

from checkbox.properties import Path
from checkbox.registries.filename import FilenameRegistry
from checkbox.registries.map import MapRegistry


class MountsRegistry(FilenameRegistry):
    """Registry for mounts information.

    Each item contained in this registry consists information about
    the mount point.
    """

    # Filename where mounts arel stored.
    filename = Path(default="/proc/mounts")

    @cache
    def items(self):
        keys = ["file_system", "mount_point", "type", "options", "dump", "pass"]
        items = []
        for line in [l for l in self.split("\n") if l]:
            values = [string_to_type(v) for v in line.split(" ")]
            map = dict(zip(keys, values))
            map["options"] = map["options"].split(",")
            value = MapRegistry(map)
            items.append((map["mount_point"], value))

        return items


factory = MountsRegistry
