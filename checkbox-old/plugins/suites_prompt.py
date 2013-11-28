#
# This file is part of Checkbox.
#
# Copyright 2008 Canonical Ltd.
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
import copy

from checkbox.contrib.persist import Persist, MemoryBackend

from checkbox.job import UNINITIATED

from checkbox.lib.resolver import Resolver

from checkbox.plugin import Plugin
from checkbox.properties import String
from checkbox.user_interface import CONTINUE_ANSWER, RERUN_ANSWER

from gettext import gettext as _


class SuitesPrompt(Plugin):

    deselect_warning = String(default="")

    @property
    def persist(self):
        if self._persist is None:
            self._persist = Persist(backend=MemoryBackend())

        return self._persist.root_at("suites_prompt")

    def register(self, manager):
        super(SuitesPrompt, self).register(manager)

        self._depends = {}
        self._jobs = {}
        self._statuses = {}
        self._persist = None
        self._recover = False

        for (rt, rh) in [
             ("begin-persist", self.begin_persist),
             ("begin-recover", self.begin_recover),
             ("report-suite", self.report_suite),
             ("store-access", self.store_access)]:
            self._manager.reactor.call_on(rt, rh)

        for (rt, rh) in [
             ("prompt-gather", self.prompt_gather),
             ("report-suite", self.report_job),
             ("report-test", self.report_job)]:
            self._manager.reactor.call_on(rt, rh, 100)

    def begin_persist(self, persist):
        self._persist = persist

    def begin_recover(self, recover):
        if recover in [CONTINUE_ANSWER, RERUN_ANSWER]:
            self._recover = True

        if not self._recover:
            self.persist.remove("default")

    def report_suite(self, suite):
        suite.setdefault("type", "suite")

    def store_access(self, store):
        self.store = store

    def report_job(self, job):
        if job.get("type") == "suite":
            attribute = "description"
        else:
            attribute = "name"

        if attribute in job:
            self._jobs[job["name"]] = job[attribute]
            if "suite" in job:
                self._depends[job["name"]] = [job["suite"]]
            if job.get("type") == "test":
                self._statuses[job["name"]] = job["status"]

    def prompt_gather(self, interface):
        # Resolve dependencies
        interface.show_progress_start(_("Gathering information from your system..."))
        resolver = Resolver()
        for key in self._jobs.keys():
            depends = self._depends.get(key, [])
            resolver.add(key, *depends)

        # Build options
        options = {}
        self._manager.reactor.fire("expose-msgstore")
        offset = self.store.get_pending_offset()
        self.store.set_pending_offset(0)
        messages = self.store.get_pending_messages()
        self.store.add_pending_offset(offset)
        tests = dict([(m["name"], m) for m in messages
              if m.get("type") in ("test", "metric")])

        def walk_dependencies(job, all_dependencies):
            for dependency in resolver.get_dependencies(job)[:-1]:
                walk_dependencies(dependency, all_dependencies)
            all_dependencies.append(job)

        for job in resolver.get_dependents():
            suboptions = options
            dependencies = []
            walk_dependencies(job, dependencies)
            for dependency in dependencies:
                if dependency in tests:
                    value = tests[dependency]["status"]
                else:
                    value = self._statuses.get(dependency, {})
                suboptions = suboptions.setdefault(self._jobs[dependency],
                                                   value)

        # Build defaults
        defaults = self.persist.get("default")
        if defaults is None:
            defaults = copy.deepcopy(options)

        # Get results
        interface.show_progress_stop()
        defaults = interface.show_tree(
            _("Choose tests to run on your system:"),
            options, defaults, self.deselect_warning)
        self.persist.set("default", defaults)

        # Get tests to ignore
        def get_ignore_jobs(options, results):
            jobs = []
            if isinstance(options, dict):
                for k, v in options.items():
                    if v == UNINITIATED and k not in results:
                        jobs.append(k)
                    else:
                        jobs.extend(get_ignore_jobs(options[k],
                                                    results.get(k, {})))

            return jobs

        ignore_jobs = get_ignore_jobs(options, defaults)
        self._manager.reactor.fire("ignore-jobs", ignore_jobs)


factory = SuitesPrompt
