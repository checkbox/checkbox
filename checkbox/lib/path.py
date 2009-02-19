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
import posixpath

from glob import glob


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

def path_expand(path):
    path = posixpath.expanduser(path)
    return glob(path)

def path_expand_recursive(path):
    paths = []
    for path in path_expand(path):
        if posixpath.isdir(path):
            def walk_func(arg, directory, names):
                for name in names:
                    path = posixpath.join(directory, name)
                    if not posixpath.isdir(path):
                        arg.append(path)

            posixpath.walk(path, walk_func, paths)
        else:
            paths.append(path)

    return paths
