# Exclude elements from an iterator

import types

from hwtest.iterator import Iterator


class Excluder(Iterator):
    def __init__(self, elements=[],
                 next_func=lambda x: False,
                 prev_func=None):
        if type(elements) is types.ListType:
            self.iterator = Iterator(elements)
        elif isinstance(elements, Iterator):
            self.iterator = elements
        else:
            raise Exception, "%s: invalid iterator type" % type(elements)
        self.next_func = next_func
        self.prev_func = prev_func or next_func

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
