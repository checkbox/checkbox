#
# Copyright (c) 2008 Canonical
#
# Written by Marc Tardif <marc@interunion.ca>
#
# This file is part of HWTest.
#
# HWTest is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HWTest is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HWTest.  If not, see <http://www.gnu.org/licenses/>.
#
import os
import logging

from hwtest.result import PASS, FAIL, SKIP
from hwtest.lib.process import Process
from hwtest.lib.signal import signal_to_name, signal_to_description
from hwtest.lib.environ import (get_variables, add_variable, remove_variable,
    get_paths, add_path, remove_path)


class Command(object):

    paths = []
    variables = {}

    def __init__(self, command="", timeout=None):
        self._command = command
        self._timeout = timeout

        self._data = ""
        self._status = SKIP

        self._paths = list(self.paths)
        self._variables = dict(self.variables)

    def __str__(self):
        return self.get_command()

    def __call__(self):
        self.execute()
        return str(self)

    def execute(self):
        command = self.get_command()
        if not command:
            return

        self.pre_execute()

        # Sanitize environment
        env = get_variables()
        env["PATH"] = ":".join(get_paths())

        logging.info("Running command: %s" % command)
        process = Process(command, env)
        if process.read(self._timeout):
            logging.info("Command timed out, killing process.")
            process.kill()

            self.set_data("Command timed out after %s seconds" % self._timeout)
            self.set_status(SKIP)
            self.post_execute()
            return

        stdout = process.outdata
        stderr = process.errdata
        wait = process.cleanup()

        self.post_execute()
        self.parse_process(stdout, stderr, wait)

    def pre_execute(self):
        variables = self.get_variables()
        for key, value in variables.items():
            add_variable(key, value)

        paths = self.get_paths()
        for path in paths:
            add_path(path)

    def post_execute(self):
        paths = self.get_paths()
        for path in paths:
            remove_path(path)

        variables = self.get_variables()
        for key in variables.keys():
            remove_variable(key)

    def parse_process(self, stdout, stderr, wait):
        # Ordering is relevant
        parse_table = [
            [self.parse_wait, wait],
            [self.parse_stdout, stdout],
            [self.parse_stderr, stderr]]

        for parse_func, parse_string in parse_table:
            parse_func(parse_string)
            if self.get_data():
                break

    def parse_stdout(self, stdout):
        self.set_data(stdout)

    def parse_stderr(self, stderr):
        self.set_data(stderr)

    def parse_wait(self, wait):
        exit_code = os.WEXITSTATUS(wait)
        if exit_code == 0:
            self.set_status(PASS)
        elif exit_code == 127:
            self.set_status(SKIP)
            self.set_data("Command failed, skipping.")
        else:
            self.set_status(FAIL)

            if exit_code > 128:
                signal = exit_code - 128
                self.set_data("Received signal %s: %s" %
                    (signal_to_name(signal),
                     signal_to_description(signal)))

    def add_path(self, path):
        self._paths.append(path)

    def add_variable(self, key, value):
        self._variables[key] = value

    def set_status(self, status):
        self._status = status

    def set_data(self, data):
        self._data = data

    def get_command(self):
        return self._command

    def get_paths(self):
        return self._paths

    def get_variables(self):
        return self._variables

    def get_status(self):
        return self._status

    def get_data(self):
        return self._data
