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
from checkbox.properties import List, String
from checkbox.plugin import Plugin
from checkbox.test import TestResult, SKIP
from checkbox.traverser import Traverser, TraverserCallbacks


class PromptTestCallbacks(TraverserCallbacks):

    def __init__(self, plugin):
        super(PromptTestCallbacks, self).__init__()
        self._plugin = plugin

    def get_architecture(self):
        return self._plugin.architecture

    def get_category(self):
        return self._plugin.category

    def get_priorities(self):
        return self._plugin.priorities

    def skipped_dependent(self, test, result):
        result = TestResult(test, status=SKIP,
            data="Test dependent on skipped test.")
        self._plugin._manager.reactor.fire("report-result", result)

    def failed_dependent(self, test, result):
        result = TestResult(test, status=SKIP,
            data="Test dependent on failed test.")
        self._plugin._manager.reactor.fire("report-result", result)

    def unsupported_requires(self, test, result):
        result = TestResult(test, status=SKIP,
            data="System does not meet test requirements.")
        self._plugin._manager.reactor.fire("report-result", result)

    def undefined_architecture(self, test, result):
        result = TestResult(test, status=SKIP,
            data="No system architecture defined.")
        self._plugin._manager.reactor.fire("report-result", result)

    def unsupported_architecture(self, test, result):
        result = TestResult(test, status=SKIP,
            data="System architecture not supported.")
        self._plugin._manager.reactor.fire("report-result", result)

    def undefined_category(self, test, result):
        result = TestResult(test, status=SKIP,
            data="No system category defined.")
        self._plugin._manager.reactor.fire("report-result", result)

    def unsupported_category(self, test, result):
        result = TestResult(test, status=SKIP,
            data="System category not supported.")
        self._plugin._manager.reactor.fire("report-result", result)


class PromptTest(Plugin):

    # Plugin priorities for running tests
    plugin_priorities = List(type=String(), default_factory=lambda:"manual")

    def register(self, manager):
        super(PromptTest, self).register(manager)
        self._tests = []
        self._result = None
        self._traverser = None

        self.architecture = None
        self.category = None
        self.priorities = self.plugin_priorities

        for (rt, rh) in [
             ("report-architecture", self.report_architecture),
             ("report-category", self.report_category),
             ("report-result", self.report_result),
             ("test-.*", self.test_all),
             ("prompt-tests", self.prompt_tests)]:
            self._manager.reactor.call_on(rt, rh)

        self._manager.reactor.call_on("prompt-test-.*",
            self.prompt_test, 100)

    def report_architecture(self, architecture):
        self.architecture = architecture

    def report_category(self, category):
        self.category = category

    def report_result(self, result):
        self._result = result

    def test_all(self, test):
        self._tests.append(test)

    def prompt_test(self, interface, test):
        if not self._result or self._result.test != test:
            result = TestResult(test, status=SKIP,
                data="Test not handled by any plugin.")
            self._manager.reactor.fire("report-result", result)

    def prompt_tests(self, interface):
        if not self._traverser:
            self._traverser = Traverser(self._tests, PromptTestCallbacks, self)

        while True:
            try:
                test = self._traverser.go(interface.direction, self._result)
            except StopIteration:
                break

            self._manager.reactor.fire("prompt-test-%s" % test.plugin, interface,
                test)


factory = PromptTest
