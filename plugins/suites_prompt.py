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
        suites_default = self.persist.get("default")
        if suites_default is not None and \
           suite["description"] not in suites_default:
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
             ("prompt-suites", self.prompt_suites)]:
            self._manager.reactor.call_on(rt, rh)

        self._manager.reactor.call_on("prompt-gather", self.prompt_gather, 100)
        self._manager.reactor.call_on("report-test", self.report_test, -100)

    def gather(self):
        for directory in self.directories:
            self._manager.reactor.fire("message-directory",
                directory, self.blacklist, self.whitelist)

    def gather_persist(self, persist):
        self.persist = persist.root_at("suites_prompt")

    def report_suite(self, suite):
        key = suite["name"]
        if key not in self._suites:
            suite.setdefault("plugin", self.plugin_default)
            self._suites[key] = suite

    def report_test(self, test):
        test.setdefault("suite", self._suite["name"])

    def prompt_gather(self, interface):
        suites = self._suites.values()
        if len(suites) > 1:
            suites_table = dict((s["description"], s) for s in suites)
            suites_default = self.persist.get("default", suites_table)
            suites_default = interface.show_check(
                _("Select the suites to test"),
                sorted(suites_table.keys()),
                suites_default)
            self.persist.set("default", suites_default)

        self._iterator = JobIterator(suites,
            self._manager.registry, self._suites_compare)
        self._iterator = IteratorExclude(self._iterator,
            self._suites_exclude, self._suites_exclude)

    def prompt_suites(self, interface):
        while True:
            try:
                self._suite = self._iterator.go(interface.direction)
            except StopIteration:
                break

            self._manager.reactor.fire(
                "prompt-suite-%s" % self._suite["plugin"],
                interface, self._suite)


factory = SuitesPrompt
