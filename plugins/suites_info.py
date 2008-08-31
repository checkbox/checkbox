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
        self.results = {}

        for (rt, rh) in [
             ("gather", self.gather),
             ("report", self.report),
             ("report-result", self.report_result)]:
            self._manager.reactor.call_on(rt, rh)

    def gather(self):
        directories = re.split("\s+", self.config.directories)
        blacklist = self.config.blacklist \
            and re.split("\s+", self.config.blacklist) or []
        whitelist = self.config.whitelist \
            and re.split("\s+", self.config.whitelist) or []
        template = TemplateI18n("suite", ["name"])
        elements = template.load_directories(directories, blacklist, whitelist)

        for element in elements:
            if "description_extended" in element:
                element["description"] = element.pop("description_extended")

            test = Test(self._manager.registry, **element)
            for command in test.command, test.description:
                command.add_path(self.config.scripts_path)
                command.add_variable("data_path", self.config.data_path)

            self._manager.reactor.fire("test-%s" % test.plugin, test)

    def report_result(self, result):
        self.results[result.test.name] = result

    def report(self):
        message = []
        for result in self.results.values():
            test = result.test
            attributes = dict(test.attributes)
            attributes["command"] = str(test.command)
            attributes["description"] = str(test.description)
            attributes["requires"] = str(test.requires)
            attributes["result"] = dict(result.attributes)

            message.append(attributes)

        self._manager.reactor.fire("report-results", message)


factory = SuitesInfo
