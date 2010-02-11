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
import re

from checkbox.job import UNINITIATED
from checkbox.properties import List, Path, String
from checkbox.plugin import Plugin


class JobsPrompt(Plugin):

    # Plugin default for running job types
    plugin_default = String(default="external")

    # Status default for jobs
    status_default = String(default=UNINITIATED)

    # Space separated list of directories where job files are stored.
    directories = List(Path(),
        default_factory=lambda:"%(checkbox_share)s/jobs")

    # List of jobs to blacklist
    blacklist = List(String(), default_factory=lambda:"")

    # List of jobs to whitelist
    whitelist = List(String(), default_factory=lambda:"")

    def register(self, manager):
        super(JobsPrompt, self).register(manager)
        self._iterator = None
        self._jobs = {}

        for (rt, rh) in [
             ("gather", self.gather),
             ("report-job", self.report_job),
             ("prompt-job", self.prompt_job)]:
            self._manager.reactor.call_on(rt, rh)

    def gather(self):
        for directory in self.directories:
            self._manager.reactor.fire("message-directory", directory)

    def report_job(self, job):
        whitelist_patterns = [re.compile(r"^%s$" % r) for r in self.whitelist if r]
        blacklist_patterns = [re.compile(r"^%s$" % r) for r in self.blacklist if r]

        # Stop if job not in whitelist or in blacklist
        name = job["name"]
        if whitelist_patterns:
            if not [name for p in whitelist_patterns if p.match(name)]:
                self._manager.reactor.stop()
        elif blacklist_patterns:
            if [name for p in blacklist_patterns if p.match(name)]:
                self._manager.reactor.stop()

        # Update job
        job.update(self._jobs.get(name, {}))
        job.setdefault("plugin", self.plugin_default)
        job.setdefault("status", self.status_default)
        self._jobs[name] = job

        self._manager.reactor.fire("report-%s" % job["plugin"], job)

    def prompt_job(self, interface, job):
        self._manager.reactor.fire("prompt-%s" % job["plugin"], interface, job)


factory = JobsPrompt
