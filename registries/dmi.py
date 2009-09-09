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
import posixpath

from checkbox.lib.cache import cache

from checkbox.properties import String
from checkbox.registries.command import CommandRegistry


class DmiRegistry(CommandRegistry):
    """Registry for dmi information."""

    # Command to retrieve dmi information.
    command = String(default="grep -r . /sys/class/dmi/id/ 2>/dev/null || true")

    @cache
    def items(self):
        items = []
        for line in str(self).split("\n"):
            if not line:
                continue

            path, value = line.split(":", 1)
            key = posixpath.basename(path)
            items.append((key, value))

        return items
 

factory = DmiRegistry
