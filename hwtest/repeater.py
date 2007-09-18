# Repeat a function before or after iteration

import types

from hwtest.iterator import Iterator


class Repeater(Iterator):
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
class PreRepeater(Repeater):
    def next(self):
        if self.element:
            self.repeat_func(self.element)
        return Repeater.next(self)


# After retrieving an element
class PostRepeater(Repeater):
    def next(self):
        element = Repeater.next(self)
        self.repeat_func(element)
        return element

