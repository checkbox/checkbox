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
import logging

from checkbox.test import FAIL, PASS, SKIP

from checkbox.properties import Path
from checkbox.plugin import Plugin


class SubunitReport(Plugin):

    # Filename where to store the subunit report
    filename = Path(default="%(checkbox_data)s/subunit.log")

    result_status_table = {
        FAIL: "failure",
        PASS: "success",
        SKIP: "skip"}

    def register(self, manager):
        super(SubunitReport, self).register(manager)
        self._file = None

        for (rt, rh) in [
             ("gather", self.gather),
             ("report-result", self.report_result)]:
            self._manager.reactor.call_on(rt, rh)

    def gather(self):
        logging.debug("Opening filename: %s", self.filename)
        self._file = open(self.filename, "w")

    def report_result(self, result):
        # Test
        test = result.test
        name = "%s %s" % (test.suite, test.name)
        self._file.write("test: %s\n" % name)

        # Tags
        tags = []
        if result.packages:
            tags.extend(["package:%s-%s" % (p.name, p.version)
                for p in result.packages])
        if tags:
            self._file.write("tags: %s\n" % " ".join(tags))

        # Status
        status = self.result_status_table[result.status]
        self._file.write("%s: %s" % (status, name))
        if result.data:
            # Prepend whitespace to the data
            data = result.data.replace("\n", "\n ").strip()
            self._file.write(" [\n %s\n]\n" % data)
        else:
            self._file.write("\n")


factory = SubunitReport
