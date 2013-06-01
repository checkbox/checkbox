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
def recursive_update(dst, src):
    irecursive_update(dst, list(src.items()))
    return dst

def irecursive_update(a, blist):
    try:
        stack = []
        while blist:
            while blist:
                (bk, bv) = blist.pop(0)
                if (bk in a
                     and isinstance(bv, dict)
                     and isinstance(a[bk], dict)):
                    stack.append((blist, a)) # current -> parent
                    break
                else:
                    a[bk] = bv
            else:
                while not blist:
                    blist, a = stack.pop() # current <- parent
                continue
            blist, a = list(bv.items()), a[bk]
    except IndexError:
        pass
