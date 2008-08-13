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
from checkbox.lib.cache import cache

from checkbox.registry import Registry
from checkbox.registries.command import CommandRegistry
from checkbox.registries.link import LinkRegistry


COLUMNS = ["name", "version", "description"]


class PackageRegistry(Registry):

    def __init__(self, config, package):
        super(PackageRegistry, self).__init__(config)
        self.package = package

    def __str__(self):
        strings = ["%s: %s" % (k, v) for k, v in self.package.items()]

        return "\n".join(strings)

    @cache
    def items(self):
        items = [(k, v) for k, v in self.package.items()]
        items.append(("package", LinkRegistry(None, self)))

        return items


class PackagesRegistry(CommandRegistry):
    """Registry for packages."""

    @cache
    def items(self):
        items = []
        for line in [l for l in self.split("\n") if l]:
            # Determine the lengths of dpkg columns and
            # strip status column.
            if line.startswith("+++"):
                lengths = [len(i) for i in line.split("-")]
                lengths[0] += 1
                for i in range(1, len(lengths)):
                    lengths[i] += lengths[i - 1] + 1

            # Parse information from installed packages.
            if line.startswith("ii"):
                package = {}
                for i in range(len(COLUMNS)):
                    key = COLUMNS[i]
                    value = line[lengths[i]:lengths[i+1]-1].strip()
                    package[key] = value

                key = package["name"]
                value = PackageRegistry(None, package)
                items.append((key, value))

        return items


factory = PackagesRegistry
