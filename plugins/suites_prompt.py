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

from checkbox.lib.iterator import IteratorExclude
from checkbox.lib.resolver import Resolver

from checkbox.job import JobIterator
from checkbox.properties import List, String
from checkbox.plugin import Plugin

from gettext import gettext as _


class SuitesPrompt(Plugin):

    # Plugin priorities for running jobs
    plugin_priorities = List(String(), default_factory=lambda:"internal")

    def register(self, manager):
        super(SuitesPrompt, self).register(manager)
        self._iterator = None
        self._ignore = []
        self._suites = {}
        self._tests = {}

        for (rt, rh) in [
             ("gather-persist", self.gather_persist),
             ("ignore-jobs", self.ignore_jobs),
             ("report-suite", self.report_suite),
             ("report-test", self.report_test),
             ("prompt-suites", self.prompt_suites)]:
            self._manager.reactor.call_on(rt, rh)

        self._manager.reactor.call_on("prompt-gather", self.prompt_gather, 100)

    def gather_persist(self, persist):
        self.persist = persist.root_at("suites_prompt")

    def ignore_jobs(self, jobs):
        self._ignore = jobs

    def report_suite(self, suite):
        name = suite["name"]
        suite.update(self._suites.get(name, {}))
        suite.setdefault("type", "suite")
        self._suites[name] = suite

    def report_test(self, test):
        name = test["name"]
        self._tests[name] = test

    def prompt_gather(self, interface):
        # Resolve dependencies
        compare = lambda a, b: cmp(a["name"], b["name"])
        resolver = Resolver(compare=compare, key=lambda e: e["name"])
        jobs = dict((k, v) for k, v in self._suites.items() + self._tests.items())
        for job in jobs.values():
            depends = [jobs[job["suite"]]] if "suite" in job else []
            resolver.add(job, *depends)

        # Build options
        options = {}
        for job in resolver.get_dependents():
            suboptions = options
            dependencies = resolver.get_dependencies(job)
            for dependency in dependencies:
                if dependency.get("type") == "suite":
                    attribute = "description"
                else:
                    attribute = "name"

                suboptions = suboptions.setdefault(dependency[attribute], {})

        # Builds defaults
        defaults = self.persist.get("default")
        if defaults is None:
            defaults = copy.deepcopy(options)

        # Get results
        results = interface.show_tree(_("Select the suites to test"),
            options, defaults)
        self.persist.set("default", results)

        # Get tests to ignore
        def get_ignore_jobs(options, results):
            jobs = []
            for k, v in options.iteritems():
                if not v and k not in results:
                    jobs.append(k)

                else:
                    jobs.extend(get_ignore_jobs(options[k], results.get(k, {})))

            return jobs

        ignore_jobs = get_ignore_jobs(options, results)
        self._manager.reactor.fire("ignore-jobs", ignore_jobs)

    def prompt_suites(self, interface):
        if not self._iterator:
            self._iterator = JobIterator(self._suites.values(),
                self._manager.registry, self._suites_compare)
            self._iterator = IteratorExclude(self._iterator,
                self._suites_exclude, self._suites_exclude)

        while True:
            try:
                suite = self._iterator.go(interface.direction)
            except StopIteration:
                break

            self._manager.reactor.fire("prompt-job", interface, suite)

    def _suites_compare(self, a, b):
        priorities = self.plugin_priorities
        if a["plugin"] in priorities:
            if b["plugin"] in priorities:
                ia = priorities.index(a["plugin"])
                ib = priorities.index(b["plugin"])
                if ia != ib:
                    return cmp(ia, ib)
            else:
                return -1
        elif b["plugin"] in priorities:
            return 1

        return cmp(a["name"], b["name"])

    def _suites_exclude(self, suite):
        if "description" in suite and suite["description"] in self._ignore:
            return True

        return False


factory = SuitesPrompt
