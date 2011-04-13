#
# This file is part of Checkbox.
#
# Copyright 2010 Canonical Ltd.
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
import os, sys, re
import gettext
import logging

from checkbox.arguments import coerce_arguments
from checkbox.properties import Float, Int, List, Map, Path, String, Unicode
from checkbox.plugin import Plugin


job_schema = Map({
    "plugin": String(),
    "name": String(),
    "type": String(required=False),
    "status": String(required=False),
    "suite": String(required=False),
    "description": Unicode(required=False),
    "purpose": Unicode(required=False),
    "steps": Unicode(required=False),
    "info": Unicode(required=False),
    "verification": Unicode(required=False),
    "command": String(required=False),
    "depends": List(String(), required=False),
    "duration": Float(required=False),
    "environ": List(String(), required=False),
    "requires": List(String(), separator=r"\n", required=False),
    "resources": List(String(), required=False),
    "timeout": Int(required=False),
    "user": String(required=False),
    "data": String(required=False)})


class JobsInfo(Plugin):

    # Domain for internationalization
    domain = String(default="checkbox")

    # Space separated list of directories where job files are stored.
    directories = List(Path(),
        default_factory=lambda: "%(checkbox_share)s/jobs")

    # List of jobs to blacklist
    blacklist = List(String(), default_factory=lambda: "")

    # Path to blacklist file
    blacklist_file = Path(required=False)

    # List of jobs to whitelist
    whitelist = List(String(), default_factory=lambda: "")

    # Path to whitelist file
    whitelist_file = Path(required=False)

    def register(self, manager):
        super(JobsInfo, self).register(manager)

        self.whitelist_patterns = self.get_patterns(self.whitelist, self.whitelist_file)
        self.blacklist_patterns = self.get_patterns(self.blacklist, self.blacklist_file)

        self._manager.reactor.call_on("prompt-begin", self.prompt_begin)
        self._manager.reactor.call_on("gather", self.gather)
        self._manager.reactor.call_on("gather", self.post_gather, 100)
        self._manager.reactor.call_on("report-job", self.report_job, -100)


    def prompt_begin(self, interface):
        """
        Capture interface object to use it later
        to display errors
        """
        self.interface = interface
        self.unused_patterns = self.whitelist_patterns + self.blacklist_patterns

    def get_patterns(self, strings, filename=None):
        if filename:
            try:
                file = open(filename)
            except IOError, e:
                error_message=(gettext.gettext("Failed to open file '%s': %s") %
                        (filename, e.strerror))
                logging.critical(error_message)
                sys.stderr.write("%s\n" % error_message)
                sys.exit(os.EX_NOINPUT)
            else:
                strings.extend([l.strip() for l in file.readlines()])

        return [re.compile(r"^%s$" % s) for s in strings
            if s and not s.startswith("#")]


    def gather(self):
        # Register temporary handler for report-message events
        messages = []

        def report_message(message):
            if self.whitelist_patterns:
                name = message["name"]
                if not [name for p in self.whitelist_patterns if p.match(name)]:
                    return

            messages.append(message)

        # Set domain and message event handler
        old_domain = gettext.textdomain()
        gettext.textdomain(self.domain)
        event_id = self._manager.reactor.call_on("report-message", report_message, 100)

        for directory in self.directories:
            self._manager.reactor.fire("message-directory", directory)

        # Apply whitelist ordering
        def cmp_function(a, b):
            a_name = a["name"]
            b_name = b["name"]
            for pattern in self.whitelist_patterns:
                if pattern.match(a_name):
                    a_index = self.whitelist_patterns.index(pattern)
                elif pattern.match(b_name):
                    b_index = self.whitelist_patterns.index(pattern)

            return cmp(a_index, b_index)

        if self.whitelist_patterns:
            messages = sorted(messages, cmp=cmp_function)
        for message in messages:
            self._manager.reactor.fire("report-job", message)

        # Unset domain and event handler
        self._manager.reactor.cancel_call(event_id)
        gettext.textdomain(old_domain)


    def post_gather(self):
        """
        Verify that all patterns were used
        """
        if self.unused_patterns:
            error = ('Unused patterns:\n'
                     '{0}\n\n'
                     "Please make sure that the patterns you used aren't outdated?\n"
                     .format('\n'.join(['- {0}'.format(p.pattern[1:-1])
                                        for p in self.unused_patterns])))
            self._manager.reactor.fire('prompt-error', self.interface, error)


    @coerce_arguments(job=job_schema)
    def report_job(self, job):
        name = job["name"]

        patterns = self.whitelist_patterns or self.blacklist_patterns
        match = next((p for p in patterns if p.match(name)), None)
        if match:
            # Keep track of which patterns didn't match any job
            if match in self.unused_patterns:
                self.unused_patterns.remove(match)
        else:
            # Stop if job not in whitelist or in blacklist
            self._manager.reactor.stop()


factory = JobsInfo
