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


PREV = -1
NEXT = 1


class Iterator(object):

    def __init__(self, elements=[]):
        self.elements = elements
        self.index = -1

    def __iter__(self):
        self.index = -1
        return self

    def has_next(self, *args, **kwargs):
        return self.index < len(self.elements) - 1

    def next(self, *args, **kwargs):
        if not self.has_next(*args, **kwargs):
            self.index = len(self.elements)
            raise StopIteration

        self.index += 1
        return self.elements[self.index]

    def _force_next(self):
        """Iterate one beyond the last element."""
        if self.index < len(self.elements):
            self.index += 1

    def has_prev(self, *args, **kwargs):
        return self.index > 0

    def prev(self, *args, **kwargs):
        if not self.has_prev(*args, **kwargs):
            raise StopIteration

        self.index -= 1
        return self.elements[self.index]

    def _force_prev(self):
        """Iterate one beyond the first element."""
        if self.index > -1:
            self.index -= 1

    def last(self, *args, **kwargs):
        while True:
            try:
                self.next(*args, **kwargs)
            except StopIteration:
                break

        return self

    def go(self, direction, *args, **kwargs):
        if direction == NEXT:
            element = self.next(*args, **kwargs)
        elif direction == PREV:
            element = self.prev(*args, **kwargs)
        else:
            raise Exception, "Unknown direction: %s" % direction

        return element


class IteratorContain(Iterator):

    def __init__(self, elements=[]):
        if type(elements) is types.ListType:
            self.iterator = Iterator(elements)
        elif isinstance(elements, Iterator):
            self.iterator = elements
        else:
            raise Exception, "%s: invalid iterator type" % type(elements)

    def __iter__(self):
        self.iterator = iter(self.iterator)
        return self

    def has_next(self, *args, **kwargs):
        return self.iterator.has_next(*args, **kwargs)

    def next(self, *args, **kwargs):
        return self.iterator.next(*args, **kwargs)

    def _force_next(self):
        self.iterator._force_next()

    def has_prev(self, *args, **kwargs):
        return self.iterator.has_prev(*args, **kwargs)

    def prev(self, *args, **kwargs):
        return self.iterator.prev(*args, **kwargs)

    def _force_prev(self):
        self.iterator._force_prev()


class IteratorExclude(IteratorContain):

    def __init__(self, elements=[], next_func=None, prev_func=None):
        super(IteratorExclude, self).__init__(elements)
        self.next_func = next_func
        self.prev_func = prev_func

    def has_next(self, *args, **kwargs):
        if self.iterator.has_next(*args, **kwargs):
            element = self.iterator.next(*args, **kwargs)
            if self.next_func is not None \
               and self.next_func(element, *args, **kwargs):
                return self.has_next(*args, **kwargs)
            else:
                self.iterator._force_prev()
                return True

        return False

    def next(self, *args, **kwargs):
        if not self.has_next(*args, **kwargs):
            self.iterator._force_next()
            raise StopIteration

        element = self.iterator.next(*args, **kwargs)
        return element

    def has_prev(self, *args, **kwargs):
        if self.iterator.has_prev(*args, **kwargs):
            element = self.iterator.prev(*args, **kwargs)
            if self.prev_func is not None \
               and self.prev_func(element, *args, **kwargs):
                return self.has_prev(*args, **kwargs)
            else:
                self.iterator._force_next()
                return True

        return False

    def prev(self, *args, **kwargs):
        if not self.has_prev(*args, **kwargs):
            raise StopIteration

        element = self.iterator.prev(*args, **kwargs)
        return element


class IteratorRepeat(IteratorContain):

    def __init__(self, elements=[], next_func=None, prev_func=None):
        super(IteratorRepeat, self).__init__(elements)
        self.next_func = next_func
        self.prev_func = prev_func
        self.element = None

    def __iter__(self):
        self.iterator = iter(self.iterator)
        self.element = None
        return self

    def next(self, *args, **kwargs):
        self.element = self.iterator.next(*args, **kwargs)
        return self.element

    def prev(self, *args, **kwargs):
        self.element = self.iterator.prev(*args, **kwargs)
        return self.element


# Before retrieving an element. Note that the last element will
# be repeated.
class IteratorPreRepeat(IteratorRepeat):

    def next(self, *args, **kwargs):
        if self.element and self.next_func is not None:
            self.next_func(self.element, *args, **kwargs)
        return super(IteratorPreRepeat, self).next(*args, **kwargs)

    def prev(self, *args, **kwargs):
        if self.element and self.prev_func is not None:
            self.prev_func(self.element, *args, **kwargs)
        return super(IteratorPreRepeat, self).prev(*args, **kwargs)


# After retrieving an element
class IteratorPostRepeat(IteratorRepeat):

    def next(self, *args, **kwargs):
        element = super(IteratorPostRepeat, self).next(*args, **kwargs)
        if self.next_func is not None:
            self.next_func(element, *args, **kwargs)
        return element

    def prev(self, *args, **kwargs):
        element = super(IteratorPostRepeat, self).prev(*args, **kwargs)
        if self.prev_func is not None:
            self.prev_func(element, *args, **kwargs)
        return element
