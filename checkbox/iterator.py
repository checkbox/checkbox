#
# Copyright (c) 2008 Canonical
#
# Written by Marc Tardif <marc@interunion.ca>
#
# This file is part of Checkbox.
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


PREV = 0
NEXT = 1

class Iterator(object):
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


class IteratorExclude(Iterator):
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


class IteratorRepeat(Iterator):
    def __init__(self, elements=[], repeat_func=lambda x: x):
        if type(elements) is types.ListType:
            self.iterator = Iterator(elements)
        elif isinstance(elements, Iterator):
            self.iterator = elements
        else:
            raise Exception, "%s: invalid iterator type" % type(elements)
        self.repeat_func = repeat_func
        self.element = None

    def __iter__(self):
        self.iterator = iter(self.iterator)
        self.element = None
        return self

    def has_next(self):
        return self.iterator.has_next()

    def next(self):
        self.element = self.iterator.next()
        return self.element

    def _force_next(self):
        self.iterator._force_next()

    def has_prev(self):
        return self.iterator.has_prev()

    def prev(self):
        self.element = self.iterator.prev()
        return self.element

    def _force_prev(self):
        self.iterator._force_prev()


# Before before retrieving an element. Note that the last element will
# be repeated.
class IteratorPreRepeat(IteratorRepeat):
    def next(self):
        if self.element:
            self.repeat_func(self.element)
        return super(IteratorPreRepeat, self).next()


# After retrieving an element
class IteratorPostRepeat(IteratorRepeat):
    def next(self):
        element = super(IteratorPostRepeat, self).next()
        self.repeat_func(element)
        return element
