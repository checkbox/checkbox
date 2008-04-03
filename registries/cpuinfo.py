#
# Copyright (c) 2008 Canonical
#
# Written by Marc Tardif <marc@interunion.ca>
#
# This file is part of HWTest.
#
# HWTest is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HWTest is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HWTest.  If not, see <http://www.gnu.org/licenses/>.
#
from hwtest.lib.cache import cache
from hwtest.lib.conversion import string_to_type

from hwtest.registries.data import DataRegistry
from hwtest.registries.file import FileRegistry
from hwtest.registries.link import LinkRegistry


class ProcessorRegistry(DataRegistry):
    """Registry for processor information.

    Each item contained in this registry consists of the information
    for a single processor in the /proc/cpuinfo file.
    """

    @cache
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

        items.append(("processor", LinkRegistry(None, self)))

        return items


class CpuinfoRegistry(FileRegistry):
    """Registry for cpuinfo information.

    Each item contained in this registry consists of the processor number
    as key and the corresponding processor registry as value.
    """

    @cache
    def items(self):
        items = []
        for data in [d.strip() for d in self.split("\n\n") if d]:
            key = len(items)
            value = ProcessorRegistry(None, data)
            items.append((key, value))

        return items


factory = CpuinfoRegistry
