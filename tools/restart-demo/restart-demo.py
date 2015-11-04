#!/usr/bin/env python3
# This file is part of Checkbox.
#
# Copyright 2015 Canonical Ltd.
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
Demonstration of the automatic application restart APIs.

This file implements a tiny application based on the plainbox SessionAssistant
APIs that supports unattended application restarts. The application runs a
simple reboot test. The test reboots the system. Upon completing the reboot,
the testing application is re-started and resumed automatically.

All that is required to add similar feature to other application is the use of
the SessionAssistant.configure_application_restart() and optionally
SessionAssistant.use_alternate_resume_strategy() which allows for complete
control over the process. Here the second method is not used, defaulting to
environment-based auto-detection.
"""
import argparse
import os
import sys

from guacamole import Command

from plainbox.impl.session.assistant import SA_RESTARTABLE
from plainbox.impl.session.assistant import SessionAssistant


class RestartDemo(Command):

    """
    Demonstration application for showcasing application restart support.

    @EPILOG@

    NOTE: This application will restart the system. If everything else works
    correctly the application will be re-started after the operating system is
    running again.
    """

    def register_arguments(self, parser):
        parser.add_argument(
            '--resume', dest='session_id', metavar="SESSION_ID",
            help=argparse.SUPPRESS)

    def invoked(self, ctx):
        sa = SessionAssistant(
            "restart-demo", "0.1",
            # Indicate that we want to use the restart API
            "0.99", (SA_RESTARTABLE,)
        )
        try:
            sa.select_providers("plainbox-provider-restart-demo")
        except ValueError:
            raise SystemExit(
                "Please 'develop' the restart-demo provider to use this demo")
        sa.configure_application_restart(
            # XXX: This assumes mk-venv and has needless stuff in a realistic
            # application. If your application has a simple executable to call
            # just pass that executable name below and don't copy the
            # PROVIDERPATH trick or the absolute path to executable trick. They
            # are only needed by this hacky example.
            lambda session_id: [
                'sh', '-c', ' '.join([
                    'PROVIDERPATH={}'.format(os.getenv("PROVIDERPATH")),
                    os.path.expandvars("$VIRTUAL_ENV/bin/python3"),
                    os.path.normpath(os.path.expandvars(
                        "$VIRTUAL_ENV/../tools/restart-demo/restart-demo.py")),
                    "--resume", session_id])
            ])
        # Resume the session if we're asked to do this
        if ctx.args.session_id:
            for (session_id, metadata) in sa.get_resumable_sessions():
                if session_id == ctx.args.session_id:
                    sa.resume_session(session_id)
                    break
            else:
                raise RuntimeError("Requested session is not resumable!")
        else:
            sa.start_new_session("Automatic application restart demo")
        sa.select_test_plan("2015.pl.zygoon.restart-demo::reboot-once")
        sa.bootstrap()
        for job_id in sa.get_dynamic_todo_list():
            print("Running job: ", job_id)
            result_builder = sa.run_job(job_id, "silent", False)
            sa.use_job_result(job_id, result_builder.get_result())
        print("All tests finished, results are printed below")
        sa.export_to_stream("text", [], sys.stdout.buffer)
        sa.finalize_session()
        input("Press enter to continue")


if __name__ == '__main__':
    RestartDemo().main()
