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
