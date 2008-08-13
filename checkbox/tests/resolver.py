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

from checkbox.resolver import Resolver


class ResolverTest(unittest.TestCase):
    def test_dependencies_none(self):
        resolver = Resolver()
        try:
            resolver.get_dependencies('a')
        except Exception, error:
            self.assertTrue(error.args[0].startswith('no dependencies'))
        else:
            self.fail('non existing element accepted by resolver')

    def test_dependencies_one_level(self):
        resolver = Resolver()
        resolver.add('a')

        results = resolver.get_dependencies('a')
        self.assertTrue(len(results) == 1)
        self.assertTrue(results[0] == 'a')

    def test_dependencies_two_level(self):
        resolver = Resolver()
        resolver.add('a')
        resolver.add('b', 'a')

        results = resolver.get_dependencies('b')
        self.assertTrue(len(results) == 2)
        self.assertTrue(results[0] == 'a')
        self.assertTrue(results[1] == 'b')

    def test_dependencies_multiple(self):
        resolver = Resolver()
        resolver.add('a')
        resolver.add('b')
        resolver.add('c', 'a', 'b')

        results = resolver.get_dependencies('c')
        self.assertTrue(len(results) == 3)
        self.assertTrue(results[0] == 'a')
        self.assertTrue(results[1] == 'b')
        self.assertTrue(results[2] == 'c')

    def test_dependencies_circular(self):
        resolver = Resolver()
        resolver.add('a', 'b')
        resolver.add('b', 'a')
        try:
            resolver.get_dependencies('a')
        except Exception, error:
            self.assertTrue(error.args[0].startswith('circular dependency'))
        else:
            self.fail('circular dependency not detected')

    def test_dependents_none(self):
        resolver = Resolver()
        resolver.add('a')

        results = resolver.get_dependents('a')
        self.assertTrue(len(results) == 0)

    def test_dependents_one(self):
        resolver = Resolver()
        resolver.add('a')
        resolver.add('b', 'a')

        results = resolver.get_dependents('a')
        self.assertTrue(len(results) == 1)
        self.assertTrue(results[0] == 'b')

    def test_dependents_two(self):
        resolver = Resolver()
        resolver.add('a')
        resolver.add('b', 'a')
        resolver.add('c', 'b')

        results = resolver.get_dependents('a')
        self.assertTrue(len(results) == 2)
        self.assertTrue(results[0] == 'b')
        self.assertTrue(results[1] == 'c')
