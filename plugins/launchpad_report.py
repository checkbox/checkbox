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

from checkbox.lib.file import write
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

        # Launchpad report should be generated last.
        self._manager.reactor.call_on("report", self.report, 100)
        for (rt, rh) in [
             ("report-architecture", self.report_architecture),
             ("report-attachments", self.report_attachments),
             ("report-client", self.report_client),
             ("report-datetime", self.report_datetime),
             ("report-distribution", self.report_distribution),
             ("report-dmi", self.report_dmi),
             ("report-packages", self.report_packages),
             ("report-processors", self.report_processors),
             ("report-system_id", self.report_system_id),
             ("report-tests", self.report_tests),
             ("report-udev", self.report_udev),
             ("report-uname", self.report_uname)]:
            self._manager.reactor.call_on(rt, rh)

    def report_architecture(self, architecture):
        self._report["summary"]["architecture"] = architecture

    def report_attachments(self, attachments):
        for attachment in attachments:
            self._report["context"].append({
                "command": attachment["command"],
                "data": attachment["data"]})

    def report_client(self, client):
        self._report["summary"]["client"] = client

    def report_datetime(self, datetime):
        self._report["summary"]["date_created"] = datetime

    def report_distribution(self, distribution):
        self._report["software"]["lsbrelease"] = dict(distribution)
        self._report["summary"]["distribution"] = distribution.distributor_id
        self._report["summary"]["distroseries"] = distribution.release

    def report_dmi(self, dmi):
        self._report["hardware"]["dmi"] = dmi

    def report_packages(self, packages):
        self._report["software"]["packages"] = packages

    def report_processors(self, processors):
        self._report["hardware"]["processors"] = processors

    def report_system_id(self, system_id):
        self._report["summary"]["system_id"] = system_id

    def report_tests(self, tests):
        for test in tests:
            question = {
                "name": test["name"],
                "answer": test["status"],
                "comment": test.get("data", "")}
            self._report["questions"].append(question)

    def report_udev(self, udev):
        self._report["hardware"]["udev"] = udev

        scsi_devices = []
        for path, device in udev.items():
            if device.bus == "scsi":
                for name in "vendor", "model", "type":
                    scsi_device = "%s=%s" % (posixpath.join(path, name),
                        device[name])
                    scsi_devices.append(scsi_device)

        self._report["hardware"]["scsi-devices"] = "\n".join(scsi_devices)

    def report_uname(self, uname):
        self._report["summary"]["kernel-release"] = uname.release

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

        write(self.filename, payload)
        #file = open(self.filename, "w")
        #file.write(payload)
        #file.close()

        self._manager.reactor.fire("launchpad-report", self.filename)


factory = LaunchpadReport
