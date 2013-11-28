#
# This file is part of Checkbox.
#
# Copyright 2013 Canonical Ltd.
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.

#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.
#
from checkbox.plugin import Plugin

class HexrPrompt(Plugin):

    def register(self, manager):
        super(HexrPrompt, self).register(manager)

        self.persist = None
        self._manager.reactor.call_on("prompt-exchange", self._on_prompt_exchange)

    def _on_prompt_exchange(self, interface):
        self._manager.reactor.fire("hexr-exchange", interface)

factory = HexrPrompt
