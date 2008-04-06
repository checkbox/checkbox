#
# Copyright (c) 2008 Canonical
#
# Written by Marc Tardif <marc@interunion.ca>
#
# This file is part of HWTest.
#
# HWTest is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HWTest is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HWTest.  If not, see <http://www.gnu.org/licenses/>.
#
from gettext import gettext as _

from hwtest.lib.cache import cache

from hwtest.plugin import Plugin
from hwtest.test import TestManager
from hwtest.result import Result


class AutoPrompt(Plugin):

    def register(self, manager):
        super(AutoPrompt, self).register(manager)
        self._test_manager = TestManager()

        for (rt, rh) in [
             ("interface-category", self.interface_category),
             ("test-auto", self.test_auto),
             ("prompt-auto", self.prompt_auto)]:
            self._manager.reactor.call_on(rt, rh)

    def interface_category(self, category):
        self._test_manager.set_category(category)

    def test_auto(self, test):
        self._test_manager.add_test(test)

    def _run_auto(self):
        for test in self._test_manager.get_iterator():
            test.command()
            test.description()
            test.result = Result(test.command.get_status(),
                test.command.get_data(),
                test.command.get_duration())
            self._manager.reactor.fire("report-test",
                test)

    @cache
    def prompt_auto(self, interface):
        if self._test_manager.get_count():
            interface.show_wait(_("Running automatic tests..."),
                self._run_auto)


factory = AutoPrompt
