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

from registries.cpuinfo import CpuinfoRegistry


class CpuinfoRegistryTest(unittest.TestCase):

    def test_processors(self):
        registry = CpuinfoRegistry()
        self.assertTrue(registry.keys() > 0)
        self.assertTrue(registry[0])

    def test_vendor_id(self):
        registry = CpuinfoRegistry()
        processor = registry[0]
        self.assertTrue(processor.vendor_id)
