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
import copy

from checkbox.contrib.persist import Persist, MemoryBackend

from checkbox.lib.resolver import Resolver

from checkbox.plugin import Plugin
from checkbox.user_interface import PREV

from gettext import gettext as _


class SuitesPrompt(Plugin):

    @property
    def persist(self):
        if self._persist is None:
            self._persist = Persist(backend=MemoryBackend())

        return self._persist.root_at("suites_prompt")

    def register(self, manager):
        super(SuitesPrompt, self).register(manager)

        self._depends = {}
        self._jobs = {}
        self._persist = None
        self._recover = False 

        for (rt, rh) in [
             ("begin-persist", self.begin_persist),
             ("begin-recover", self.begin_recover),
             ("report-suite", self.report_suite)]:
            self._manager.reactor.call_on(rt, rh)

        for (rt, rh) in [
             ("prompt-gather", self.prompt_gather),
             ("report-suite", self.report_job),
             ("report-test", self.report_job)]:
            self._manager.reactor.call_on(rt, rh, 100)

    def begin_persist(self, persist):
        self._persist = persist

    def begin_recover(self, recover):
        self._recover = recover

    def report_suite(self, suite):
        suite.setdefault("type", "suite")

    def report_job(self, job):
        if job.get("type") == "suite":
            attribute = "description"
        else:
            attribute = "name"

        if attribute in job:
            self._jobs[job["name"]] = job[attribute]
            if "suite" in job:
                self._depends[job["name"]] = [job["suite"]]

    def prompt_gather(self, interface):
        # Resolve dependencies
        resolver = Resolver()
        for key in self._jobs.iterkeys():
            depends = self._depends.get(key, [])
            resolver.add(key, *depends)

        # Build options
        options = {}
        for job in resolver.get_dependents():
            suboptions = options
            dependencies = resolver.get_dependencies(job)
            for dependency in dependencies:
                suboptions = suboptions.setdefault(self._jobs[dependency], {})

        # Build defaults
        defaults = self.persist.get("default")
        if defaults is None:
            defaults = copy.deepcopy(options)

        # Only prompt if not recovering
        if interface.direction == PREV or not self._recover:
            self._recover = False

            # Get results
            defaults = interface.show_tree(_("Select the suites to test"),
                options, defaults)
            self.persist.set("default", defaults)

        # Get tests to ignore
        def get_ignore_jobs(options, results):
            jobs = []
            for k, v in options.iteritems():
                if not v and k not in results:
                    jobs.append(k)

                else:
                    jobs.extend(get_ignore_jobs(options[k], results.get(k, {})))

            return jobs

        ignore_jobs = get_ignore_jobs(options, defaults)
        self._manager.reactor.fire("ignore-jobs", ignore_jobs)


factory = SuitesPrompt
