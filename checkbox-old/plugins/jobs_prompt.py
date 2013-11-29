#
# This file is part of Checkbox.
#
# Copyright 2010 Canonical Ltd.
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.

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

from checkbox.contrib.persist import Persist, MemoryBackend

from checkbox.job import JobStore, PASS, UNINITIATED, UNTESTED
from checkbox.properties import Int, Path
from checkbox.plugin import Plugin
from checkbox.user_interface import (
    NEXT,
    PREV,
    CONTINUE_ANSWER,
    RERUN_ANSWER,
)


class JobsPrompt(Plugin):

    # Directory where messages are stored
    store_directory = Path(default="%(checkbox_data)s/store")

    # Maximum number of messages per directory
    store_directory_size = Int(default=1000)

    @property
    def persist(self):
        if self._persist is None:
            self._persist = Persist(backend=MemoryBackend())

        return self._persist.root_at("jobs_prompt")

    @property
    def store(self):
        if self._store is None:
            self._store = JobStore(self.persist, self.store_directory,
                                   self.store_directory_size)

        return self._store

    def register(self, manager):
        super(JobsPrompt, self).register(manager)

        self._ignore = []
        self._persist = None
        self._store = None
        self._fail_current = False

        for (rt, rh) in [("expose-msgstore", self.expose_msgstore),
                         ("begin-persist", self.begin_persist),
                         ("begin-recover", self.begin_recover),
                         ("ignore-jobs", self.ignore_jobs),
                         ("prompt-job", self.prompt_job),
                         ("prompt-jobs", self.prompt_jobs),
                         ("prompt-finish", self.prompt_finish),
                         ("report", self.report),
                         ("report-job", self.report_job),
                         ("report-jobs", self.report_jobs)]:
            self._manager.reactor.call_on(rt, rh)

        #This should fire first thing during the gathering phase.
        self._manager.reactor.call_on("gather", self.begin_gather, -900)

        #This should fire last during gathering (i.e. after
        #all other gathering callbacks are finished)
        self._manager.reactor.call_on("gather", self.end_gather, 900)

    def expose_msgstore(self):
        self._manager.reactor.fire("store-access", self.store)

    def begin_persist(self, persist):
        self._persist = persist

    def begin_recover(self, recover):
        if recover == RERUN_ANSWER:
            logging.debug("Recovering from last job")
        elif recover == CONTINUE_ANSWER:
            logging.debug("Marking last job failed, starting from next job")
            self._fail_current = True
        else:
            self.store.delete_all_messages()

    def begin_gather(self):
        #Speed boost during the gathering phase. Not critical data anyway.
        self.store.safe_file_closing = False

    def end_gather(self):
        #Back to saving data very carefully once gathering is done.
        self.store.safe_file_closing = True

    def ignore_jobs(self, jobs):
        self._ignore = jobs

    def report_job(self, job):
        # Update job
        job.setdefault("status", UNINITIATED)
        self._manager.reactor.fire("report-%s" % job["plugin"], job)

    def report_jobs(self, jobs):
        for job in jobs:
            self.store.add(job)

    def prompt_job(self, interface, job):
        attribute = "description" if job.get("type") == "suite" else "name"
        if job[attribute] in self._ignore:
            job["status"] = UNTESTED
        else:
            if "depends" in job:
                offset = self.store.get_pending_offset()
                self.store.set_pending_offset(0)
                messages = self.store.get_pending_messages()
                self.store.set_pending_offset(offset)

                # Skip if any message in the depends doesn't pass
                depends = job["depends"]
                for message in messages:
                    if message["name"] in depends and \
                       message["status"] != PASS:
                        return

            self._manager.reactor.fire("prompt-%s" % job["plugin"],
                                       interface, job)

    def prompt_jobs(self, interface):
        while True:
            if interface.direction == PREV:
                if not self.store.remove_pending_offset():
                    break

            if self._fail_current:
                msg_to_fail = self.store.get_pending_messages(1)
                job_to_fail = msg_to_fail[0]
                job_to_fail["status"] = "fail"
                logging.warning("Marking job %s as failed"
                                "at user request" % job_to_fail["name"])
                self.store.update(job_to_fail)
                self.store.add_pending_offset()
                self._fail_current = False

            messages = self.store.get_pending_messages(1)
            if not messages:
                break

            done_count = self.store.get_pending_offset()
            pending_count = self.store.count_pending_messages()

            progress = (done_count, done_count + pending_count)
            self._manager.reactor.fire("set-progress", progress)

            job = messages[0]
            self._manager.reactor.fire("prompt-job", interface, job)
            self.store.update(job)

            if interface.direction == NEXT:
                self.store.add_pending_offset()

    def prompt_finish(self, interface):
        if interface.direction == NEXT:
            self.store.delete_all_messages()

    def report(self):
        self.store.set_pending_offset(0)
        messages = self.store.get_pending_messages()
        self.store.add_pending_offset(len(messages))

        tests = [m for m in messages if m.get("type") in ("test", "metric")]
        self._manager.reactor.fire("report-tests", tests)

        suites = [m for m in messages if m.get("type") == "suite"]
        self._manager.reactor.fire("report-suites", suites)

        attachments = [m for m in messages
                      if m.get("type") == "attachment" and "data" in m]
        self._manager.reactor.fire("report-attachments", attachments)


factory = JobsPrompt
