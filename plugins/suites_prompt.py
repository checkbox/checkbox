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

from checkbox.lib.iterator import IteratorExclude

from checkbox.job import JobIterator
from checkbox.properties import List, Path, String
from checkbox.plugin import Plugin

from gettext import gettext as _


class SuitesPrompt(Plugin):

    # Plugin default for running suite types
    plugin_default = String(default="external")

    # Plugin priorities for running suites
    plugin_priorities = List(String(), default_factory=lambda:"internal")

    # Space separated list of directories where suite files are stored.
    directories = List(Path(),
        default_factory=lambda:"%(checkbox_share)s/suites")

    # List of suites to blacklist
    blacklist = List(String(), default_factory=lambda:"")

    # List of suites to whitelist
    whitelist = List(String(), default_factory=lambda:"")

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
        whitelist_patterns = [re.compile(r"^%s$" % r) for r in self.whitelist if r]
        blacklist_patterns = [re.compile(r"^%s$" % r) for r in self.blacklist if r]

        name = suite["name"]
        if whitelist_patterns:
            if not [name for p in whitelist_patterns if p.match(name)]:
                return True
        elif blacklist_patterns:
            if [name for p in blacklist_patterns if p.match(name)]:
                return True

        suites_ignore = self.persist.get("ignore", [])
        if "description" in suite and suite["description"] in suites_ignore:
            return True

        return False

    def register(self, manager):
        super(SuitesPrompt, self).register(manager)
        self._iterator = None
        self._suite = None
        self._suites = {}

        for (rt, rh) in [
             ("gather", self.gather),
             ("gather-persist", self.gather_persist),
             ("report-suite", self.report_suite),
             ("prompt-suite", self.prompt_suite),
             ("prompt-suites", self.prompt_suites)]:
            self._manager.reactor.call_on(rt, rh)

        self._manager.reactor.call_on("prompt-gather", self.prompt_gather, 100)
        self._manager.reactor.call_on("report-(attachment|test)",
            self.report_attachment_or_test, -100)

    def gather(self):
        for directory in self.directories:
            self._manager.reactor.fire("message-directory", directory)

    def gather_persist(self, persist):
        self.persist = persist.root_at("suites_prompt")

    def report_attachment_or_test(self, element):
        if self._suite:
            element.setdefault("suite", self._suite["name"])

    def report_suite(self, suite):
        key = suite["name"]
        if key not in self._suites:
            suite.setdefault("plugin", self.plugin_default)
            self._suites[key] = suite
            self._iterator = JobIterator(self._suites.values(),
                self._manager.registry, self._suites_compare)
            self._iterator = IteratorExclude(self._iterator,
                self._suites_exclude, self._suites_exclude)
            if self._suite:
                for suite in self._iterator:
                    if suite == self._suite:
                        break

    def prompt_gather(self, interface):
        suites = [s for s in self._iterator]
        self._iterator = iter(self._iterator)
        if len(suites) > 1:
            suites_all = set([s["description"] for s in suites if "description" in s])
            suites_ignore = set(self.persist.get("ignore", []))
            suites_default = suites_all.difference(suites_ignore)
            suites_default = set(interface.show_check(
                _("Select the suites to test"),
                sorted(suites_all), suites_default))
            suites_ignore = suites_all.difference(suites_default)
            self.persist.set("ignore", list(suites_ignore))

    def prompt_suite(self, interface, suite):
        self._manager.reactor.fire("prompt-%s" % suite["plugin"],
            interface, suite)

    def prompt_suites(self, interface):
        while True:
            try:
                self._suite = self._iterator.go(interface.direction)
            except StopIteration:
                break

            self._manager.reactor.fire("prompt-suite", interface, self._suite)


factory = SuitesPrompt
