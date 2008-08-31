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
import os
import logging

from checkbox.result import Result, PASS, FAIL, SKIP
from checkbox.lib.process import Process
from checkbox.lib.signal import signal_to_name, signal_to_description
from checkbox.lib.environ import (get_variables, add_variable, remove_variable,
    get_paths, add_path, remove_path)


class Command(object):

    def __init__(self, command=None, timeout=None,
            paths=[], variables={}):
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

            result = Result(self)
            result.duration = self._timeout
            result.data = "Command timed out after %s seconds" \
                % self._timeout
        else:
            stdout = process.outdata
            stderr = process.errdata
            wait = process.cleanup()

            result = self.parse_process(stdout, stderr, wait)
            result.duration = int(process.endtime - process.starttime)

        self.post_execute(result)
        return result

    def pre_execute(self, *args, **kwargs):
        variables = self.get_variables()
        for key, value in variables.items():
            add_variable(key, value)

        paths = self.get_paths()
        for path in paths:
            add_path(path)

    def post_execute(self, result):
        paths = self.get_paths()
        for path in paths:
            remove_path(path)

        variables = self.get_variables()
        for key in variables.keys():
            remove_variable(key)

    def parse_process(self, stdout, stderr, wait):
        result = Result(self)

        # Ordering is relevant
        parse_table = [
            [self.parse_wait, wait],
            [self.parse_stdout, stdout],
            [self.parse_stderr, stderr]]

        for parse_func, parse_string in parse_table:
            parse_func(result, parse_string)
            if result.data:
                break

        return result

    def parse_stdout(self, result, stdout):
        result.data = stdout

    def parse_stderr(self, result, stderr):
        result.data = stderr

    def parse_wait(self, result, wait):
        exit_code = os.WEXITSTATUS(wait)
        if exit_code == 0:
            result.status = PASS
        elif exit_code == 127:
            result.status = SKIP
            result.data = "Command failed, skipping."
        else:
            result.status = FAIL

            if exit_code > 128:
                signal = exit_code - 128
                result.data = "Received signal %s: %s" % \
                    (signal_to_name(signal),
                     signal_to_description(signal))

    def add_path(self, path):
        self._paths.append(path)

    def add_variable(self, key, value):
        self._variables[key] = value

    def get_command(self):
        return self._command

    def get_paths(self):
        return self._paths

    def get_variables(self):
        return self._variables
