#!/usr/bin/env python3
# Copyright 2015 Canonical Ltd.
# Written by:
#   Sylvain Pineau <sylvain.pineau@canonical.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import subprocess
import re

def _get_battery_path():
    paths = subprocess.check_output(["upower", "-e"])
    match = re.search(b'/org/freedesktop/UPower/devices/battery.*', paths)
    if match:
        return match.group(0)

def get_battery_percentage():
    path = _get_battery_path()
    info = subprocess.check_output(["upower", "-i", path])
    match = re.search(b'percentage:\s+(\d+)', info, re.M)
    if match:
        return match.group(1)
