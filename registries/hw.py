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
import os
import re
import logging

from checkbox.lib.cache import cache

from checkbox.properties import String
from checkbox.registries.command import CommandRegistry
from checkbox.registries.data import DataRegistry
from checkbox.registries.map import MapRegistry


class DeviceRegistry(DataRegistry):
    """Registry for HW device information.

    Each item contained in this registry consists of the properties of
    the corresponding HW device.
    """

    @cache
    def items(self):
        items = []
        lines = []

        id = status = depth = None
        for line in self.split("\n"):
            if not line:
                continue

            match = re.match(r"(\s+(\*-)?)(.+)", line)
            if not match:
                raise Exception, "Invalid line: %s" % line

            space = len(match.group(1))
            if depth is None:
                depth = space

            if space > depth:
                lines.append(line)
            elif match.group(2) is not None:
                if id is not None:
                    value = DeviceRegistry("\n".join(lines))
                    lines = []

                    items.append((id, value))
                    items.append(("status", status))

                node = match.group(3)
                match = re.match(r"([^\s]+)( [A-Z]+)?", node)
                if not match:
                    raise Exception, "Invalid node: %s" % node

                id = match.group(1)
                status = match.group(2)
            else:
                (key, value) = match.group(3).split(": ", 1)
                key = key.replace(" ", "_")

                # Parse potential list or dict values
                values = value.split(" ")
                if key == "product":
                    match = re.search(r"(.*) \[[0-9A-F]{1,4}:([0-9A-F]{1,4})\]$",
                        value)
                    if match:
                        value = match.group(1)
                        items.append(("product_id", int(match.group(2), 16)))
                elif key == "vendor":
                    match = re.search(r"(.*) \[([0-9A-F]{1,4})\]$", value)
                    if match:
                        value = match.group(1)
                        items.append(("vendor_id", int(match.group(2), 16)))
                elif key.endswith("s"):
                    value = values
                elif [v for v in values if "=" in v]:
                    index = 1
                    for value in values[1:]:
                        if "=" not in value:
                            values[index - 1] += " %s" % values.pop(index)
                        else:
                            index += 1
                    value = dict((v.split("=", 1) for v in values))
                    value = MapRegistry(value)

                items.append((key, value))

        if lines:
            value = DeviceRegistry("\n".join(lines))
            items.append((id, value))

        return items


class HwRegistry(CommandRegistry):
    """Registry for HW information.

    Each item contained in this registry consists of the hardware id as
    key and the corresponding device registry as value.
    """

    # Command to retrieve hw information.
    command = String(default="lshw -numeric 2>/dev/null")

    # Command to retrieve the hw version.
    version = String(default="lshw -version 2>/dev/null")

    @cache
    def __str__(self):
        logging.info("Running command: %s", self.version)
        version = os.popen(self.version).read().strip()
        numbers = version.split(".")
        if len(numbers) == 3 \
           and numbers[0] == "B" \
           and int(numbers[1]) == 2 \
           and int(numbers[2]) < 13:
            self.command = self.command.replace(" -numeric", "")

        return super(HwRegistry, self).__str__()

    @cache
    def items(self):
        lines = self.split("\n")

        key = lines.pop(0)
        value = DeviceRegistry("\n".join(lines))

        return [(key, value)]


factory = HwRegistry
