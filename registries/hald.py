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
from checkbox.properties import String
from checkbox.registries.command import CommandRegistry


class HaldRegistry(CommandRegistry):
    """Registry for HAL daemon information.

    For the moment, this registry only contains an item for the version
    as returned by the hald command.
    """

    # Command to retrieve hald information.
    command = String(default="hald --version 2>&1")

    def __str__(self):
        str = super(HaldRegistry, self).__str__()
        return str.strip().rsplit(": ")[1]

    def items(self):
        return [("version", str(self))]


factory = HaldRegistry
