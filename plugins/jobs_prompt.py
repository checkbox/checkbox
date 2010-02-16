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
import logging

from checkbox.arguments import coerce_arguments
from checkbox.job import JobStore, UNINITIATED, UNTESTED
from checkbox.properties import Float, Int, List, Map, Path, String, Unicode
from checkbox.plugin import Plugin
from checkbox.user_interface import NEXT, PREV


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


class JobsPrompt(Plugin):

    # Space separated list of directories where job files are stored.
    directories = List(Path(),
        default_factory=lambda:"%(checkbox_share)s/jobs")

    # Directory where messages are stored
    store_directory = Path(default="%(checkbox_data)s/store")

    # Maximum number of messages per directory
    store_directory_size = Int(default=1000)

    # List of jobs to blacklist
    blacklist = List(String(), default_factory=lambda:"")

    # Path to blacklist file
    blacklist_file = Path(required=False)

    # List of jobs to whitelist
    whitelist = List(String(), default_factory=lambda:"")

    # Path to whitelist file
    whitelist_file = Path(required=False)

    def register(self, manager):
        super(JobsPrompt, self).register(manager)
        self._ignore = []

        self.whitelist_patterns = self.get_patterns(self.whitelist, self.whitelist_file)
        self.blacklist_patterns = self.get_patterns(self.blacklist, self.blacklist_file)

        for (rt, rh) in [
             ("gather", self.gather),
             ("gather-persist", self.gather_persist),
             ("ignore-jobs", self.ignore_jobs),
             ("prompt-job", self.prompt_job),
             ("prompt-jobs", self.prompt_jobs),
             ("prompt-finish", self.prompt_finish),
             ("report", self.report)]:
            self._manager.reactor.call_on(rt, rh)

        self._manager.reactor.call_on("report-job", self.report_job, 100)

    def get_patterns(self, strings, filename=None):
        if filename:
            try:
                file = open(filename)
            except IOError, e:
                logging.info("Failed to open file '%s': %s",
                    filename, e.strerror)
            else:
                strings.extend([l.strip() for l in file.readlines()])

        return [re.compile(r"^%s$" % s) for s in strings if s]

    def gather(self):
        def report_message(message):
            self._manager.reactor.fire("report-job", message)

        event_id = self._manager.reactor.call_on("report-message", report_message, 100)
        for directory in self.directories:
            self._manager.reactor.fire("message-directory", directory)
        self._manager.reactor.cancel_call(event_id)

    def gather_persist(self, persist):
        persist = persist.root_at("jobs_prompt")
        self.store = JobStore(persist, self.store_directory,
            self.store_directory_size)

    def ignore_jobs(self, jobs):
        self._ignore = jobs

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

        # Update job
        job.setdefault("status", UNINITIATED)
        self._manager.reactor.fire("report-%s" % job["plugin"], job)

        self.store.add(job)

    def prompt_job(self, interface, job):
        attribute = "description" if job.get("type") == "suite" else "name"
        if job[attribute] in self._ignore:
            job["status"] = UNTESTED
        else:
            self._manager.reactor.fire("prompt-%s" % job["plugin"], interface, job)

    def prompt_jobs(self, interface):
        while True:
            if interface.direction == PREV:
                if not self.store.remove_pending_offset():
                    break

            messages = self.store.get_pending_messages(1)
            if not messages:
                break

            job = messages[0]
            self._manager.reactor.fire("prompt-job", interface, job)
            self.store.update(job)

            if interface.direction == NEXT:
                self.store.add_pending_offset()

    def prompt_finish(self, interface):
        self.store.delete_all_messages()

    def report(self):
        self.store.set_pending_offset(0)
        messages = self.store.get_pending_messages()
        tests = [m for m in messages if m.get("type") in ("test", "metric")]
        self._manager.reactor.fire("report-tests", tests)

        attachments = [m for m in messages if m.get("type") == "attachment" and "data" in m]
        self._manager.reactor.fire("report-attachments", attachments)


factory = JobsPrompt
