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
import posixpath
import shutil

from checkbox.lib.safe import safe_make_directory

from checkbox.properties import Path
from checkbox.plugin import Plugin
from checkbox.reports.launchpad_report import LaunchpadReportManager


class LaunchpadReport(Plugin):

    # Filename where submission information is cached.
    filename = Path(default="%(checkbox_data)s/submission.xml")

    # XSL Stylesheet
    stylesheet = Path(default="%(checkbox_share)s/report/checkbox.xsl")

    def register(self, manager):
        super(LaunchpadReport, self).register(manager)

        self._report = {
            "summary": {
                "private": False,
                "contactable": False,
                "live_cd": False},
            "hardware": {},
            "software": {
                "packages": []},
            "questions": [],
            "context": []}

        for (rt, rh) in [
             ("report-attachments", self.report_attachments),
             ("report-client", self.report_client),
             ("report-cpuinfo", self.report_cpuinfo),
             ("report-datetime", self.report_datetime),
             ("report-dpkg", self.report_dpkg),
             ("report-lsb", self.report_lsb),
             ("report-package", self.report_package),
             ("report-uname", self.report_uname),
             ("report-system_id", self.report_system_id),
             ("report-tests", self.report_tests)]:
            self._manager.reactor.call_on(rt, rh)

        # Launchpad report should be generated last.
        self._manager.reactor.call_on("report", self.report, 100)

    def report_attachments(self, attachments):
        for attachment in attachments:
            name = attachment["name"]
            if name == "dmi":
                self._report["hardware"]["dmi"] = attachment["data"]

            elif name == "udev":
                self._report["hardware"]["udev"] = attachment["data"]

            else:
                self._report["context"].append({
                    "command": attachment["command"],
                    "data": attachment["data"]})

    def report_client(self, client):
        self._report["summary"]["client"] = client

    def report_cpuinfo(self, resources):
        cpuinfo = resources[0]
        processors = []
        for i in range(int(cpuinfo["count"])):
            cpuinfo = dict(cpuinfo)
            cpuinfo["name"] = i
            processors.append(cpuinfo)

        self._report["hardware"]["processors"] = processors

    def report_datetime(self, datetime):
        self._report["summary"]["date_created"] = datetime

    def report_dpkg(self, resources):
        dpkg = resources[0]
        self._report["summary"]["architecture"] = dpkg["architecture"]

    def report_lsb(self, resources):
        lsb = resources[0]
        self._report["software"]["lsbrelease"] = dict(lsb)
        self._report["summary"]["distribution"] = lsb["distributor_id"]
        self._report["summary"]["distroseries"] = lsb["release"]

    def report_package(self, resources):
        self._report["software"]["packages"] = resources

    def report_uname(self, resources):
        uname = resources[0]
        self._report["summary"]["kernel-release"] = uname["release"]

    def report_system_id(self, system_id):
        self._report["summary"]["system_id"] = system_id

    def report_tests(self, tests):
        for test in tests:
            question = {
                "name": test["name"],
                "answer": test["status"],
                "comment": test.get("data", "")}
            self._report["questions"].append(question)

    def report(self):
        # Copy stylesheet to report directory
        stylesheet = posixpath.join(
            posixpath.dirname(self.filename),
            posixpath.basename(self.stylesheet))
        shutil.copy(self.stylesheet, stylesheet)

        # Prepare the payload and attach it to the form
        stylesheet = posixpath.abspath(stylesheet)
        report_manager = LaunchpadReportManager("system", "1.0", stylesheet)
        payload = report_manager.dumps(self._report).toprettyxml("")

        directory = posixpath.dirname(self.filename)
        safe_make_directory(directory)

        file = open(self.filename, "w")
        file.write(payload)
        file.close()

        self._manager.reactor.fire("launchpad-report", self.filename)


factory = LaunchpadReport
