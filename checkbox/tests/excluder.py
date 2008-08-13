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
from checkbox.tests.iterator import IteratorTest

from checkbox.excluder import Excluder


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
