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
import os

from gettext import gettext as _
from string import printable

from checkbox.lib.safe import safe_make_directory

from checkbox.properties import Path, String
from checkbox.plugin import Plugin
from checkbox.reports.launchpad_report import LaunchpadReportManager


class LaunchpadReport(Plugin):

    # Filename where submission information is cached.
    filename = Path(default="%(checkbox_data)s/submission.xml")

    # Prompt for place to save the submission file
    submission_path_prompt = String(default="")

    # XML Schema
    schema = Path(default="%(checkbox_share)s/report/hardware-1_0.rng")

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
             ("report-suites", self.report_suites),
             ("report-review", self.report_review),             
             ("report-tests", self.report_tests)]:
            self._manager.reactor.call_on(rt, rh)

        # Launchpad report should be generated last.
        self._manager.reactor.call_on("report", self.report, 100)

        #Ask where to put submission file
        self._manager.reactor.call_on("prompt-begin", self.prompt_begin, 110)

    def prompt_begin(self, interface):
        if self.submission_path_prompt:
            # Ignore whether to submit to HEXR
            new_filename = interface.show_entry(
                self.submission_path_prompt, self.filename)[0]
            if new_filename != "":
                self.filename = new_filename

    def report_attachments(self, attachments):
        for attachment in attachments:
            name = attachment["name"]
            if "sysfs_attachment" in name:
                self._report["hardware"]["sysfs-attributes"] = attachment["data"]

            elif "dmi_attachment" in name:
                self._report["hardware"]["dmi"] = attachment["data"]

            elif "udev_attachment" in name:
                self._report["hardware"]["udev"] = attachment["data"]

            elif all(c in printable for c in attachment["data"]):
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
        self.tests = tests
        for test in tests:
            question = {
                "name": test["name"],
                "answer": test["status"],
                "comment": test.get("data", "")}
            self._report["questions"].append(question)

    def report(self):
        # Prepare the payload and attach it to the form
        stylesheet_path = os.path.join(
            os.path.dirname(self.filename),
            os.path.basename(self.stylesheet))
        report_manager = LaunchpadReportManager(
            "system", "1.0", stylesheet_path, self.schema)
        payload = report_manager.dumps(self._report).toprettyxml("")

        # Write the report
        stylesheet_data = open(self.stylesheet).read() % os.environ
        open(stylesheet_path, "w").write(stylesheet_data)
        directory = os.path.dirname(self.filename)
        safe_make_directory(directory)
        open(self.filename, "w").write(payload)

        # Validate the report
        if not report_manager.validate(payload):
            self._manager.reactor.fire("report-error", _("""\
The generated report seems to have validation errors,
so it might not be processed by Launchpad."""))

        self._manager.reactor.fire("launchpad-report", self.filename)

    def report_review(self, interface):
        """
        Show test report in the interface
        """
        report = {}

        def add_job(job):
            is_suite = 'type' in job and job['type'] == 'suite'
            if 'suite' in job:
                suite_name = job['suite']
                parent_node = add_job(self.suites[suite_name])

                if is_suite:
                    if job['description'] in parent_node:
                        return parent_node[job['description']]

                    node = {}
                    parent_node[job['description']] = node
                    return node
                parent_node[job['name']] = job
            else:
                if is_suite:
                    field = 'description'
                else:
                    field = 'name'

                if job[field] in report:
                    return report[job[field]]

                node = {}
                report[job[field]] = node
                return node

        for test in self.tests:
            add_job(test)

        try:
            interface.show_report("Test case results report", report)
        except NotImplementedError:
            # Silently ignore the interfaces that don't implement the method
            pass

    def report_suites(self, suites):
        """
        Get tests results and store it
        to display them later
        """
        self.suites = dict([(suite['name'], suite) for suite in suites])


factory = LaunchpadReport
