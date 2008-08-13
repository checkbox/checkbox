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
from checkbox.registries.map import MapRegistry
from checkbox.registries.tests.helpers import TestHelper


class MapRegistryTest(TestHelper):

    def test_map(self):
        map = {'a': 1}
        registry = MapRegistry(self.config, map)
        self.assertTrue(registry.a)
        self.assertTrue(registry.a == 1)
        self.assertFalse(registry.b)
