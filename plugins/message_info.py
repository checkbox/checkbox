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
import os
import re
import posixpath
import signal

from StringIO import StringIO

from checkbox.lib.path import path_expand_recursive
from checkbox.lib.template_i18n import TemplateI18n

from checkbox.parsers.description import DescriptionParser

from checkbox.job import Job, PASS
from checkbox.plugin import Plugin


class DescriptionResult:

    def __init__(self, message):
        self.message = message

    def setDescription(self, purpose, steps, verification):
        self.message["purpose"] = purpose
        self.message["steps"] = steps
        self.message["verification"] = verification


class MessageInfo(Plugin):

    def register(self, manager):
        super(MessageInfo, self).register(manager)

        for (rt, rh) in [
             ("report-messages", self.report_messages),
             ("message-directory", self.message_directory),
             ("message-exec", self.message_exec),
             ("message-file", self.message_file),
             ("message-filename", self.message_filename),
             ("message-result", self.message_result)]:
            self._manager.reactor.call_on(rt, rh)

    def report_messages(self, messages):
        for message in messages:
            self._manager.reactor.fire("report-message", message)

    def message_directory(self, directory, blacklist=[], whitelist=[]):
        whitelist_patterns = [re.compile(r"^%s$" % r) for r in whitelist if r]
        blacklist_patterns = [re.compile(r"^%s$" % r) for r in blacklist if r]

        for filename in path_expand_recursive(directory):
            name = posixpath.basename(filename)
            if name.startswith(".") or name.endswith("~"):
                continue

            if whitelist_patterns:
                if not [name for p in whitelist_patterns if p.match(name)]:
                    continue
            elif blacklist_patterns:
                if [name for p in blacklist_patterns if p.match(name)]:
                    continue

            self._manager.reactor.fire("message-filename", filename)

    def message_exec(self, message):
        if "user" not in message:

            def stop():
                os.kill(0, signal.SIGTERM)

            job = Job(message["command"], message.get("environ"),
                message.get("timeout"))

            # Kill the job if the stop event is fired during execution
            event_id = self._manager.reactor.call_on("stop", stop)
            result = job.execute()
            self._manager.reactor.cancel_call(event_id)

            self._manager.reactor.fire("message-result", *result)

    def message_file(self, file, filename="<stream>"):
        template = TemplateI18n()
        messages = template.load_file(file, filename)
        for message in messages:
            long_ext = "_extended"
            for long_key in message.keys():
                if long_key.endswith(long_ext):
                    short_key = long_key.replace(long_ext, "")
                    message[short_key] = message.pop(long_key)
            if "description" in message:
                parser = DescriptionParser(StringIO(message["description"]))
                result = DescriptionResult(message)
                parser.run(result)

        if messages:
            self._manager.reactor.fire("report-messages", messages)

    def message_filename(self, filename):
        file = open(filename, "r")
        self._manager.reactor.fire("message-file", file, filename)

    def message_result(self, status, data, duration):
        if status == PASS:
            file = StringIO(data)
            self._manager.reactor.fire("message-file", file)


factory = MessageInfo
