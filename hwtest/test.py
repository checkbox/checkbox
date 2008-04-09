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
"""
The purpose of this module is to encapsulate the concept of a test
which might be presented in several ways. For example, a test might
require manual intervention whereas another test might be completely
automatic. Either way, this module provides the base common to each type
of test.
"""

import re
import logging

from hwtest.command import Command
from hwtest.description import Description
from hwtest.excluder import Excluder
from hwtest.iterator import Iterator, NEXT, PREV
from hwtest.repeater import PreRepeater
from hwtest.requires import Requires
from hwtest.resolver import Resolver
from hwtest.result import Result, FAIL, SKIP


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

    def __init__(self):
        self._tests = []
        self._architecture = None
        self._category = None

    def add_test(self, test):
        """
        Add a test to the manager.
        """
        self._tests.append(test)

    def set_architecture(self, architecture):
        self._architecture = architecture

    def set_category(self, category):
        self._category = category

    def get_count(self):
        return len(self._tests)

    def get_iterator(self, direction=NEXT):
        """
        Get an iterator over the tests added to the manager. The
        purpose of this iterator is that it orders tests based on
        dependencies and enforces constraints defined in fields.
        """
        def dependent_prerepeat_func(test, resolver):
            """Pre repeater function which assigns the SKIP status to
               dependents when a test has a status of FAIL or SKIP."""
            result = test.result
            if result and (result.status == FAIL or result.status == SKIP):
                for dependent in resolver.get_dependents(test):
                    dependent.result.status = SKIP

        def requires_exclude_func(test):
            """Excluder function which removes test when the requires
               field contains a False value."""
            if False in test.requires.get_mask():
                logging.debug("Test '%s' does not pass requires field: %s"
                    % (test.name, test.requires))
                return True

            return False

        def architecture_exclude_func(test, architecture):
            """Excluder function which removes test when the architectures
               field exists and doesn't meet the given requirements."""
            if architecture and architecture not in test.architectures:
                logging.debug("Architecture not available for test: %s"
                    % test.name)
                return True

            return False

        def category_exclude_func(test, category):
            """Excluder function which removes test when the categories
               field exists and doesn't meet the given requirements."""
            if category and category not in test.categories:
                logging.debug("Category not available for test: %s"
                    % test.name)
                return True

            return False

        resolver = Resolver()
        test_dict = dict((q.name, q) for q in self._tests)
        for test in self._tests:
            test_depends = [test_dict[d] for d in test.depends]
            resolver.add(test, *test_depends)

        tests = resolver.get_dependents()
        tests_iter = Iterator(tests)
        tests_iter = PreRepeater(tests_iter,
            lambda test, resolver=resolver: \
                   dependent_prerepeat_func(test, resolver))
        tests_iter = Excluder(tests_iter,
            requires_exclude_func, requires_exclude_func)
        tests_iter = Excluder(tests_iter,
            lambda test, architecture=self._architecture: \
                   architecture_exclude_func(test, architecture),
            lambda test, architecture=self._architecture: \
                   architecture_exclude_func(test, architecture))
        tests_iter = Excluder(tests_iter,
            lambda test, category=self._category: \
                   category_exclude_func(test, category),
            lambda test, category=self._category: \
                   category_exclude_func(test, category))

        if direction == PREV:
            while True:
                try:
                    tests_iter.next()
                except StopIteration:
                    break

        return tests_iter


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
    requires:      List of registry expressions on which are requirements
                   for this test: 'input.mouse' in info.capabilities
    timeout:       Timeout for running the command.
    optional:      Boolean expression set to True if this test is optional
                   or False if this test is required.
    """

    required_fields = ["name", "plugin", "description", "suite"]
    optional_fields = {
        "architectures": ALL_ARCHITECTURES,
        "categories": ALL_CATEGORIES,
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
        attributes["description"].add_variable("test", self)

        # Result attribute
        result = Result()
        result.packages = attributes["requires"].get_packages()
        result.devices = attributes["requires"].get_devices()
        super(Test, self).__setattr__("result", result)

        self._validate()

    def _validate(self):
        # Unknown fields
        for field in self.attributes.keys():
            if field not in self.required_fields + self.optional_fields.keys():
                logging.info("Test attributes contains unknown field: %s" \
                    % field)
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
