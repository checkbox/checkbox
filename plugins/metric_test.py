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
from gettext import gettext as _

from checkbox.job import Job, UNINITIATED
from checkbox.plugin import Plugin


class MetricTest(Plugin):

    def register(self, manager):
        super(MetricTest, self).register(manager)

        for (rt, rh) in [
             ("prompt-metric", self.prompt_metric),
             ("report-metric", self.report_metric)]:
            self._manager.reactor.call_on(rt, rh)

    def prompt_metric(self, interface, test):
        command = test.get("command")
        status = test.get("status", UNINITIATED)
        if command and status == UNINITIATED:
            job = Job(command, test.get("environ"),
                test.get("timeout"), test.get("user"))
            (status, data, duration) = interface.show_progress(
                _("Running metric tests..."), job.execute)
            test["data"] = data
            test["duration"] = duration
            test["status"] = status

    def report_metric(self, test):
        test["type"] = "metric"
        self._manager.reactor.fire("report-test", test)


factory = MetricTest
