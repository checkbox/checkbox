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
from hwtest.contrib import bpickle
from hwtest.registry import Registry


def install():
    """Install bpickle extensions for Registry types."""
    for type, function in get_registry_types():
        bpickle.dumps_table[type] = function


def uninstall():
    """Uninstall bpickle extensions for Registry types."""
    for type, function in get_registry_types():
        del bpickle.dumps_table[type]


def get_registry_types():
    """
    Generator yields C{(type, bpickle_function)} for available Registry
    types.
    """
    for (type, function) in [(Registry, bpickle.dumps_dict)]:
        yield type, function
