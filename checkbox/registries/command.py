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
import os
import logging

from checkbox.lib.cache import cache

from checkbox.registry import Registry


class CommandRegistry(Registry):
    """Base registry for running commands.

    The default behavior is to return the output of the command.

    Subclasses should define a command configuration parameter.
    """

    optional_attributes = ["command"]

    def __init__(self, config, command=None):
        super(CommandRegistry, self).__init__(config)
        self._command = command or self._config.command

    @cache
    def __str__(self):
        logging.info("Running command: %s", self._command)
        return os.popen(self._command).read()

    def items(self):
        return []
