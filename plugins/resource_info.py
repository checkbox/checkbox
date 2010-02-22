#
# This file is part of Checkbox.
#
# Copyright 2009 Canonical Ltd.
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
from checkbox.job import UNSUPPORTED
from checkbox.plugin import Plugin
from checkbox.resource import Resource


class ResourceInfo(Plugin):

    def register(self, manager):
        super(ResourceInfo, self).register(manager)

        self.resources = []

        self._manager.reactor.call_on("report-resource", self.report_resource)
        self._manager.reactor.call_on("prompt-job", self.prompt_job, -10)

    def prompt_job(self, interface, job):
        mask = []
        values = []
        for require in job.get("requires", []):
            new_values = []
            for resource in self.resources:
                if resource.eval(require) is not None:
                        new_values.append(resource)

            mask.append(bool(new_values))
            values.extend(new_values)

        if all(mask):
            job["resources"] = values

        else:
            job["status"] = UNSUPPORTED
            job["data"] = "Job requirements not met."
            self._manager.reactor.stop()

    def report_resource(self, resource):
        # Register temporary handler for report-messages events
        def report_messages(messages):
            for message in messages:
                message = Resource(message)
                message = Resource({resource["name"]: message})
                self.resources.append(message)

            self._manager.reactor.fire("report-%s" % resource["name"], messages)

            # Don't report other messages
            self._manager.reactor.stop()

        event_id = self._manager.reactor.call_on("report-messages", report_messages, -100)
        self._manager.reactor.fire("message-exec", resource)
        self._manager.reactor.cancel_call(event_id)


factory = ResourceInfo
