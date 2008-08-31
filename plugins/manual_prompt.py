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
from checkbox.plugin import Plugin


class ManualPrompt(Plugin):

    def register(self, manager):
        super(ManualPrompt, self).register(manager)
        self._results = {}

        # Manual tests should be asked first.
        for (rt, rh) in [
             ("prompt-test-manual", self.prompt_test_manual)]:
            self._manager.reactor.call_on(rt, rh)

    def prompt_test_manual(self, interface, test):
        result = self._results.get((test.suite, test.name))
        result = interface.show_test(test, result)
        self._results[(test.suite, test.name)] = result
        self._manager.reactor.fire("report-result", result)
        self._manager.reactor.stop()


factory = ManualPrompt
