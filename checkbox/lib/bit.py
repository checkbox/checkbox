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
def get_bitmask(key):
    bitmask = []
    for value in reversed(key.split()):
        value = int(value, 16)
        bitmask.append(value)

    return bitmask

def get_bitcount(bitmask):
    bitcount = 0
    for value in bitmask:
        while value:
            bitcount += 1
            value &= (value - 1)

    return bitcount

def test_bit(bit, bitmask):
    bits_per_long = 8 * 8
    offset = bit % bits_per_long
    long = int(bit / bits_per_long)
    if long >= len(bitmask):
        return 0
    return (bitmask[long] >> offset) & 1
