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
from checkbox.plugin import Plugin


class ManualTest(Plugin):

    def register(self, manager):
        super(ManualTest, self).register(manager)

        for (rt, rh) in [
             ("prompt-manual", self.prompt_manual),
             ("prompt-user-verify", self.prompt_manual),
             ("prompt-user-interact", self.prompt_manual),
             ("prompt-user-interact-verify", self.prompt_manual),
             ("report-manual", self.report_manual),
             ("report-user-verify", self.report_manual),
             ("report-user-interact", self.report_manual)]:
             ("report-user-interact-verify", self.report_manual)]:
            self._manager.reactor.call_on(rt, rh)

    def prompt_manual(self, interface, test):
        def runner(test):
            # Avoid modifying the content of test in place
            temp = dict(test)
            self._manager.reactor.fire("prompt-shell", interface, temp)
            return (temp["status"],
                temp.get("data", ""),
                temp.get("duration", 0))

        interface.show_test(test, runner)
        self._manager.reactor.fire("prompt-test", interface, test)

    def report_manual(self, test):
        self._manager.reactor.fire("report-test", test)


factory = ManualTest
