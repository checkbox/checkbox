# This file is part of Checkbox.
#
# Copyright 2013 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.

#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.

"""
plainbox.impl.commands.test_sru
===============================

Test definitions for plainbox.impl.box module
"""

from inspect import cleandoc
from unittest import TestCase

from plainbox.testing_utils.io import TestIO

from checkbox_ng.main import main


class TestSru(TestCase):

    def test_help(self):
        with TestIO(combined=True) as io:
            with self.assertRaises(SystemExit) as call:
                main(['sru', '--help'])
            self.assertEqual(call.exception.args, (0,))
        self.maxDiff = None
        expected = """
        usage: checkbox sru [-h] [--check-config] --secure-id SECURE-ID
                            [--fallback FILE] [--destination URL] [--staging] [-n]
                            [-T TEST-PLAN-ID] [-i PATTERN] [-x PATTERN] [-w WHITELIST]

        optional arguments:
          -h, --help            show this help message and exit
          --check-config        run check-config before starting

        sru-specific options:
          --secure-id SECURE-ID
                                associate submission with a machine using this SECURE-
                                ID (unset)
          --fallback FILE       if submission fails save the test report as FILE
                                (unset)
          --destination URL     POST the test report XML to this URL (https://certific
                                ation.canonical.com/submissions/submit/)
          --staging             override --destination to use the staging
                                certification website

        execution options:
          -n, --dry-run         don't really run most jobs

        test selection options:
          -T TEST-PLAN-ID, --test-plan TEST-PLAN-ID
                                load the specified test plan
          -i PATTERN, --include-pattern PATTERN
                                include jobs matching the given regular expression
          -x PATTERN, --exclude-pattern PATTERN
                                exclude jobs matching the given regular expression
          -w WHITELIST, --whitelist WHITELIST
                                load whitelist containing run patterns
        """
        self.assertEqual(io.combined, cleandoc(expected) + "\n")
