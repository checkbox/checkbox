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
from checkbox.lib.environ import get_variable

from checkbox.properties import Bool
from checkbox.plugin import Plugin


class BootPrompt(Plugin):

    # Enable running checkbox at boot time.
    enable = Bool(default=False)

    def register(self, manager):
        super(BootPrompt, self).register(manager)
        self._manager.reactor.call_on("prompt-begin", self.prompt_begin)

    def prompt_begin(self, interface):
        if get_variable("UPSTART_JOB") and not self.enable:
            self._manager.reactor.stop_all()


factory = BootPrompt
