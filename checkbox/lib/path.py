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
import posixpath


def path_split(path):
    return path.split(posixpath.sep)

def path_common(l1, l2, common=[]):
    if len(l1) < 1:
        return (common, l1, l2)

    if len(l2) < 1:
        return (common, l1, l2)

    if l1[0] != l2[0]:
        return (common, l1, l2)

    return path_common(l1[1:], l2[1:], common + [l1[0]])

def path_relative(p1, p2):
    (common, l1, l2) = path_common(path_split(p1), path_split(p2))
    p = []
    if len(l1) > 0:
        p = ["..%s" % posixpath.sep * len(l1)]

    p = p + l2
    return posixpath.join( *p )
