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
from checkbox.lib.template_i18n import TemplateI18n

from checkbox.properties import List, Path, String
from checkbox.plugin import Plugin
from checkbox.test import Test


class SuitesInfo(Plugin):

    # Space separated list of directories where suite files are stored.
    directories = List(type=Path(),
        default_factory=lambda:"%(checkbox_share)s/suites")

    # Executable path for running scripts. These might be
    # referenced from the above suites for example.
    scripts_path = Path(default="%(checkbox_share)s/scripts")

    # Data path containing files for scripts.
    data_path = Path(default="%(checkbox_share)s/data")

    # List of suites to blacklist
    blacklist = List(type=String(), default_factory=lambda:"")

    # List of suites to whitelist
    whitelist = List(type=String(), default_factory=lambda:"")

    def register(self, manager):
        super(SuitesInfo, self).register(manager)
        self._manager.reactor.call_on("gather", self.gather)

    def gather(self):
        template = TemplateI18n("suite", ["name"])
        elements = template.load_directories(self.directories,
            self.blacklist, self.whitelist)

        for element in elements:
            long_ext = "_extended"
            for long_key in element.keys():
                if long_key.endswith(long_ext):
                    short_key = long_key.replace(long_ext, "")
                    element[short_key] = element.pop(long_key)

            test = Test(self._manager.registry, **element)
            for command in test.command, test.description:
                command.add_path(self.scripts_path)
                command.add_variable("data_path", self.data_path)

            self._manager.reactor.fire("test-%s" % test.plugin, test)


factory = SuitesInfo
