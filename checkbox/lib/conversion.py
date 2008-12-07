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
        "\d+": lambda v: int(v.group(0)),
        "\d+\.\d+": lambda v: float(v.group(0)),
        "(\d+) ?([kmgt]?b?)": lambda v: int(v.group(1)),
        "(\d+\.\d+) ?([kmgt]?b?)": lambda v: float(v.group(1)),
        "(\d+) ?([kmgt]?hz?)": lambda v: int(v.group(1)),
        "(\d+\.\d+) ?([kmgt]?hz?)": lambda v: float(v.group(1))}

    multiplier_table = {
        "b": 1,
        "kb?": 1024,
        "mb?": 1024 * 1024,
        "gb?": 1024 * 1024 * 1024,
        "tb?": 1024 * 1024 * 1024 * 1024,
        "hz": 1,
        "khz?": 1024,
        "mhz?": 1024 * 1024,
        "ghz?": 1024 * 1024 * 1024,
        "thz?": 1024 * 1024 * 1024 * 1024}

    for regex, conversion in conversion_table.items():
        match = re.match("^%s$" % regex, string, re.IGNORECASE)
        if match:
            value = conversion(match)
            if len(match.groups()) > 1:
                string = match.group(2)
                for regex, multiplier in multiplier_table.items():
                    match = re.match("^%s$" % regex, string, re.IGNORECASE)
                    if match:
                        value *= multiplier
                        return value

            return value

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
