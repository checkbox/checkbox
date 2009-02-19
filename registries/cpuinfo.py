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
from checkbox.lib.cache import cache
from checkbox.lib.conversion import string_to_type

from checkbox.properties import Path
from checkbox.registries.data import DataRegistry
from checkbox.registries.filename import FilenameRegistry
from checkbox.registries.link import LinkRegistry


class ProcessorRegistry(DataRegistry):
    """Registry for processor information.

    Each item contained in this registry consists of the information
    for a single processor in the /proc/cpuinfo file.
    """

    def items(self):
        items = []
        for line in [l.strip() for l in self.split("\n")]:
            (key, value) = line.split(":", 1)

            # Sanitize key so that it can be expressed as
            # an attribute
            key = key.strip()
            key = key.replace(" ", "_")
            key = key.lower()

            # Rename processor entry to name
            if key == "processor":
                key = "name"

            # Express value as a list if it is flags
            value = value.strip()
            if key == "flags":
                value = value.split()
            else:
                value = string_to_type(value)

            items.append((key, value))

        items.append(("processor", LinkRegistry(self)))

        return items


class CpuinfoRegistry(FilenameRegistry):
    """Registry for cpuinfo information.

    Each item contained in this registry consists of the processor number
    as key and the corresponding processor registry as value.
    """

    # Filename where cpuinfo is stored.
    filename = Path(default="/proc/cpuinfo")

    @cache
    def items(self):
        items = []
        for data in [d.strip() for d in self.split("\n\n") if d]:
            key = len(items)
            value = ProcessorRegistry(data)
            items.append((key, value))

        return items


factory = CpuinfoRegistry
