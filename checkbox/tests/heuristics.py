# This file is part of Checkbox.
#
# Copyright 2012 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
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

"""

checkbox.tests.heuristics
=========================

Unit tests for checkbox.heuristics package
"""

from unittest import TestCase

from checkbox.heuristics.udisks2 import is_memory_card


class TestIsMemoryCard(TestCase):

    def test_generic(self):
        """
        Device with vendor string "GENERIC" is a memory card
        """
        self.assertTrue(
            is_memory_card(vendor="Generic", model="", udisks2_media=None))
