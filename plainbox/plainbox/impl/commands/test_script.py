# This file is part of Checkbox.
#
# Copyright 2012-2014 Canonical Ltd.
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
plainbox.impl.commands.test_script
==================================

Test definitions for plainbox.impl.script module
"""

import argparse
from inspect import cleandoc
from unittest import TestCase

from plainbox.impl.applogic import PlainBoxConfig
from plainbox.impl.commands.cmd_script import ScriptCommand
from plainbox.impl.commands.inv_script import ScriptInvocation
from plainbox.impl.providers.v1 import DummyProvider1
from plainbox.impl.testing_utils import make_job
from plainbox.testing_utils.io import TestIO
from plainbox.vendor import mock


class TestScriptCommand(TestCase):

    def setUp(self):
        self.parser = argparse.ArgumentParser(prog='test')
        self.subparsers = self.parser.add_subparsers()
        self.provider_loader = lambda: [mock.Mock()]
        self.config_loader = lambda: mock.Mock()
        self.ns = mock.Mock()

    def test_init(self):
        script_cmd = ScriptCommand(self.provider_loader, self.config_loader)
        self.assertIs(script_cmd.provider_loader, self.provider_loader)
        self.assertIs(script_cmd.config_loader, self.config_loader)

    def test_register_parser(self):
        ScriptCommand(
            self.provider_loader, self.config_loader
        ).register_parser(self.subparsers)
        with TestIO() as io:
            self.parser.print_help()
        self.assertIn("script    run a command from a job", io.stdout)
        with TestIO() as io:
            with self.assertRaises(SystemExit):
                self.parser.parse_args(['script', '--help'])
        self.assertEqual(
            io.stdout, cleandoc(
                """
                usage: plainbox dev script [-h] JOB-ID

                positional arguments:
                  JOB-ID      Id of the job to run

                optional arguments:
                  -h, --help  show this help message and exit
                """)
            + "\n")

    @mock.patch("plainbox.impl.commands.inv_script.ScriptInvocation")
    def test_invoked(self, patched_ScriptInvocation):
        retval = ScriptCommand(
            self.provider_loader, self.config_loader
        ).invoked(self.ns)
        patched_ScriptInvocation.assert_called_once_with(
            self.provider_loader, self.config_loader, self.ns.job_id)
        self.assertEqual(
            retval, patched_ScriptInvocation(
                self.provider_loader, self.config_loader,
                self.ns.job_id
            ).run.return_value)


class ScriptInvocationTests(TestCase):
    JOB_ID = '2013.com.canonical.plainbox::foo'
    JOB_PARTIAL_ID = 'foo'

    def setUp(self):
        self.provider_loader = mock.Mock()
        self.config_loader = lambda: PlainBoxConfig()
        self.job_id = mock.Mock()

    def assertCommandOutput(self, actual, expected):
        self.assertEqual(actual, cleandoc(expected) + '\n')

    def test_init(self):
        script_inv = ScriptInvocation(
            self.provider_loader, self.config_loader, self.job_id)
        self.assertIs(script_inv.provider_loader, self.provider_loader)
        self.assertIs(script_inv.config_loader, self.config_loader)
        self.assertIs(script_inv.job_id, self.job_id)

    def test_run_no_such_job(self):
        provider_loader = lambda: [DummyProvider1()]
        script_inv = ScriptInvocation(
            provider_loader, self.config_loader, self.JOB_ID)
        with TestIO() as io:
            retval = script_inv.run()
        self.assertCommandOutput(
            io.stdout, (
                """
                There is no job called '{job_id}'
                See `plainbox special --list-jobs` for a list of choices
                """).format(job_id=self.JOB_ID))
        self.assertEqual(retval, 126)

    def test_run_job_without_command(self):
        provider_loader = lambda: [DummyProvider1([make_job(self.JOB_PARTIAL_ID)])]
        script_inv = ScriptInvocation(
            provider_loader, self.config_loader, self.JOB_ID)
        with TestIO() as io:
            retval = script_inv.run()
        self.assertCommandOutput(
            io.stdout, (
                """
                Selected job does not have a command
                """))
        self.assertEqual(retval, 125)

    @mock.patch('plainbox.impl.ctrl.check_output')
    def test_job_with_command(self, mock_check_output):
        provider_loader = lambda: [DummyProvider1([
            make_job(self.JOB_PARTIAL_ID, command='echo ok')])]
        script_inv = ScriptInvocation(
            provider_loader, self.config_loader, self.JOB_ID)
        with TestIO() as io:
            retval = script_inv.run()
        self.assertCommandOutput(
            io.stdout, (
                """
                (job {job_id}, <stdout:00001>) ok
                job {job_id} returned 0
                command: echo ok
                """).format(job_id=self.JOB_ID))
        self.assertEqual(retval, 0)

    @mock.patch('plainbox.impl.ctrl.check_output')
    def test_job_with_command_making_files(self, mock_check_output):
        provider_loader = lambda: [DummyProvider1([
            make_job(self.JOB_PARTIAL_ID, command='echo ok > file')])]
        script_inv = ScriptInvocation(
            provider_loader, self.config_loader, self.JOB_ID)
        with TestIO() as io:
            retval = script_inv.run()
        self.maxDiff = None
        self.assertCommandOutput(
            io.stdout, (
                """
                Leftover file detected: 'file':
                  file:1: ok
                job {job_id} returned 0
                command: echo ok > file
                """).format(job_id=self.JOB_ID))
        self.assertEqual(retval, 0)

    @mock.patch('plainbox.impl.ctrl.check_output')
    def test_job_with_command_making_directories(self, mock_check_output):
        provider_loader = lambda: [DummyProvider1([
            make_job(self.JOB_PARTIAL_ID, command='mkdir dir')])]
        script_inv = ScriptInvocation(
            provider_loader, self.config_loader, self.JOB_ID)
        with TestIO() as io:
            retval = script_inv.run()
        self.maxDiff = None
        self.assertCommandOutput(
            io.stdout, (
                """
                Leftover directory detected: 'dir'
                job {job_id} returned 0
                command: mkdir dir
                """).format(job_id=self.JOB_ID))
        self.assertEqual(retval, 0)
