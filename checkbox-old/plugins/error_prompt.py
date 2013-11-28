#
# This file is part of Checkbox.
#
# Copyright 2008 Canonical Ltd.
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


class ErrorPrompt(Plugin):

    def register(self, manager):
        super(ErrorPrompt, self).register(manager)

        self._manager.reactor.call_on("prompt-error",
            self.prompt_error)

    def prompt_error(self, interface, primary_text, secondary_text=None,
                     detailed_text=None):
        interface.show_error(primary_text, secondary_text, detailed_text)


factory = ErrorPrompt
