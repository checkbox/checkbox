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
from gettext import gettext as _

from checkbox.plugin import Plugin
from checkbox.properties import String

final_text = String(default=_("Successfully finished testing!"))

class FinalPrompt(Plugin):

    def register(self, manager):
        super(FinalPrompt, self).register(manager)

        # Final should be prompted first
        self._manager.reactor.call_on("prompt-finish", self.prompt_finish, -100)
        self._manager.reactor.call_on("report-final-text", self._on_report_final_text, -100)

    def _on_report_final_text(self, text):
        self.final_text = text

    def prompt_finish(self, interface):
        interface.show_text(self.final_text, next=_("_Finish"))


factory = FinalPrompt
