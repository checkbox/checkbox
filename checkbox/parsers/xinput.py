#
# This file is part of Checkbox.
#
# Copyright 2012 Canonical Ltd.
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

from string import (
    ascii_letters,
    ascii_uppercase,
    )


DEVICE_RE = re.compile(
    r""".+?(?P<name>[%s].+?) *\sid=(?P<id>\d+)"""
    % ascii_uppercase)
ATTRIBUTE_RE = re.compile(
    r"""(?P<key>[%s].+?): (?P<value>.+)"""
    % ascii_letters)
CLASS_VALUE_RE = re.compile(
    r"""\d+\. Type: (?P<class>.+)""")
LIST_VALUE_RE = re.compile(
    r"""((?:[^ "]|"[^"]*")+)""")


class XinputParser:
    """Parser for the xinput command."""

    _key_map = {
        "Buttons supported": "buttons_supported",
        "Button labels": "button_labels",
        "Button state": "button_state",
        "Class originated from": "class",
        "Keycodes supported": "keycodes_supported",
        "Touch mode": "touch_mode",
        "Max number of touches": "max_touch",
        }

    def __init__(self, stream):
        self.stream = stream

    def _parseKey(self, key):
        if " " in key:
            return self._key_map.get(key)
        else:
            return key.lower()

    def _parseValue(self, value):
        if value is not None:
            value = value.strip()
            if not value:
                return None

            match = CLASS_VALUE_RE.match(value)
            if match:
                return match.group("class")

            if '"' in value:
                return list(self._parseList(value))

        return value

    def _parseList(self, value):
        for element in LIST_VALUE_RE.split(value)[1::2]:
            if element.startswith('"') and element.endswith('"'):
                yield element.strip('"')
            elif element == "None":
                yield None

    def run(self, result):
        output = self.stream.read()
        for record in re.split(r"\n{2,}", output):
            record = record.strip()

            # Skip empty records
            if not record:
                continue

            lines = record.split("\n")

            # Parse device
            line = lines.pop(0)
            match = DEVICE_RE.match(line)
            if not match:
                continue

            device = {
                "id": int(match.group("id")),
                "name": match.group("name"),
                }
            result.addXinputDevice(device)

            # Parse device classes
            device_class = {}
            prefix = ""

            for line in lines:
                line = line.strip()

                # Skip lines with an unsupported attribute
                match = ATTRIBUTE_RE.match(line)
                if not match:
                    if line.startswith("Scroll"):
                        prefix = "scroll_"
                    elif line.startswith("Detail"):
                        prefix = "detail_"
                    continue

                # Skip lines with an unsupported key
                key = self._parseKey(match.group("key"))
                if not key:
                    continue

                value = self._parseValue(match.group("value"))

                # Special case for the class
                if key == "class" and device_class:
                    result.addXinputDeviceClass(device, device_class)
                    device_class = {}
                    prefix = ""

                device_class[prefix + key] = value

            if device_class:
                result.addXinputDeviceClass(device, device_class)

        return result
