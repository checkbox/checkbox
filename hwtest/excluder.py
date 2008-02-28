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
"""
Exclude elements from an iterator.
"""

import types

from hwtest.iterator import Iterator


class Excluder(Iterator):
    def __init__(self, elements=[],
                 next_func=lambda x: False,
                 prev_func=lambda x: False):
        if type(elements) is types.ListType:
            self.iterator = Iterator(elements)
        elif isinstance(elements, Iterator):
            self.iterator = elements
        else:
            raise Exception, "%s: invalid iterator type" % type(elements)
        self.next_func = next_func
        self.prev_func = prev_func

    def __iter__(self):
        self.iterator = iter(self.iterator)
        return self

    def has_next(self):
        if self.iterator.has_next():
            element = self.iterator.next()
            if self.next_func(element):
                return self.has_next()
            else:
                self.iterator._force_prev()
                return True

        return False

    def next(self):
        if not self.has_next():
            self.iterator._force_next()
            raise StopIteration

        element = self.iterator.next()
        return element

    def _force_next(self):
        self.iterator._force_next()

    def has_prev(self):
        if self.iterator.has_prev():
            element = self.iterator.prev()
            if self.prev_func(element):
                return self.has_prev()
            else:
                self.iterator._force_next()
                return True

        return False

    def prev(self):
        if not self.has_prev():
            raise StopIteration

        element = self.iterator.prev()
        return element

    def _force_prev(self):
        self.iterator._force_prev()
