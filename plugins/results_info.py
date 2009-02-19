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
from checkbox.properties import Int
from checkbox.plugin import Plugin


class ResultsInfo(Plugin):

    # Maximum number of results per request
    max_per_request = Int(default=20)

    def register(self, manager):
        super(ResultsInfo, self).register(manager)
        self._results = []

        for (rt, rh) in [
             ("report", self.report),
             ("report-result", self.report_result)]:
            self._manager.reactor.call_on(rt, rh)

    def report_result(self, result):
        self._results.append(result)
        if len(self._results) >= self.max_per_request:
            self.report()

    def report(self):
        if len(self._results):
            self._manager.reactor.fire("report-results", self._results)
            self._results = []


factory = ResultsInfo
