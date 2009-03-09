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
import logging

from checkbox.lib.process import Process

from checkbox.frontend import frontend
from checkbox.properties import String
from checkbox.registry import Registry


class CommandRegistry(Registry):
    """Base registry for running commands.

    The default behavior is to return the output of the command.

    Subclasses should define a command parameter.
    """

    command = String()

    def __init__(self, command=None):
        super(CommandRegistry, self).__init__()
        if command is not None:
            self.command = command

    @frontend("get_registry")
    def __str__(self):
        logging.info("Running command: %s", self.command)
        process = Process(self.command)
        while process.read():
            pass

        if process.errdata:
            logging.error("Failed to run command: %s", process.errdata.strip())
        return process.outdata

    def items(self):
        # Force running the command
        item = str(self)
        return []
