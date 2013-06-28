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
import os
import re
import sys

import difflib
import gettext
import logging

from collections import defaultdict
from gettext import gettext as _

from checkbox.lib.resolver import Resolver

from checkbox.arguments import coerce_arguments
from checkbox.plugin import Plugin
from checkbox.properties import (
    Float,
    Int,
    List,
    Map,
    Path,
    String,
    )


job_schema = Map({
    "plugin": String(),
    "name": String(),
    "type": String(required=False),
    "status": String(required=False),
    "suite": String(required=False),
    "description": String(required=False),
    "purpose": String(required=False),
    "steps": String(required=False),
    "info": String(required=False),
    "verification": String(required=False),
    "command": String(required=False),
    "depends": List(String(), required=False),
    "duration": Float(required=False),
    "environ": List(String(), required=False),
    "requires": List(String(), separator=r"\n", required=False),
    "resources": List(String(), required=False),
    "estimated_duration": Int(required=False),
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

        self.whitelist_patterns = self.get_patterns(
            self.whitelist, self.whitelist_file)
        self.blacklist_patterns = self.get_patterns(
            self.blacklist, self.blacklist_file)
        self.selected_jobs = defaultdict(list)

        self._missing_dependencies_report = ""

        self._manager.reactor.call_on("prompt-begin", self.prompt_begin)
        self._manager.reactor.call_on("gather", self.gather)
        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
            self._manager.reactor.call_on(
                "prompt-gather", self.post_gather, 90)
        self._manager.reactor.call_on("report-job", self.report_job, -100)

    def prompt_begin(self, interface):
        """
        Capture interface object to use it later
        to display errors
        """
        self.interface = interface
        self.unused_patterns = (
            self.whitelist_patterns + self.blacklist_patterns)

    def check_ordered_messages(self, messages):
        """Return whether the list of messages are ordered or not.
           Also populates a _missing_dependencies_report string variable
           with a report of any jobs that are required but not present
           in the whitelist."""
        names_so_far = set()
        all_names = set([message['name'] for message in messages])
        messages_ordered = True
        missing_dependencies = defaultdict(set)

        for message in messages:
            name = message["name"]
            for dependency in message.get("depends", []):
                if dependency not in names_so_far:
                    messages_ordered = False
                #Two separate checks :) we *could* save a negligible
                #bit of time by putting this inside the previous "if"
                #but we're not in *that* big a hurry.
                if dependency not in all_names:
                    missing_dependencies[name].add(dependency)
            names_so_far.add(name)

        #Now assemble the list of missing deps into a nice report
        jobs_and_missing_deps = ["{} required by {}".format(job_name,
                                 ", ".join(missing_dependencies[job_name]))
                                 for job_name in missing_dependencies]
        self._missing_dependencies_report = "\n".join(jobs_and_missing_deps) 
        
        return messages_ordered

    def get_patterns(self, strings, filename=None):
        """Return the list of strings as compiled regular expressions."""
        if filename:
            try:
                file = open(filename)
            except IOError as e:
                error_message = (_("Failed to open file '%s': %s")
                    % (filename, e.strerror))
                logging.critical(error_message)
                sys.stderr.write("%s\n" % error_message)
                sys.exit(os.EX_NOINPUT)
            else:
                strings.extend([l.strip() for l in file.readlines()])

        return [re.compile(r"^%s$" % s) for s in strings
            if s and not s.startswith("#")]

    def get_unique_messages(self, messages):
        """Return the list of messages without any duplicates, giving
        precedence to messages that are the longest.
        """
        unique_messages = []
        unique_indexes = {}
        for message in messages:
            name = message["name"]
            index = unique_indexes.get(name)
            if index is None:
                unique_indexes[name] = len(unique_messages)
                unique_messages.append(message)
            elif len(message) > len(unique_messages[index]):
                unique_messages[index] = message

        return unique_messages

    def gather(self):
        # Register temporary handler for report-message events
        messages = []

        def report_message(message):
            if self.whitelist_patterns:
                name = message["name"]
                names = [name for p in self.whitelist_patterns
                    if p.match(name)]
                if not names:
                    return

            messages.append(message)

        # Set domain and message event handler
        old_domain = gettext.textdomain()
        gettext.textdomain(self.domain)
        event_id = self._manager.reactor.call_on(
            "report-message", report_message, 100)

        for directory in self.directories:
            self._manager.reactor.fire("message-directory", directory)

        for message in messages:
            self._manager.reactor.fire("report-job", message)

        # Unset domain and event handler
        self._manager.reactor.cancel_call(event_id)
        gettext.textdomain(old_domain)

        # Get unique messages from the now complete list
        messages = self.get_unique_messages(messages)

        # Apply whitelist ordering
        if self.whitelist_patterns:
            def key_function(obj):
                name = obj["name"]
                for pattern in self.whitelist_patterns:
                    if pattern.match(name):
                        return self.whitelist_patterns.index(pattern)

            messages = sorted(messages, key=key_function)

        if not self.check_ordered_messages(messages):
            #One of two things may have happened if we enter this code path.
            #Either the jobs are not in topological ordering,
            #Or they are in topological ordering but a dependency is
            #missing.
            old_message_names = [
                message["name"] + "\n" for message in messages]
            resolver = Resolver(key_func=lambda m: m["name"])
            for message in messages:
                resolver.add(
                    message, *message.get("depends", []))
            messages = resolver.get_dependents()

            if (self.whitelist_patterns and
                logging.getLogger().getEffectiveLevel() <= logging.DEBUG):
                new_message_names = [
                    message["name"] + "\n" for message in messages]
                #This will contain a report of out-of-order jobs.
                detailed_text = "".join(
                    difflib.unified_diff(
                        old_message_names,
                        new_message_names,
                        "old whitelist",
                        "new whitelist"))
                #First, we report missing dependencies, if any.
                if self._missing_dependencies_report:
                    primary = _("Dependencies are missing so some jobs "
                                "will not run.")
                    secondary = _("To fix this, close checkbox and add "
                                  "the missing dependencies to the "
                                  "whitelist.")
                    self._manager.reactor.fire("prompt-warning",
                            self.interface,
                            primary,
                            secondary,
                            self._missing_dependencies_report)
                #If detailed_text is empty, it means the problem
                #was missing dependencies, which we already reported.
                #Otherwise, we also need to report reordered jobs here.
                if detailed_text:
                    primary = _("Whitelist not topologically ordered")
                    secondary = _("Jobs will be reordered to fix broken "
                                  "dependencies")
                    self._manager.reactor.fire("prompt-warning",
                                               self.interface,
                                               primary,
                                               secondary,
                                               detailed_text)

        self._manager.reactor.fire("report-jobs", messages)

    def post_gather(self, interface):
        """
        Verify that all patterns were used
        """
        if logging.getLogger().getEffectiveLevel() > logging.DEBUG:
            return

        orphan_test_cases = []
        for name, jobs in self.selected_jobs.items():
            is_test = any(job.get('type') == 'test' for job in jobs)
            has_suite = any(job.get('suite') for job in jobs)
            if is_test and not has_suite:
                orphan_test_cases.append(name)

        if orphan_test_cases:
            detailed_error = \
                ('Test cases not included in any test suite:\n'
                 '{0}\n\n'
                 'This might cause problems '
                 'when uploading test cases results.\n'
                 'Please make sure that the patterns you used are up-to-date\n'
                 .format('\n'.join(['- {0}'.format(tc)
                                    for tc in orphan_test_cases])))
            self._manager.reactor.fire('prompt-warning', self.interface,
                                       'Orphan test cases detected',
                                       "Some test cases aren't included "
                                       'in any test suite',
                                       detailed_error)

        if self.unused_patterns:
            detailed_error = \
                ('Unused patterns:\n'
                 '{0}\n\n'
                 "Please make sure that the patterns you used are up-to-date\n"
                 .format('\n'.join(['- {0}'.format(p.pattern[1:-1])
                                        for p in self.unused_patterns])))
            self._manager.reactor.fire('prompt-warning', self.interface,
                                       'Unused patterns',
                                       'Please make sure that the patterns '
                                       'you used are up-to-date',
                                       detailed_error)

    @coerce_arguments(job=job_schema)
    def report_job(self, job):
        name = job["name"]

        patterns = self.whitelist_patterns or self.blacklist_patterns
        if patterns:
            match = next((p for p in patterns if p.match(name)), None)
            if match:
                # Keep track of which patterns didn't match any job
                if match in self.unused_patterns:
                    self.unused_patterns.remove(match)
                self.selected_jobs[name].append(job)
            else:
                # Stop if job not in whitelist or in blacklist
                self._manager.reactor.stop()


factory = JobsInfo
