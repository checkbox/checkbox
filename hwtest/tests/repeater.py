from hwtest.tests.iterator import IteratorTest

from hwtest.repeater import PostRepeater


class PostRepeaterTest(IteratorTest):

    iterator_class = PostRepeater

    i = 0
    def increment(self):
        self.i += 1

    def test_next_func(self):
        self.i = 0
        r = self.iterator_class([1, 2], lambda x: self.increment())
        self.assertTrue(self.i == 0)
        self.assertTrue(r.next() == 1)
        self.assertTrue(self.i == 1)
        self.assertTrue(r.next() == 2)
        self.assertTrue(self.i == 2)
        try: r.next()
        except StopIteration: pass
        else: self.fail('next should raise exception')
        self.assertTrue(self.i == 2)

    def test_prev_func(self):
        self.i = 0
        r = self.iterator_class([1, 2], lambda x: self.increment())
        self.assertTrue(self.i == 0)
        self.assertTrue(r.next() == 1)
        self.assertTrue(self.i == 1)
        self.assertTrue(r.next() == 2)
        self.assertTrue(self.i == 2)
        self.assertTrue(r.prev() == 1)
        self.assertTrue(self.i == 2)
        try: r.prev()
        except StopIteration: pass
        else: self.fail('prev should raise exception')
        self.assertTrue(self.i == 2)
