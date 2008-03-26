#
# Copyright (c) 2008 Canonical
#
# Written by Marc Tardif <marc@interunion.ca>
#
# This file is part of HWTest.
#
# HWTest is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HWTest is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HWTest.  If not, see <http://www.gnu.org/licenses/>.
#
import types

from hwtest.lib.cache import cache
from hwtest.registry import Registry


class MapRegistry(Registry):
    """Registry for maps.

    The default behavior is to express the given maps as a tree of items.
    """

    def __init__(self, config, map={}):
        super(MapRegistry, self).__init__(config)
        self.map = map

    def __str__(self):
        strings = ["%s: %s" % (k, v) for k, v in self.map.items()]

        return "\n".join(strings)

    @cache
    def items(self):
        items = []
        for key, value in self.map.items():
            if type(value) is types.DictType:
                value = MapRegistry(self.config, value)

            items.append((key, value))

        return items
