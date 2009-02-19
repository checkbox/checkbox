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
import types

from checkbox.lib.cache import cache
from checkbox.registry import Registry


class MapRegistry(Registry):
    """Registry for maps.

    The default behavior is to express the given maps as a tree of items.
    """

    def __init__(self, map={}):
        super(MapRegistry, self).__init__()
        self._map = map

    def __str__(self):
        strings = ["%s: %s" % (k, v) for k, v in self._map.items()]

        return "\n".join(strings)

    @cache
    def items(self):
        items = []
        for key, value in self._map.items():
            if type(value) is types.DictType:
                value = MapRegistry(value)

            items.append((key, value))

        return items
