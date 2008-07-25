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
from hwtest.plugin import Plugin
from hwtest.iterator import Iterator


class UserInterface(Plugin):

    required_attributes = ["interface_module", "interface_class"]
    optional_attributes = ["title", "gtk_path"]

    def run(self):
        interface_module = __import__(self.config.interface_module,
            None, None, [''])
        interface_class = getattr(interface_module, self.config.interface_class)
        interface = interface_class(self.config)

        iterator = Iterator([
             "prompt-begin",
             "prompt-gather",
             "prompt-category",
             "prompt-manual",
             "prompt-auto",
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
