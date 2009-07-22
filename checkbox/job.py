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

from checkbox.lib.iterator import IteratorContain
from checkbox.lib.process import Process
from checkbox.lib.signal import signal_to_name, signal_to_description

from checkbox.depends import DependsIterator
from checkbox.requires import RequiresIterator


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

        self.data = None
        self.duration = -1
        self.status = UNINITIATED

    def execute(self):
        # Sanitize environment
        process_environ = dict(os.environ)
        for environ in self.environ:
            key, value = environ.split("=", 1)
            value = Template(value).substitute(process_environ)
            process_environ[key] = value

        logging.info("Running command: %s", self.command)
        process = Process(self.command, process_environ)
        if process.read(self.timeout):
            logging.info("Command timed out, killing process.")
            process.kill()

        status = process.cleanup()
        if os.WIFEXITED(status):
            exit_status = os.WEXITSTATUS(status)
            if exit_status == 0:
                self.status = PASS
                self.data = process.outdata
                if not self.data:
                    self.data = process.errdata
            elif exit_status == 127:
                self.status = UNRESOLVED
                self.data = _("Command not found.")
            else:
                self.status = FAIL
                self.data = process.errdata
        elif os.WIFSIGNALED(status):
            self.status = UNRESOLVED
            term_signal = os.WTERMSIG(status)
            self.data = _("Command received signal %s: %s") % \
                (signal_to_name(term_signal),
                 signal_to_description(term_signal))
        else:
            raise Exception, "Command not terminated: %s" \
                % self.command

        self.duration = process.endtime - process.starttime


class JobIterator(IteratorContain):

    def __init__(self, iterator, registry, compare=None):
        iterator = RequiresIterator(iterator, registry)
        iterator = DependsIterator(iterator, compare)

        super(JobIterator, self).__init__(iterator)
