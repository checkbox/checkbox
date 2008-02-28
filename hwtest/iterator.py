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
PREV = 0
NEXT = 1

class Iterator:
    def __init__(self, elements=[]):
        self.elements = elements
        self.index = -1

    def __iter__(self):
        self.index = -1
        return self

    def has_next(self):
        return self.index < len(self.elements) - 1

    def next(self):
        if not self.has_next():
            self.index = len(self.elements)
            raise StopIteration

        self.index += 1
        return self.elements[self.index]

    def _force_next(self):
        """Iterate one beyond the last element."""
        if self.index < len(self.elements):
            self.index += 1

    def has_prev(self):
        return self.index > 0

    def prev(self):
        if not self.has_prev():
            raise StopIteration

        self.index -= 1
        return self.elements[self.index]

    def _force_prev(self):
        """Iterate one beyond the first element."""
        if self.index > -1:
            self.index -= 1

    def go(self, direction):
        if direction == NEXT:
            element = self.next()
        elif direction == PREV:
            element = self.prev()
        else:
            raise Exception, "Unknown direction: %s" % direction

        return element
