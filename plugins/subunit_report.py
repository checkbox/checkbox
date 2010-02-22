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

from checkbox.job import (FAIL, PASS, UNINITIATED,
    UNRESOLVED, UNSUPPORTED, UNTESTED)
from checkbox.properties import Path
from checkbox.plugin import Plugin


STATUS_TO_SUBUNIT = {
    FAIL: "failure",
    PASS: "success",
    UNINITIATED: "skip",
    UNRESOLVED: "error",
    UNSUPPORTED: "skip",
    UNTESTED: "skip"}


class SubunitReport(Plugin):

    # Filename where to store the subunit report
    filename = Path(default="%(checkbox_data)s/subunit.log")

    def register(self, manager):
        super(SubunitReport, self).register(manager)

        for (rt, rh) in [
             ("gather", self.gather),
             ("prompt-test", self.prompt_test)]:
            self._manager.reactor.call_on(rt, rh)

    def gather(self):
        logging.debug("Opening filename: %s", self.filename)
        self.file = open(self.filename, "w")

    def prompt_test(self, interface, test):
        file = self.file

        # Test
        if "suite" in test:
            name = "%s %s" % (test["suite"], test["name"])
        else:
            name = test["name"]
        file.write("test: %s\n" % name)

        # TODO: determine where to handle requires

        # Status
        status = STATUS_TO_SUBUNIT[test["status"]]
        file.write("%s: %s" % (status, name))

        # Data
        data = test.get("data")
        if data:
            # Prepend whitespace to the data
            data = data.replace("\n", "\n ").strip()
            file.write(" [\n %s\n]" % data)

        file.write("\n")


factory = SubunitReport
