#
# This file is part of Checkbox.
#
# Copyright 2010 Canonical Ltd.
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
import gettext
import logging

from checkbox.arguments import coerce_arguments
from checkbox.properties import Float, Int, List, Map, Path, String, Unicode
from checkbox.plugin import Plugin


job_schema = Map({
    "plugin": String(),
    "name": String(),
    "type": String(required=False),
    "status": String(required=False),
    "suite": String(required=False),
    "description": Unicode(required=False),
    "command": String(required=False),
    "depends": List(String(), required=False),
    "duration": Float(required=False),
    "environ": List(String(), required=False),
    "requires": List(String(), separator=r"\n", required=False),
    "resources": List(String(), required=False),
    "timeout": Int(required=False),
    "user": String(required=False),
    "data": String(required=False)})


class JobsInfo(Plugin):

    # Domain for internationalization
    domain = String(default="checkbox")

    # Space separated list of directories where job files are stored.
    directories = List(Path(),
        default_factory=lambda:"%(checkbox_share)s/jobs")

    # List of jobs to blacklist
    blacklist = List(String(), default_factory=lambda:"")

    # Path to blacklist file
    blacklist_file = Path(required=False)

    # List of jobs to whitelist
    whitelist = List(String(), default_factory=lambda:"")

    # Path to whitelist file
    whitelist_file = Path(required=False)

    def register(self, manager):
        super(JobsInfo, self).register(manager)

        self.whitelist_patterns = self.get_patterns(self.whitelist, self.whitelist_file)
        self.blacklist_patterns = self.get_patterns(self.blacklist, self.blacklist_file)

        self._manager.reactor.call_on("gather", self.gather)
        self._manager.reactor.call_on("report-job", self.report_job, -100)

    def get_patterns(self, strings, filename=None):
        if filename:
            try:
                file = open(filename)
            except IOError, e:
                logging.info("Failed to open file '%s': %s",
                    filename, e.strerror)
            else:
                strings.extend([l.strip() for l in file.readlines()
                                if not l.startswith('#')])

        return [re.compile(r"^%s$" % s) for s in strings if s]

    def gather(self):
        # Register temporary handler for report-message events
        def report_message(message):
            self._manager.reactor.fire("report-job", message)

        # Set domain and message event handler
        old_domain = gettext.textdomain()
        gettext.textdomain(self.domain)
        event_id = self._manager.reactor.call_on("report-message", report_message, 100)

        for directory in self.directories:
            self._manager.reactor.fire("message-directory", directory)

        # Unset domain and event handler
        self._manager.reactor.cancel_call(event_id)
        gettext.textdomain(old_domain)

    @coerce_arguments(job=job_schema)
    def report_job(self, job):
        # Stop if job not in whitelist or in blacklist
        name = job["name"]
        if self.whitelist_patterns:
            if not [name for p in self.whitelist_patterns if p.match(name)]:
                self._manager.reactor.stop()
        elif self.blacklist_patterns:
            if [name for p in self.blacklist_patterns if p.match(name)]:
                self._manager.reactor.stop()


factory = JobsInfo
