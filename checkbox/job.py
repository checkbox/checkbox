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
import logging

from gettext import gettext as _
from string import Template

from checkbox.lib.process import Process
from checkbox.lib.signal import signal_to_name, signal_to_description

from checkbox.message import MessageStore


FAIL = "fail"
PASS = "pass"
UNINITIATED = "uninitiated"
UNRESOLVED = "unresolved"
UNSUPPORTED = "unsupported"
UNTESTED = "untested"

ALL_STATUS = [FAIL, PASS, UNINITIATED, UNRESOLVED, UNSUPPORTED, UNTESTED]


class Job(object):

    def __init__(self, command, environ=None, timeout=None):
        if environ is None:
            environ = []

        self.command = command
        self.environ = environ
        self.timeout = timeout

    def execute(self):
        # Sanitize environment
        process_environ = dict(os.environ)
        for environ in self.environ:
            key, value = environ.split("=", 1)
            value = Template(value).safe_substitute(process_environ)
            process_environ[key] = value

        logging.info("Running command: %s", self.command)
        process = Process(self.command, process_environ)
        if not process.read(self.timeout):
            logging.info("Command timed out, killing process.")
            process.kill()

        process_status = process.cleanup()
        if os.WIFEXITED(process_status):
            exit_status = os.WEXITSTATUS(process_status)
            if exit_status == 0:
                status = PASS
                data = process.outdata
                if not data:
                    data = process.errdata
            elif exit_status == 127:
                status = UNRESOLVED
                data = _("Command not found.")
            else:
                status = FAIL
                data = (process.errdata
                             or process.outdata)
        elif os.WIFSIGNALED(process_status):
            status = UNRESOLVED
            term_signal = os.WTERMSIG(process_status)
            data = _("Command received signal %s: %s") % \
                (signal_to_name(term_signal),
                 signal_to_description(term_signal))
        else:
            raise Exception, "Command not terminated: %s" \
                % self.command

        duration = process.endtime - process.starttime

        return (status, data, duration,)


class JobStore(MessageStore):
    """A job store which stores its jobs in a file system hierarchy."""

    def add(self, job):
        # TODO: Order alphabetically within suite or non-suite

        # Remove the same job if it already exists without a suite
        if "suite" in job:
            for filename in self._find_matching_messages(name=job["name"], suite=None):
                os.unlink(filename)

        # Return if the same job is already in the store
        if list(self._find_matching_messages(name=job["name"])):
            return

        message_id = super(JobStore, self).add(job)

        # TODO: Apply dependencies
        if "depends" in job:
            for depends in job["depends"]:
                for filename in self._find_matching_messages(suite=job.get("suite")):
                    message = self._read_message(filename)
                    if job["name"] in message.get("depends", []):
                        new_filename = self._get_next_message_filename()
                        os.rename(filename, new_filename)

        return message_id

    # TODO: Optimize by only searching backwards until a given condition
    def _find_matching_messages(self, **kwargs):
        for filename in self._walk_messages():
            message = self._read_message(filename)
            for key, value in kwargs.iteritems():
                if message.get(key) != value:
                    break
            else:
                yield filename
