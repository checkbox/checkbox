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

from checkbox.lib.cache import cache
from checkbox.lib.update import recursive_update

from checkbox.properties import String
from checkbox.registries.command import CommandRegistry
from checkbox.registries.data import DataRegistry
from checkbox.registries.map import MapRegistry


class DeviceRegistry(DataRegistry):
    """Registry for HAL device information.

    Each item contained in this registry consists of the properties of
    the corresponding HAL device.
    """

    @cache
    def items(self):
        all = {}
        current = None
        for line in self.split("\n"):
            match = re.match(r"  (.*) = (.*) \((.*?)\)", line)
            if match:
                keys = match.group(1).split(".")
                value = match.group(2).strip()
                type_name = match.group(3)
                if type_name == "bool":
                    value = bool(value == "true")
                elif type_name == "double":
                    value = float(value.split()[0])
                elif type_name == "int" or type_name == "uint64":
                    value = int(value.split()[0])
                elif type_name == "string":
                    value = str(value.strip("'"))
                elif type_name == "string list":
                    value = [v.strip("'")
                            for v in value.strip("{}").split(", ")]
                else:
                    raise Exception, "Unknown type: %s" % type_name

                for key in reversed(keys):
                    value = {key: value}

                recursive_update(all, value)

        items = []
        for key, value in all.items():
            value = MapRegistry(value)
            items.append((key, value))

        return items


class HalRegistry(CommandRegistry):
    """Registry for HAL information.

    Each item contained in this registry consists of the udi as key and
    the corresponding device registry as value.
    """

    # Command to retrieve hal information.
    command = String(default="lshal")

    @cache
    def items(self):
        items = []
        for block in self.split("\n\n"):
            lines = block.split("\n")
            while lines:
                line = lines.pop(0)
                match = re.match(r"udi = '(.*)'", line)
                if match:
                    udi = match.group(1)
                    key = udi.split("/")[-1]
                    break

            if lines:
                value = DeviceRegistry("\n".join(lines))
                items.append((key, value))

        return items


factory = HalRegistry
