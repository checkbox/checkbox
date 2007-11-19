import unittest

from hwtest.iterator import Iterator


class IteratorTest(unittest.TestCase):

    iterator_class = Iterator

    def test_empty_iter(self):
        i = self.iterator_class()
        for element in i:
            self.fail('iteration should not start if empty')

    def test_empty_has_next(self):
        i = self.iterator_class()
        self.assertFalse(i.has_next())

    def test_empty_next(self):
        i = self.iterator_class()
        try: i.next()
        except StopIteration: pass
        else: self.fail('next should raise exception')

    def test_empty_has_prev(self):
        i = self.iterator_class()
        self.assertFalse(i.has_prev())

    def test_empty_prev(self):
        i = self.iterator_class()
        try: i.prev()
        except StopIteration: pass
        else: self.fail('prev should raise exception')

    def test_one_iter(self):
        i = self.iterator_class(['a'])
        for element in i:
            self.assertTrue(element == 'a')

    def test_one_has_next(self):
        i = self.iterator_class(['a'])
        self.assertTrue(i.has_next())
        self.assertTrue(i.next() == 'a')
        self.assertFalse(i.has_next())

    def test_one_next(self):
        i = self.iterator_class(['a'])
        self.assertTrue(i.next() == 'a')
        try: i.next()
        except StopIteration: pass
        else: self.fail('next should raise exception')

    def test_one_has_prev(self):
        i = self.iterator_class(['a'])
        self.assertFalse(i.has_prev())
        self.assertTrue(i.next() == 'a')
        self.assertFalse(i.has_prev())
        try: i.next()
        except StopIteration: pass
        else: self.fail('next should raise exception')
        self.assertTrue(i.has_prev())
        self.assertTrue(i.prev() == 'a')
        self.assertFalse(i.has_prev())

    def test_one_prev(self):
        i = self.iterator_class(['a'])
        # next until after last element
        self.assertTrue(i.next() == 'a')
        try: i.next()
        except StopIteration: pass
        else: self.fail('next should raise exception')
        # prev until before first element
        self.assertTrue(i.prev() == 'a')
        try: i.prev()
        except StopIteration: pass
        else: self.fail('prev should raise exception')

    def test_two_next(self):
        i = self.iterator_class(['a', 'b'])
        # next until after last element
        self.assertTrue(i.next() == 'a')
        self.assertTrue(i.next() == 'b')
        try: i.next()
        except StopIteration: pass
        else: self.fail('next should raise exception')

    def test_two_prev(self):
        i = self.iterator_class(['a', 'b'])
        # next until after last element
        self.assertTrue(i.next() == 'a')
        self.assertTrue(i.next() == 'b')
        try: i.next()
        except StopIteration: pass
        else: self.fail('next should raise exception')
        # prev until before first element
        self.assertTrue(i.prev() == 'b')
        self.assertTrue(i.prev() == 'a')
        try: i.prev()
        except StopIteration: pass
        else: self.fail('prev should raise exception')

    def test_reset_elements(self):
        i = self.iterator_class(['a', 'b'])
        self.assertTrue(i.next() == 'a')
        i = iter(i)
        self.assertTrue(i.next() == 'a')
