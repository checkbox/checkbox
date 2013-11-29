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

from checkbox.job import UNINITIATED
from checkbox.plugin import Plugin


class ShellTest(Plugin):

    def register(self, manager):
        super(ShellTest, self).register(manager)

        for (rt, rh) in [
             ("prompt-shell", self.prompt_shell),
             ("report-shell", self.report_shell)]:
            self._manager.reactor.call_on(rt, rh)

    def prompt_shell(self, interface, test):
        command = test.get("command")
        status = test.get("status", UNINITIATED)
        plugin = test.get("plugin", "shell")
        if command and (status == UNINITIATED or plugin != "shell"):
            # Register temporary handler for message-result events
            def message_result(status, data, duration):
                test["status"] = status
                test["data"] = data
                test["duration"] = duration

                # Don't fire any other message result
                self._manager.reactor.stop()

            event_id = self._manager.reactor.call_on("message-result", message_result, -100)

            interface.show_progress(
                _("Running %s...") % test["name"], self._manager.reactor.fire,
                "message-exec", test)

            self._manager.reactor.cancel_call(event_id)

        self._manager.reactor.fire("prompt-test", interface, test)

    def report_shell(self, test):
        self._manager.reactor.fire("report-test", test)


factory = ShellTest
