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
from checkbox.lib.iterator import IteratorExclude, PREV

from checkbox.job import JobIterator
from checkbox.plugin import Plugin


class TestsPrompt(Plugin):

    def register(self, manager):
        super(TestsPrompt, self).register(manager)
        self._iterator = None
        self._ignore = []
        self._tests = {}

        for (rt, rh) in [
             ("ignore-jobs", self.ignore_jobs),
             ("report", self.report),
             ("report-test", self.report_test),
             ("prompt-tests", self.prompt_tests)]:
            self._manager.reactor.call_on(rt, rh)

    def report(self):
        self._manager.reactor.fire("report-tests", self._tests.values())

    def report_test(self, test):
        name = test["name"]
        test.update(self._tests.get(name, {}))
        test.setdefault("type", "test")
        self._tests[name] = test

    def ignore_jobs(self, jobs):
        self._ignore = jobs

    def prompt_tests(self, interface, blacklist=[], whitelist=[]):
        # TODO: blacklist and whitelist are being ignored
        if not self._iterator:
            tests = self._tests.values()
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

            self._manager.reactor.fire("prompt-job", interface, test)

    def _tests_exclude(self, test):
        if test["name"] in self._ignore:
            return True

        return False


factory = TestsPrompt
