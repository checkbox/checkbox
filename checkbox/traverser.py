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
The traverser exposes a simple iterator interface for accessing the graph
of tests as expressed by the dependency tree. The constructor provides an
additional callbacks instance for processing tests which might be skipped.
"""

import logging

from checkbox.lib.iterator import (Iterator, IteratorContain,
    IteratorExclude, IteratorPostRepeat, IteratorPreRepeat)

from checkbox.resolver import Resolver
from checkbox.test import FAIL, SKIP


class TraverserCallbacks(object):

    def get_architecture(self):
        return None

    def get_category(self):
        return None

    def get_priorities(self):
        return []

    def skipped_dependent(self, test, result):
        logging.info("Test '%s' dependent on skipped test",
            test.name)

    def failed_dependent(self, test, result):
        logging.info("Test '%s' dependent on failed test",
            test.name)

    def unsupported_requires(self, test, result):
        logging.info("Test '%s' does not support requires field: %s",
            test.name, test.requires)

    def undefined_architecture(self, test, result):
        logging.info("No system architecture defined, skipping test: %s",
            test.name)

    def unsupported_architecture(self, test, result):
        logging.info("System architecture not supported, skipping test: %s",
            test.name)

    def undefined_category(self, test, result):
        logging.info("No system category defined, skipping test: %s",
            test.name)

    def unsupported_category(self, test, result):
        logging.info("System category not supported, skipping test: %s",
            test.name)


class Traverser(IteratorContain):

    def __init__(self, tests=[], callbacks=TraverserCallbacks, *args, **kwargs):
        self._callbacks = callbacks(*args, **kwargs)

        self._dependent_next = []
        self._dependent_prev = []
        self._dependent_status = None

        # Express dependents as objects rather than string names
        resolver = Resolver(self._compare_func)
        test_dict = dict(((t.suite, t.name), t) for t in tests)
        for test in tests:
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

        super(Traverser, self).__init__(iterator)

    def _compare_func(self, a, b):
        priorities = self._callbacks.get_priorities()
        if a.plugin in priorities:
            if b.plugin in priorities:
                ia = priorities.index(a.plugin)
                ib = priorities.index(b.plugin)
                if ia != ib:
                    return cmp(ia, ib)
            else:
                return -1
        elif b.plugin in priorities:
            return 1

        return cmp((a.suite, a.name), (b.suite, b.name))

    def _dependent_prerepeat_next_func(self, test, result, resolver):
        """IteratorPreRepeat function which completely skips dependents
           of tests which either have a status of FAIL or SKIP."""
        if result and result.test == test:
            if result.status == FAIL or result.status == SKIP:
                self._dependent_next = resolver.get_dependents(test)
                self._dependent_status = result.status
            else:
                self._dependent_next = []

        self._dependent_prev.append(test)

    def _dependent_prerepeat_prev_func(self, test, result, resolver):
        """IteratorPreRepeat function which supplements the above by
           keeping track of a stack of previously run tests."""
        self._dependent_prev.pop()

    def _dependent_exclude_next_func(self, test, result):
        if test in self._dependent_next:
            if self._dependent_status == FAIL:
                self._callbacks.failed_dependent(test, result)
            elif self._dependent_status == SKIP:
                self._callbacks.skipped_dependent(test, result)
            return True

        return False

    def _dependent_exclude_prev_func(self, test, result):
        if self._dependent_prev[-1] != test:
            return True

        return False

    def _requires_exclude_func(self, test, result):
        """IteratorExclude function which removes test when the
           requires field contains a False value."""
        if False in test.requires.get_mask():
            self._callbacks.unsupported_requires(test, result)
            return True

        return False

    def _architecture_exclude_func(self, test, result):
        """IteratorExclude function which removes test when the
           architectures field exists and doesn't meet the given
           requirements."""
        if test.architectures:
            architecture = self._callbacks.get_architecture()
            if architecture is None:
                self._callbacks.undefined_architecture(test, result)
                return True
            elif architecture not in test.architectures:
                self._callbacks.unsupported_architecture(test, result)
                return True

        return False

    def _category_exclude_func(self, test, result):
        """IteratorExclude function which removes test when
           the categories field exists and doesn't meet the given
           requirements."""
        if test.categories:
            category = self._callbacks.get_category()
            if category is None:
                self._callbacks.undefined_category(test, result)
                return True
            elif category not in test.categories:
                self._callbacks.unsupported_category(test, result)
                return True

        return False
