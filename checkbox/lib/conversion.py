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
import re


def string_to_type(string):
    conversion_table = {
        "(yes|true)": lambda v: True,
        "(no|false)": lambda v: False,
        "\d+\.\d+": lambda v: float(v.group(0)),
        "(\d+)( b)?": lambda v: int(v.group(1)),
        "(\d+) kb": lambda v: int(v.group(1)) * 1024,
        "(\d+) mb": lambda v: int(v.group(1)) * 1024 * 1024,
        "(\d+) gb": lambda v: int(v.group(1)) * 1024 * 1024 * 1024,
        "(\d+)( hz)?": lambda v: int(v.group(1)),
        "(\d+) khz": lambda v: int(v.group(1)) * 1024,
        "(\d+) mhz": lambda v: int(v.group(1)) * 1024 * 1024,
        "(\d+) ghz": lambda v: int(v.group(1)) * 1024 * 1024 * 1024}

    for regex, func in conversion_table.items():
        match = re.match("^%s$" % regex, string, re.IGNORECASE)
        if match:
            return func(match)

    return string

def sizeof_bytes(bytes):
    for x in ["bytes", "KB", "MB", "GB", "TB"]:
        string = "%3.1f%s" % (bytes, x)
        if bytes < 1024.0:
            break
        bytes /= 1024.0

    return string

def sizeof_hertz(hertz):
    for x in ["Hz", "KHz", "MHz", "GHz"]:
        string = "%3.1f%s" % (hertz, x)
        if hertz < 1000.0:
            break
        hertz /= 1000.0

    return string
