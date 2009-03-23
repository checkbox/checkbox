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
"""
The purpose of this module is to encapsulate the concept of a test
which might be presented in several ways. For example, a test might
require manual intervention whereas another test might be completely
automatic. Either way, this module provides the base common to each type
of test.
"""

import re
import logging

from gettext import gettext as _

from checkbox.lib.environ import add_variable, remove_variable
from checkbox.lib.signal import signal_to_name, signal_to_description

from checkbox.command import Command
from checkbox.frontend import frontend
from checkbox.requires import Requires


DESKTOP = "desktop"
LAPTOP = "laptop"
SERVER = "server"
ALL_CATEGORIES = [DESKTOP, LAPTOP, SERVER]

I386 = "i386"
AMD64 = "amd64"
LPIA = "lpia"
SPARC = "sparc"
ALL_ARCHITECTURES = [I386, AMD64, LPIA, SPARC]

FAIL = "fail"
PASS = "pass"
SKIP = "skip"
ALL_STATUS = [PASS, FAIL, SKIP]


class TestResult(object):

    def __init__(self, test, status, data, duration=None):
        self.test = test
        self.status = status
        self.data = data
        self.duration = duration

    @property
    def attributes(self):
        return {
            "status": self.status,
            "data": self.data,
            "duration": self.duration}

    @property
    def devices(self):
        return self.test.requires.get_devices()

    @property
    def packages(self):
        return self.test.requires.get_packages()

    def _get_status(self):
        return self._status

    def _set_status(self, status):
        if status not in ALL_STATUS:
            raise Exception, "Invalid status: %s" % status

        self._status = status

    status = property(_get_status, _set_status)


class TestCommand(Command):

    def __init__(self, test, *args, **kwargs):
        super(TestCommand, self).__init__(test.command, test.timeout,
            *args, **kwargs)
        self.test = test

    @frontend("get_test_result")
    def execute(self, *args, **kwargs):
        return super(TestCommand, self).execute(*args, **kwargs)

    def post_execute(self, result):
        result = super(TestCommand, self).post_execute(result)

        if result.if_exited:
            exit_status = result.exit_status
            if exit_status == 0:
                status = PASS
                data = result.stdout
                if not data:
                    data = result.stderr
            elif exit_status == 127:
                status = SKIP
                data = _("Command failed, skipping.")
            else:
                status = FAIL
                data = result.stderr
        elif result.if_signaled:
            status = SKIP
            term_signal = result.term_signal
            data = _("Received terminate signal %s: %s") % \
                (signal_to_name(term_signal),
                 signal_to_description(term_signal))
        else:
            raise Exception, "Command not terminated: %s" \
                % self.get_command()

        duration = result.duration
        return TestResult(self.test, status, data, duration)


class TestDescription(Command):

    def __init__(self, test):
        super(TestDescription, self).__init__(test.description, test.timeout)
        self.test = test
        self.output = None

    def get_command(self):
        command = super(TestDescription, self).get_command()
        return "cat <<EOF\n%s\nEOF\n" % command

    def pre_execute(self, result=None):
        super(TestDescription, self).pre_execute()
        if re.search(r"\$output", self.get_command()):
            if not self.output and not result:
                result = self.test.command()

            if result:
                self.output = result.data.strip()
                result.data = ""

            add_variable("output", self.output)

    @frontend("get_test_description")
    def execute(self, *args, **kwargs):
        return super(TestDescription, self).execute(*args, **kwargs)

    def post_execute(self, result):
        result = super(TestDescription, self).post_execute(result)
        remove_variable("output")

        if not result.if_exited \
           or result.exit_status != 0:
            raise Exception, "Description failed: %s" \
                % self.get_command()

        return result.stdout


class Test(object):
    """
    Test base class which should be inherited by each test
    implementation. A test instance contains the following required
    fields:

    name:          Unique name for a test.
    plugin:        Plugin name to handle this test.
    description:   Long description of what the test does.
    suite:         Name of the suite containing this test.

    An instance also contains the following optional fields:

    architectures: List of architectures for which this test is relevant:
                   amd64, i386, powerpc and/or sparc
    categories:    List of categories for which this test is relevant:
                   desktop, laptop and/or server
    command:       Command to run for the test.
    depends:       List of names on which this test depends. So, if
                   the other test fails, this test will be skipped.
    requires:      Registry expressions which are requirements for
                   this test: 'input.mouse' in info.capabilities
    timeout:       Timeout for running the command.
    user:          User to run the command.
    optional:      Boolean expression set to True if this test is optional
                   or False if this test is required.
    """

    required_fields = ["name", "plugin", "description", "suite"]
    optional_fields = {
        "architectures": [],
        "categories": [],
        "command": None,
        "depends": [],
        "requires": None,
        "timeout": None,
        "user": None,
        "optional": False}

    def __init__(self, registry, **attributes):
        super(Test, self).__setattr__("attributes", attributes)

        # Typed fields
        for field in ["architectures", "categories", "depends"]:
            if attributes.has_key(field):
                attributes[field] = re.split(r"\s*,\s*", attributes[field])
        for field in ["timeout"]:
            if attributes.has_key(field):
                attributes[field] = int(attributes[field])

        # Optional fields
        for field in self.optional_fields.keys():
            if not attributes.has_key(field):
                attributes[field] = self.optional_fields[field]

        # Requires field
        attributes["requires"] = Requires(registry, attributes["requires"])

        # Command field
        attributes["command"] = TestCommand(self)

        # Description field
        attributes["description"] = TestDescription(self)

        self._validate()

    def _validate(self):
        # Unknown fields
        for field in self.attributes.keys():
            if field not in self.required_fields + self.optional_fields.keys():
                logging.info("Test attributes contains unknown field: %s",
                    field)
                del self.attributes[field]

        # Required fields
        for field in self.required_fields:
            if not self.attributes.has_key(field):
                raise Exception, \
                    "Test attributes does not contain '%s': %s" \
                    % (field, self.attributes)

    def __getattr__(self, name):
        if name not in self.attributes:
            raise AttributeError, name

        return self.attributes[name]

    def __setattr__(self, name, value):
        if name not in self.attributes:
            raise AttributeError, name

        self.attributes[name] = value
        self._validate()
