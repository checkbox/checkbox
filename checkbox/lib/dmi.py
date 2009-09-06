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

# See also 3.3.4.1 of the "System Management BIOS Reference Specification,
# Version 2.6.1" (Preliminary Standard) document, available from
# http://www.dmtf.org/standards/smbios.
class Dmi:
    chassis = (
        ("Undefined",             "unknown"), # 0x00
        ("Other",                 "unknown"),
        ("Unknown",               "unknown"),
        ("Desktop",               "desktop"),
        ("Low Profile Desktop",   "desktop"),
        ("Pizza Box",             "server"),
        ("Mini Tower",            "desktop"),
        ("Tower",                 "desktop"),
        ("Portable",              "laptop"),
        ("Laptop",                "laptop"),
        ("Notebook",              "laptop"),
        ("Hand Held",             "handheld"),
        ("Docking Station",       "laptop"),
        ("All In One",            "unknown"),
        ("Sub Notebook",          "laptop"),
        ("Space-saving",          "desktop"),
        ("Lunch Box",             "unknown"),
        ("Main Server Chassis",   "server"),
        ("Expansion Chassis",     "unknown"),
        ("Sub Chassis",           "unknown"),
        ("Bus Expansion Chassis", "unknown"),
        ("Peripheral Chassis",    "unknown"),
        ("RAID Chassis",          "unknown"),
        ("Rack Mount Chassis",    "unknown"),
        ("Sealed-case PC",        "unknown"),
        ("Multi-system",          "unknown"),
        ("CompactPCI",            "unknonw"),
        ("AdvancedTCA",           "unknown"),
        ("Blade",                 "server"),
        ("Blade Enclosure",       "unknown"))

    chassis_names = [c[0] for c in chassis]
    chassis_types = [c[1] for c in chassis]
    chassis_name_to_type = dict(chassis)


class DmiNotAvailable(object):
    def __init__(self, function):
        self._function = function

    def __get__(self, instance, cls=None):
        self._instance = instance
        return self

    def __call__(self, *args, **kwargs):
        name = self._function(self._instance, *args, **kwargs)
        if name == "Not Available":
            name = None

        return name
