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
import re

from checkbox.lib.iterator import IteratorExclude, PREV

from checkbox.job import JobIterator, UNINITIATED
from checkbox.plugin import Plugin
from checkbox.properties import List, String


class TestsPrompt(Plugin):

    # List of suites to blacklist
    blacklist = List(String(), default_factory=lambda:"")

    # List of suites to whitelist
    whitelist = List(String(), default_factory=lambda:"")

    def _tests_exclude(self, test):
        whitelist_patterns = [re.compile(r"^%s$" % r) for r in self.whitelist if r]
        blacklist_patterns = [re.compile(r"^%s$" % r) for r in self.blacklist if r]

        name = test["name"]
        if whitelist_patterns:
            if not [name for p in whitelist_patterns if p.match(name)]:
                return True
        elif blacklist_patterns:
            if [name for p in blacklist_patterns if p.match(name)]:
                return True

        return False

    def register(self, manager):
        super(TestsPrompt, self).register(manager)
        self._iterator = None
        self._keys = []
        self._tests = {}

        for (rt, rh) in [
             ("report", self.report),
             ("report-test", self.report_test),
             ("prompt-test", self.prompt_test),
             ("prompt-tests", self.prompt_tests)]:
            self._manager.reactor.call_on(rt, rh)

        self._manager.reactor.call_on("prompt-suite", self.prompt_suite, -100)

    def prompt_suite(self, interface, suite):
        self._iterator = None
        self._keys = []

    def report(self):
        self._manager.reactor.fire("report-tests", self._tests.values())

    def report_test(self, test):
        key = (test["suite"], test["name"],)
        self._keys.append(key)
        if key not in self._tests:
            test.setdefault("status", UNINITIATED)
            self._tests[key] = test

    def prompt_test(self, interface, test):
        self._manager.reactor.fire("prompt-%s" % test["plugin"],
            interface, test)

    def prompt_tests(self, interface, blacklist=[], whitelist=[]):
        # TODO: blacklist and whitelist are being ignored
        if not self._iterator:
            tests = [self._tests[k] for k in self._keys]
            self._iterator = JobIterator(tests, self._manager.registry)
            self._iterator = IteratorExclude(self._iterator,
                self._tests_exclude, self._tests_exclude)
            if interface.direction == PREV:
                self._iterator = self._iterator.last()

        while True:
            try:
                test = self._iterator.go(interface.direction)
            except StopIteration:
                break

            self._manager.reactor.fire("prompt-test", interface, test)


factory = TestsPrompt
