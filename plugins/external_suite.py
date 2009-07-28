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
from checkbox.plugin import Plugin


class ExternalSuite(Plugin):

    def register(self, manager):
        super(ExternalSuite, self).register(manager)

        for (rt, rh) in [
             ("prompt-external", self.prompt_external),
             ("report-external", self.report_external)]:
            self._manager.reactor.call_on(rt, rh)

    def prompt_external(self, interface, suite):
        self._manager.reactor.fire("message-exec", suite)
        self._manager.reactor.fire("prompt-tests", interface)

    def report_external(self, suite):
        self._manager.reactor.fire("report-suite", suite)


factory = ExternalSuite
