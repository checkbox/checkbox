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
import re

from checkbox.plugin import Plugin
from checkbox.test import TestManager


class PromptTest(Plugin):

    required_attributes = ["plugin_priorities"]

    def register(self, manager):
        super(PromptTest, self).register(manager)
        self.iterator = None
        self.result = None

        plugin_priorities = self.config.plugin_priorities \
            and re.split("\s+", self.config.plugin_priorities) or []
        self.test_manager = TestManager(plugin_priorities=plugin_priorities)

        for (rt, rh) in [
             ("report-architecture", self.report_architecture),
             ("report-category", self.report_category),
             ("report-result", self.report_result),
             ("test-.*", self.test_all),
             ("prompt-tests", self.prompt_tests)]:
            self._manager.reactor.call_on(rt, rh)

    def report_architecture(self, architecture):
        self.test_manager.set_architecture(architecture)

    def report_category(self, category):
        self.test_manager.set_category(category)

    def report_result(self, result):
        self.result = result

    def test_all(self, test):
        self.test_manager.add_test(test)

    def prompt_tests(self, interface):
        if self.iterator is None:
            self.iterator = self.test_manager.get_iterator()

        while True:
            try:
                test = self.iterator.go(interface.direction, self.result)
            except StopIteration:
                break

            self._manager.reactor.fire("prompt-test-%s" % test.plugin, interface,
                test)


factory = PromptTest
