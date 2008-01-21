import os
import logging
from subprocess import Popen, PIPE

from hwtest.answer import YES, NO, SKIP
from hwtest.lib.environ import (add_variable, remove_variable, add_path,
    remove_path)


class Command(object):

    def __init__(self, command="", paths=[], variables={}):
        self._command = command or ""
        self._paths = paths
        self._variables = variables

        self._status = SKIP
        self._data = ""

    def __str__(self):
        return self.get_command()

    def __call__(self):
        self.execute()

    def execute(self, timeout=None):
        command = self.get_command()
        if not command:
            return

        self.pre_execute()

        logging.info("Running command: %s" % command)
        process = Popen([command], shell=True,
            stdin=None, stdout=PIPE, stderr=PIPE,
            close_fds=True)
        (stdout, stderr) = process.communicate()
        wait = process.wait()

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
            self.set_status(YES)
        elif exit_code == 127:
            self.set_status(SKIP)
            self.set_data("Failed to run command, skipping.")
        else:
            self.set_status(NO)

            if exit_code > 128:
                signal = exit_code - 128
                self.set_data("Received signal %s: %s" %
                    (signal_to_name(signal),
                     signal_to_description(signal)))
            else:
                self.set_data("Returned exit code: %d" % exit_code)

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
