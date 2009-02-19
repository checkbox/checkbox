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
from checkbox.lib.iterator import Iterator

from checkbox.properties import Path, String
from checkbox.plugin import Plugin


class UserInterface(Plugin):

    interface_module = String()
    interface_class = String()

    # Title of the user interface
    title = String(default="System Testing")

    # Path where data files are stored.
    data_path = Path(required=False)

    def register(self, manager):
        super(UserInterface, self).register(manager)

        self._manager.reactor.call_on("run", self.run)

    def run(self):
        interface_module = __import__(self.interface_module,
            None, None, [''])
        interface_class = getattr(interface_module, self.interface_class)
        interface = interface_class(self.title, self.data_path)

        iterator = Iterator([
             "prompt-begin",
             "prompt-gather",
             "prompt-category",
             "prompt-tests",
             "prompt-report",
             "prompt-exchange",
             "prompt-finish"])

        while True:
            try:
                event_type = iterator.go(interface.direction)
            except StopIteration:
                break

            self._manager.reactor.fire(event_type, interface)


factory = UserInterface
