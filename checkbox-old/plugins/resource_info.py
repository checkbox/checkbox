#
# This file is part of Checkbox.
#
# Copyright 2009 Canonical Ltd.
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.

#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.
#
from checkbox.job import UNSUPPORTED
from checkbox.plugin import Plugin
from checkbox.resource import ResourceMap


class ResourceInfo(Plugin):

    def register(self, manager):
        super(ResourceInfo, self).register(manager)

        self.resources = ResourceMap()

        self._manager.reactor.call_on("report-resource", self.report_resource)
        self._manager.reactor.call_on("prompt-job", self.prompt_job, -10)

    def prompt_job(self, interface, job):
        mask = []
        values = []
        failed_requirements = []

        for require in job.get("requires", []):
            new_values = self.resources.eval(require)
            mask.append(bool(new_values))

            if not bool(new_values):
                failed_requirements.append(require)

            if new_values is not None:
                values.extend(new_values)

        if all(mask):
            job["resources"] = values

        else:
            job["status"] = UNSUPPORTED

            data = "Job requirement%s not met:" % (
                's' if len(failed_requirements) > 1 else '')
            
            for failed_require in failed_requirements:
                data += " '" + failed_require + "'"
                
            job["data"] = data
            self._manager.reactor.stop()

    def report_resource(self, resource):
        # Register temporary handler for report-messages events
        def report_messages(messages):
            self.resources[resource["name"]] = messages
            self._manager.reactor.fire("report-%s" % resource["name"], messages)

            # Don't report other messages
            self._manager.reactor.stop()

        event_id = self._manager.reactor.call_on("report-messages", report_messages, -100)
        self._manager.reactor.fire("message-exec", resource)
        self._manager.reactor.cancel_call(event_id)


factory = ResourceInfo
