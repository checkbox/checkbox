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
from checkbox.registry import Registry


class LinkRegistry(Registry):
    """Registry for links.

    The default behavior is to express the given maps as a tree of items.
    """

    def __init__(self, link):
        super(LinkRegistry, self).__init__()
        self._link = link

    def __str__(self):
        return str(self._link)

    def items(self):
        items = []
        for k, v in self._link.items():
            if isinstance(v, LinkRegistry):
                continue
            items.append((k, v))

        return items
