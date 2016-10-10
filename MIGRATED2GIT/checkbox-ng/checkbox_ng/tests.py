# This file is part of Checkbox.
#
# Copyright 2012 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.

#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.

"""
:mod:`checkbox_ng.tests` -- auxiliary test loaders for checkbox-ng
==================================================================
"""

import inspect
import os
import unittest

import checkbox_ng


def load_unit_tests():
    """
    Load all unit tests and return a TestSuite object
    """
    # Discover all unit tests. By simple convention those are kept in
    # python modules that start with the word 'test_' .
    return unittest.defaultTestLoader.discover(
        os.path.dirname(
            inspect.getabsfile(checkbox_ng)))


def test_suite():
    """
    Test suite function used by setuptools test loader.

    Uses unittest test discovery system to get a list of test cases defined
    inside checkbox-ng. See setup.py setup(test_suite=...) for a matching entry
    """
    return load_unit_tests()
