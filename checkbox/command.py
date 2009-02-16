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

from checkbox.lib.process import Process
from checkbox.lib.environ import (get_variables, add_variable, remove_variable,
    get_paths, prepend_path, remove_path)


SUCCESS = 0
FAILURE = 1
ALL_STATUS = [SUCCESS, FAILURE]


class CommandResult(object):

    def __init__(self, command, status, stdout, stderr, start_time, end_time):
        self.command = command
        self.status = status
        self.stdout = stdout
        self.stderr = stderr
        self.start_time = start_time
        self.end_time = end_time

        self.if_exited = os.WIFEXITED(self.status)
        self.if_signaled = os.WIFSIGNALED(self.status)
        self.if_stopped = os.WIFSTOPPED(self.status)
        self.if_continued = os.WIFCONTINUED(self.status)

    @property
    def exit_status(self):
        if not self.if_exited:
            raise Exception, "Command not exited: %s" % self.command

        return os.WEXITSTATUS(self.status)

    @property
    def term_signal(self):
        if not self.if_signaled:
            raise Exception, "Command not signaled: %s" % self.command

        return os.WTERMSIG(self.status)

    @property
    def stop_signal(self):
        if not self.if_stopped:
            raise Exception, "Command not stopped: %s" % self.command

        return os.WSTOPSIG(self.status)

    @property
    def duration(self):
        if not self.end_time:
            raise Exception, "Command timed out: %s" % self.command

        return self.end_time - self.start_time


class Command(object):

    def __init__(self, command=None, timeout=None, paths=[], variables={}):
        self._command = command
        self._timeout = timeout
        self._paths = paths
        self._variables = variables

    def __str__(self):
        return self.get_command() or ""

    def __call__(self, *args, **kwargs):
        return self.execute(*args, **kwargs)

    def execute(self, *args, **kwargs):
        command = self.get_command()
        if command is None:
            return

        self.pre_execute(*args, **kwargs)

        # Sanitize environment
        env = get_variables()
        env["PATH"] = ":".join(get_paths())

        logging.info("Running command: %s", command)
        process = Process(command, env)
        if process.read(self._timeout):
            logging.info("Command timed out, killing process.")
            process.kill()

        status = process.cleanup()
        result = CommandResult(self, status, process.outdata, process.errdata,
            process.starttime, process.endtime)

        return self.post_execute(result)

    def pre_execute(self, *args, **kwargs):
        variables = self.get_variables()
        for key, value in variables.items():
            add_variable(key, value)

        paths = self.get_paths()
        for path in paths:
            prepend_path(path)

    def post_execute(self, result):
        paths = self.get_paths()
        for path in paths:
            remove_path(path)

        variables = self.get_variables()
        for key in variables.keys():
            remove_variable(key)

        return result

    def add_path(self, path):
        self._paths.append(path)

    def add_variable(self, key, value):
        self._variables[key] = value

    def get_command(self):
        return self._command

    def get_paths(self):
        return self._paths

    def get_variable(self, name, default=None):
        return self._variables.get(name, default)

    def get_variables(self):
        return self._variables
