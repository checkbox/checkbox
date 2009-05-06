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


class TestsInfo(Plugin):

    def register(self, manager):
        super(TestsInfo, self).register(manager)
        self._tests = []

        for (rt, rh) in [
             ("report", self.report),
             ("report-test", self.report_test)]:
            self._manager.reactor.call_on(rt, rh)

    def report_test(self, test):
        self._tests.append(test)

    def report(self):
        self._manager.reactor.fire("report-tests", self._tests)


factory = TestsInfo
