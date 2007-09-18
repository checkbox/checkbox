from tests.iterator import IteratorTest

from hwtest.excluder import Excluder


class ExcluderTest(IteratorTest):

    iterator_class = Excluder

    def test_next_func(self):
        e = self.iterator_class(['a', 'b'], next_func=lambda x: x == 'a')
        # next until after last element
        self.assertTrue(e.next() == 'b')
        try: e.next()
        except StopIteration: pass
        else: self.fail('next should raise exception')
        # prev until before first element
        self.assertTrue(e.prev() == 'b')
        self.assertTrue(e.prev() == 'a')
        try: e.prev()
        except StopIteration: pass
        else: self.fail('prev should raise exception')

    def test_prev_func(self):
        e = self.iterator_class(['a', 'b'], prev_func=lambda x: x == 'a')
        # next until after last element
        self.assertTrue(e.next() == 'a')
        self.assertTrue(e.next() == 'b')
        try: e.next()
        except StopIteration: pass
        else: self.fail('next should raise exception')
        # prev until before first element
        self.assertTrue(e.prev() == 'b')
        try: e.prev()
        except StopIteration: pass
        else: self.fail('prev should raise exception')
