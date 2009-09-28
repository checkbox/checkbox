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
import re

from checkbox.lib.cache import cache
from checkbox.lib.conversion import string_to_type

from checkbox.properties import Path
from checkbox.registries.filename import FilenameRegistry


class MeminfoRegistry(FilenameRegistry):
    """Registry for memory information.

    Each item contained in this registry consists of the information
    in the /proc/meminfo file.
    """

    # Filename where meminfo is stored.
    filename = Path(default="/proc/meminfo")

    @cache
    def items(self):
        meminfo = {}
        for line in self.split("\n"):
            match = re.match(r"(.*):\s+(.*)", line)
            if match:
                key = match.group(1)
                value = string_to_type(match.group(2))
                meminfo[key] = value

        meminfo_to_items = (
            ("MemTotal", "total"),
            ("SwapTotal", "swap"))

        items = []
        for mkey, ikey in meminfo_to_items:
            value = meminfo[mkey]
            items.append((ikey, value))

        return items


factory = MeminfoRegistry
