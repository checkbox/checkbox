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
from checkbox.lib.iterator import NEXT

from checkbox.plugin import Plugin


class InternalSuite(Plugin):

    def register(self, manager):
        super(InternalSuite, self).register(manager)

        for (rt, rh) in [
             ("prompt-internal", self.prompt_internal),
             ("report-internal", self.report_internal)]:
            self._manager.reactor.call_on(rt, rh)

        self._manager.reactor.call_on("prompt-suite", self.prompt_suite, -100)

    def prompt_suite(self, interface, suite):
        if suite["plugin"] != "internal" and interface.direction == NEXT:
            self._manager.reactor.fire("prompt-tests", interface,
                blacklist=["plugin=manual"])

    def prompt_internal(self, interface, suite):
        self._manager.reactor.fire("prompt-tests", interface,
            whitelist=["plugin=manual"])

    def report_internal(self, suite):
        self._manager.reactor.fire("report-suite", suite)
        self._manager.reactor.fire("message-exec", suite)


factory = InternalSuite
