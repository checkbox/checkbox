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
from gettext import gettext as _

from checkbox.job import Job, FAIL
from checkbox.plugin import Plugin
from checkbox.properties import String
from checkbox.registry import registry_eval_recursive


class BugPrompt(Plugin):

    # Command for reporting bugs
    command = String(default="ubuntu-bug @package@")

    def register(self, manager):
        super(BugPrompt, self).register(manager)

        self._manager.reactor.call_on("prompt-test", self.prompt_test, 100)

    def prompt_test(self, interface, test):
        if test["status"] == FAIL:
            for require in test.get("requires", []):
                packages = registry_eval_recursive(self._manager.registry.packages,
                    require)
                if packages:
                    package = packages[0].name
                    break
            else:
                package = "linux"

            command = self.command.replace("@package@", package)

            job = Job(command)
            interface.show_wait(_("Reporting bug..."),
                job.execute)


factory = BugPrompt
