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
"""
The purpose of this module is to encapsulate the concept of a test
which might be presented in several ways. For example, a test might
require manual intervention whereas another test might be completely
automatic. Either way, this module provides the base common to each type
of test.
"""

import re
import logging

from checkbox.command import Command
from checkbox.description import Description
from checkbox.iterator import Iterator, IteratorExclude, IteratorPreRepeat, IteratorPostRepeat
from checkbox.requires import Requires
from checkbox.resolver import Resolver
from checkbox.result import FAIL, SKIP


DESKTOP = "desktop"
LAPTOP = "laptop"
SERVER = "server"
ALL_CATEGORIES = [DESKTOP, LAPTOP, SERVER]

I386 = "i386"
AMD64 = "amd64"
SPARC = "sparc"
ALL_ARCHITECTURES = [I386, AMD64, SPARC]


class TestManager(object):
    """
    Test manager which is essentially a container of tests.
    """

    def __init__(self, tests=[], plugin_priorities=[]):
        self._tests = tests
        self._plugin_priorities = plugin_priorities

        self._architecture = None
        self._category = None

        self._dependent_next = []
        self._dependent_prev = []

    def add_test(self, test):
        """
        Add a test to the manager.
        """
        self._tests.append(test)

    def set_architecture(self, architecture):
        self._architecture = architecture

    def set_category(self, category):
        self._category = category

    def _compare_func(self, a, b):
        if a.plugin in self._plugin_priorities:
            if b.plugin in self._plugin_priorities:
                ia = self._plugin_priorities.index(a.plugin)
                ib = self._plugin_priorities.index(b.plugin)
                if ia != ib:
                    return cmp(ia, ib)
            else:
                return -1
        elif b.plugin in self._plugin_priorities:
            return 1

        return cmp((a.suite, a.name), (b.suite, b.name))

    def _dependent_prerepeat_next_func(self, test, result, resolver):
        """IteratorPreRepeat function which completely skips dependents
           of tests which either have a status of FAIL or SKIP."""
        if result and result.test == test:
            if result.status == FAIL or result.status == SKIP:
                self._dependent_next = resolver.get_dependents(test)
            else:
                self._dependent_next = []

        self._dependent_prev.append(test)

    def _dependent_prerepeat_prev_func(self, test, result, resolver):
        """IteratorPreRepeat function which supplements the above by
           keeping track of a stack of previously run tests."""
        self._dependent_prev.pop()

    def _dependent_exclude_next_func(self, test, result):
        if test in self._dependent_next:
            logging.info("Test '%s' dependent on failed or skipped test",
                test.name)
            return True

        return False

    def _dependent_exclude_prev_func(self, test, result):
        if self._dependent_prev[-1] != test:
            logging.info("Test '%s' dependent on failed or skipped test",
                test.name)
            return True

        return False

    def _requires_exclude_func(self, test, result):
        """IteratorExclude function which removes test when the
           requires field contains a False value."""
        if False in test.requires.get_mask():
            logging.info("Test '%s' does not pass requires field: %s",
                test.name, test.requires)
            return True

        return False

    def _architecture_exclude_func(self, test, result):
        """IteratorExclude function which removes test when the
           architectures field exists and doesn't meet the given
           requirements."""
        if test.architectures:
            if not self._architecture:
                logging.info("No system architecture, "
                    "skipping test: %s", test.name)
                return True
            elif self._architecture not in test.architectures:
                logging.info("System architecture not supported, "
                    "skipping test: %s", test.name)
                return True

        return False

    def _category_exclude_func(self, test, result):
        """IteratorExclude function which removes test when
           the categories field exists and doesn't meet the given
           requirements."""
        if test.categories:
            if not self._category:
                logging.info("No system category, "
                    "skipping test: %s", test.name)
                return True
            elif self._category not in test.categories:
                logging.info("System category not supported, "
                    "skipping test: %s", test.name)
                return True

        return False

    def get_iterator(self):
        """
        Get an iterator over the tests added to the manager. The
        purpose of this iterator is that it orders tests based on
        dependencies and enforces constraints defined in fields.
        """
        resolver = Resolver(self._compare_func)

        # Express dependents as objects rather than string names
        test_dict = dict(((t.suite, t.name), t) for t in self._tests)
        for test in self._tests:
            test_depends = [test_dict[(test.suite, d)] for d in test.depends]
            resolver.add(test, *test_depends)

        tests = resolver.get_dependents()
        iterator = Iterator(tests)
        iterator = IteratorExclude(iterator,
            self._requires_exclude_func,
            self._requires_exclude_func)
        iterator = IteratorExclude(iterator,
            self._architecture_exclude_func,
            self._architecture_exclude_func)
        iterator = IteratorExclude(iterator,
            self._category_exclude_func,
            self._category_exclude_func)
        iterator = IteratorExclude(iterator,
            self._dependent_exclude_next_func,
            self._dependent_exclude_prev_func)
        iterator = IteratorPreRepeat(iterator,
            lambda test, result, resolver=resolver: \
                   self._dependent_prerepeat_next_func(test, result, resolver))
        iterator = IteratorPostRepeat(iterator,
            prev_func=lambda test, result, resolver=resolver: \
                   self._dependent_prerepeat_prev_func(test, result, resolver))

        return iterator


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
        attributes["requires"] = Requires(attributes["requires"], registry)

        # Command field
        attributes["command"] = Command(attributes["command"],
            attributes["timeout"])

        # Description field
        attributes["description"] = Description(attributes["description"],
            attributes["timeout"])

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
