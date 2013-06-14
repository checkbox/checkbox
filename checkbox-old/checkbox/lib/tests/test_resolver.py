#
# This file is part of Checkbox.
#
# Copyright 2008 Canonical Ltd.
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

from checkbox.lib.resolver import Resolver


class ResolverTest(unittest.TestCase):
    def setUp(self):
        self.resolver = Resolver()

    def test_dependencies_none(self):
        try:
            self.resolver.get_dependencies('a')
        except Exception as error:
            self.assertTrue(error.args[0].startswith('no dependencies'))
        else:
            self.fail('non existing element accepted by resolver')

    def test_dependencies_one_level(self):
        self.resolver.add('a')

        results = self.resolver.get_dependencies('a')
        self.assertListEqual(results, ['a'])

    def test_dependencies_two_level(self):
        self.resolver.add('a')
        self.resolver.add('b', 'a')

        results = self.resolver.get_dependencies('b')
        self.assertListEqual(results, ['a', 'b'])

    def test_dependencies_multiple(self):
        self.resolver.add('a')
        # A appears as a dependency multiple times
        # in b and c, but isn't a circular dependency
        self.resolver.add('b', 'a')
        self.resolver.add('c', 'a', 'b')

        results = self.resolver.get_dependencies('c')
        self.assertListEqual(results, ['a', 'b', 'c'])

    def test_dependencies_circular(self):
        try:
            self.resolver.add('a', 'b')
            self.resolver.add('b', 'a')
            self.resolver.get_dependencies('a')
        except Exception as error:
            self.assertTrue(error.args[0].startswith('circular dependency'))
        else:
            self.fail('circular dependency not detected')

    def test_dependents_none(self):
        self.resolver.add('a')

        results = self.resolver.get_dependents('a')
        self.assertTrue(len(results) == 0)

    def test_dependents_one(self):
        self.resolver.add('a')
        self.resolver.add('b', 'a')

        results = self.resolver.get_dependents('a')
        self.assertListEqual(results, ['b'])

    def test_dependents_two(self):
        resolver = Resolver()
        resolver.add('a')
        resolver.add('b', 'a')
        resolver.add('c', 'b')

        results = resolver.get_dependents('a')
        self.assertListEqual(results, ['b', 'c'])

    def test_multiple_resolve_steps(self):
        self.resolver.add('a', 'b')
        results = self.resolver.get_dependents()
        self.assertListEqual(results, ['a'])

        self.resolver.add('b')
        results = self.resolver.get_dependents()
        self.assertListEqual(results, ['b', 'a'])
