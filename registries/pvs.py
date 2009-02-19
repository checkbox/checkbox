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

from checkbox.properties import String
from checkbox.registries.command import CommandRegistry
from checkbox.registries.map import MapRegistry


class PvsRegistry(CommandRegistry):
    """Registry for pvs information.

    Each item contained in this registry consists information about
    the mount point.
    """

    # Command to retrieve physical volume information
    command = String(default="pvs")

    # User to run pvs command
    user = String(default="root")

    @cache
    def items(self):
        items = []
        lines = [l.strip() for l in self.split("\n") if l]
        if lines:
            keys_line = lines.pop(0)
            keys = [k.lower() for k in re.split(r"\s+", keys_line)]

            for line in lines:
                values = [string_to_type(v) for v in re.split(r"\s+", line)]
                map = dict(zip(keys, values))
                value = MapRegistry(map)
                items.append((map["pv"], value))

        return items


factory = PvsRegistry
