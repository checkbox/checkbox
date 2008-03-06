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
from hwtest.plugin import Plugin
from hwtest.test import TestManager


class ManualPrompt(Plugin):

    def register(self, manager):
        super(ManualPrompt, self).register(manager)
        self._test_manager = TestManager()

        # Manual tests should be asked first.
        for (rt, rh) in [
             (("interface", "category"), self.interface_category),
             (("test", "manual"), self.test_manual),
             (("test", "interactive"), self.test_manual),
             (("prompt", "manual"), self.prompt_manual)]:
            self._manager.reactor.call_on(rt, rh)

    def interface_category(self, category):
        self._test_manager.set_category(category)

    def test_manual(self, test):
        self._test_manager.add_test(test)

    def prompt_manual(self, interface):
        tests = self._test_manager.get_iterator(interface.direction)

        while True:
            try:
                test = tests.go(interface.direction)
            except StopIteration:
                break

            interface.show_test(test, test.plugin == "manual")
            self._manager.reactor.fire(("report", "test"), test)


factory = ManualPrompt
