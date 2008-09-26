#
# Copyright (c) 2008 Canonical
#
# Written by Marc Tardif <marc@interunion.ca>
#
# This file is part of Checkbox.
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

from checkbox.lib.template_i18n import TemplateI18n

from checkbox.plugin import Plugin
from checkbox.test import Test


class SuitesInfo(Plugin):

    required_attributes = ["directories", "scripts_path", "data_path"]
    optional_attributes = ["blacklist", "whitelist"]

    def register(self, manager):
        super(SuitesInfo, self).register(manager)
        self._manager.reactor.call_on("gather", self.gather)

    def gather(self):
        directories = re.split("\s+", self._config.directories)
        blacklist = self._config.blacklist \
            and re.split("\s+", self._config.blacklist) or []
        whitelist = self._config.whitelist \
            and re.split("\s+", self._config.whitelist) or []
        template = TemplateI18n("suite", ["name"])
        elements = template.load_directories(directories, blacklist, whitelist)

        for element in elements:
            long_ext = "_extended"
            for long_key in element.keys():
                if long_key.endswith(long_ext):
                    short_key = long_key.replace(long_ext, "")
                    element[short_key] = element.pop(long_key)

            test = Test(self._manager.registry, **element)
            for command in test.command, test.description:
                command.add_path(self._config.scripts_path)
                command.add_variable("data_path", self._config.data_path)

            self._manager.reactor.fire("test-%s" % test.plugin, test)


factory = SuitesInfo
