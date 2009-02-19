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
from gettext import gettext as _

from checkbox.lib.cache import cache

from checkbox.plugin import Plugin


class ShellPrompt(Plugin):

    def register(self, manager):
        super(ShellPrompt, self).register(manager)
        self._manager.reactor.call_on("prompt-test-shell",
            self.prompt_test_shell)

    def _run_shell(self, test):
        result = test.command()
        self._manager.reactor.fire("report-result", result)

    @cache
    def prompt_test_shell(self, interface, test):
        if str(test.command):
            interface.show_wait(_("Running shell tests..."),
                self._run_shell, test)


factory = ShellPrompt
