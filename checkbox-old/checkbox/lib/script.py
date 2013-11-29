#
# This file is part of Checkbox.
#
# Copyright 2008 Canonical Ltd.
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
#
import posixpath

from checkbox.lib.environ import get_path


def get_globals(script):
    path = posixpath.expanduser(script)
    if not posixpath.exists(path):
        path = get_path(script)
        if not path:
            raise Exception("Script not found in PATH: %s" % script)

    globals = {}
    exec(compile(open(path).read(), path, 'exec'), globals)
    return globals
