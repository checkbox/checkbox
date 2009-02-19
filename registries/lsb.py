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

from checkbox.properties import String
from checkbox.registries.command import CommandRegistry


class LsbRegistry(CommandRegistry):
    """Registry for LSB information.

    Each item contained in this registry consists of the information
    returned by the lsb_release command.
    """

    # Command to retrieve LSB information.
    command = String(default="lsb_release -a 2>/dev/null")

    default_map = {
        "Distributor ID": "distributor_id",
        "Description": "description",
        "Release": "release",
        "Codename": "codename"}

    def __init__(self, filename=None, map=None):
        super(LsbRegistry, self).__init__(filename)
        self._map = map or self.default_map

    @cache
    def items(self):
        items = []
        for line in [l for l in self.split("\n") if l]:
            (key, value) = line.split(":\t", 1)
            if key in self._map:
                key = self._map[key]
                items.append((key, value))

        return items


factory = LsbRegistry
