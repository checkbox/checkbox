# This file is part of Checkbox.
#
# Copyright 2012 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
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

"""
plainbox.impl.test_result
=========================

Test definitions for plainbox.impl.result module
"""

from unittest import TestCase

from plainbox.impl.result import JobResult
from plainbox.impl.testing_utils import make_job


class JobResultTests(TestCase):

    def setUp(self):
        self.job = make_job("A")

    def test_smoke(self):
        result = JobResult({'job': self.job})
        self.assertEqual(str(result), "A: None")
        self.assertEqual(repr(result), (
            "<JobResult job:<JobDefinition name:'A' plugin:'dummy'>"
            " outcome:None>"))
        self.assertIs(result.job, self.job)
        self.assertIsNone(result.outcome)
        self.assertIsNone(result.comments)
        self.assertEqual(result.io_log, ())
        self.assertIsNone(result.return_code)

    def test_everything(self):
        result = JobResult({
            'job': self.job,
            'outcome': JobResult.OUTCOME_PASS,
            'comments': "it said blah",
            'io_log': ((0, 'stdout', 'blah\n'),),
            'return_code': 0
        })
        self.assertEqual(str(result), "A: pass")
        self.assertEqual(repr(result), (
            "<JobResult job:<JobDefinition name:'A' plugin:'dummy'>"
            " outcome:'pass'>"))
        self.assertIs(result.job, self.job)
        self.assertEqual(result.outcome, JobResult.OUTCOME_PASS)
        self.assertEqual(result.comments, "it said blah")
        self.assertEqual(result.io_log, ((0, 'stdout', 'blah\n'),))
        self.assertEqual(result.return_code, 0)
