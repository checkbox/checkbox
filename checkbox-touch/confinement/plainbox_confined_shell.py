# This file is part of Checkbox.
#
# Copyright 2015 Canonical Ltd.
# Written by:
#   Maciej Kisielewski <maciej.kisielewski@canonical.com>
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

import json
import os


def obj_to_file(obj, consumer_name, filename):
    """
    Stringify object, write it to file and return path to the file.

    :param object:
        Object to be stringified
    :param consumer_name:
        Name of the app that will consume the generated file
    :param filename:
        Name of the file to write to (just the basename)
    :returns:
        Path to the written file
    """
    s = json.dumps(obj)
    dir_path = os.path.join(os.environ['XDG_RUNTIME_DIR'], consumer_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    out_path = os.path.join(dir_path, filename)
    with open(out_path, "wt") as f:
        f.write(s)
    return out_path
