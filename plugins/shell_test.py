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

from checkbox.frontend import FrontendException
from checkbox.job import Job, UNINITIATED, UNRESOLVED
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
        if command and status == UNINITIATED:
            job = Job(command, test.get("environ"),
                test.get("timeout"), test.get("user"))
            try:
                (status, data, duration) = interface.show_progress(
                    _("Running %s..." % test["name"]), job.execute)
            except FrontendException:
                test["data"] = "Failed acquire privileges."
                test["duration"] = 0
                test["status"] = UNRESOLVED
            else:
                test["data"] = data
                test["duration"] = duration
                test["status"] = status

        self._manager.reactor.fire("prompt-test", interface, test)

    def report_shell(self, test):
        self._manager.reactor.fire("report-test", test)


factory = ShellTest
