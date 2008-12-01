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
import unittest

from checkbox.lib.iterator import Iterator, IteratorExclude, IteratorPostRepeat


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


class IteratorExcludeTest(IteratorTest):

    iterator_class = IteratorExclude

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


class IteratorPostRepeatTest(IteratorTest):

    iterator_class = IteratorPostRepeat

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
