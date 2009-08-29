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
import re
import string

def get_ids(filename):
    vendor_re = re.compile(r"^(?P<id>[%s]{4})\s+(?P<name>.*\S)\s*$"
        % string.hexdigits)
    device_re = re.compile(r"^\t(?P<id>[%s]{4})\s+(?P<name>.*\S)\s*$"
        % string.hexdigits)

    ids = {}
    file = open(filename, "r")
    for line in file.readlines():
        match = vendor_re.match(line)
        if match:
            vendor_id = int(match.group("id"), 16)
            vendor_name = match.group("name").strip()
            ids[vendor_id] = {"name": vendor_name}
        else:
            match = device_re.match(line)
            if match:
                device_id = int(match.group("id"), 16)
                device_name = match.group("name").strip()
                ids[vendor_id].setdefault("devices", {})
                ids[vendor_id]["devices"][device_id] = {"name": device_name}

    return ids
