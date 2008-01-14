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
