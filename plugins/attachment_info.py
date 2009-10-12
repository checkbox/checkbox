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
from checkbox.job import Job, FAIL, UNINITIATED
from checkbox.plugin import Plugin

from gettext import gettext as _


class AttachmentInfo(Plugin):

    def register(self, manager):
        super(AttachmentInfo, self).register(manager)
        self._attachments = []

        for (rt, rh) in [
             ("report", self.report),
             ("report-attachment", self.report_attachment)]:
            self._manager.reactor.call_on(rt, rh)

        self._manager.reactor.call_on("prompt-test", self.prompt_test, 100)

    def prompt_test(self, interface, test):
        if test.get("status", UNINITIATED) != FAIL:
            return

        attachments = []
        for attachment in self._attachments:
            if test["suite"] == attachment.get("suite", None) and \
               test["name"] in attachment.get("depends", []):
                job = Job(attachment["command"], attachment.get("environ"),
                    attachment.get("timeout"), attachment.get("user"))
                (status, data, duration) = interface.show_progress(
                    _("Running attachment..."), job.execute)
                attachment = dict(attachment)
                attachment["test"] = test["name"]
                attachment["suite"] = test["suite"]
                attachment["data"] = data
                attachment["duration"] = duration
                attachment["status"] = status
                attachments.append(attachment)

        if attachments:
            self._manager.reactor.fire("report-attachments", attachments)

    def report(self):
        attachments = []
        for attachment in self._attachments:
            if not attachment.get("depends", []):
                job = Job(attachment["command"], attachment.get("environ"),
                    attachment.get("timeout"))
                (status, data, duration) = job.execute()
                attachment = dict(attachment)
                attachment["data"] = data
                attachment["duration"] = duration
                attachment["status"] = status
                attachments.append(attachment)

        if attachments:
            self._manager.reactor.fire("report-attachments", attachments)

    def report_attachment(self, attachment):
        if "command" in attachment:
            self._attachments.append(attachment)


factory = AttachmentInfo
