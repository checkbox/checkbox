# This file is part of Checkbox.
#
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
:mod:`checkbox_ng.commands.sru` -- sru sub-command
==================================================

.. warning::

    THIS MODULE DOES NOT HAVE STABLE PUBLIC API
"""
import logging
import sys
import tempfile

from gettext import gettext as _
from plainbox.impl.applogic import get_matching_job_list
from plainbox.impl.applogic import get_whitelist_by_name
from plainbox.impl.applogic import run_job_if_possible
from plainbox.impl.commands import PlainBoxCommand
from plainbox.impl.commands.inv_check_config import CheckConfigInvocation
from plainbox.impl.commands.cmd_checkbox import CheckBoxCommandMixIn
from plainbox.impl.commands.inv_checkbox import CheckBoxInvocationMixIn
from plainbox.impl.depmgr import DependencyDuplicateError
from plainbox.impl.exporter import ByteStringStreamTranslator
from plainbox.impl.exporter.xml import XMLSessionStateExporter
from plainbox.impl.runner import JobRunner
from plainbox.impl.secure.config import ValidationError, Unset
from plainbox.impl.session import SessionStateLegacyAPI as SessionState
from plainbox.impl.transport import TransportError

from checkbox_ng.certification import CertificationTransport


logger = logging.getLogger("plainbox.commands.sru")


class _SRUInvocation(CheckBoxInvocationMixIn):
    """
    Helper class instantiated to perform a particular invocation of the sru
    command. Unlike the SRU command itself, this class is instantiated each
    time.
    """

    def __init__(self, provider_loader, config_loader, ns):
        super().__init__(provider_loader, config_loader)
        self.ns = ns
        if self.ns.whitelist:
            self.whitelist = self.get_whitelist_from_file(
                self.ns.whitelist[0].name, self.ns.whitelist)
        elif self.config.whitelist is not Unset:
            self.whitelist = self.get_whitelist_from_file(
                self.config.whitelist)
        else:
            self.whitelist = get_whitelist_by_name(self.provider_list, 'sru')
        self.job_list = self.get_job_list(ns)
        # XXX: maybe allow specifying system_id from command line?
        self.exporter = XMLSessionStateExporter(system_id=None)
        self.session = None
        self.runner = None

    def run(self):
        # Compute the run list, this can give us notification about problems in
        # the selected jobs. Currently we just display each problem
        # Create a session that handles most of the stuff needed to run jobs
        try:
            self.session = SessionState(self.job_list)
        except DependencyDuplicateError as exc:
            # Handle possible DependencyDuplicateError that can happen if
            # someone is using plainbox for job development.
            print(_("The job database you are currently using is broken"))
            print(_("At least two jobs contend for the name {0}").format(
                exc.job.id))
            print(_("Second job defined in: {0}").format(
                exc.duplicate_job.origin))
            raise SystemExit(exc)
        with self.session.open():
            self._set_job_selection()
            self.runner = JobRunner(
                self.session.session_dir, self.provider_list,
                self.session.jobs_io_log_dir, command_io_delegate=self,
                dry_run=self.ns.dry_run)
            self._run_all_jobs()
            if self.config.fallback_file is not Unset:
                self._save_results()
            self._submit_results()
        # FIXME: sensible return value
        return 0

    def _set_job_selection(self):
        desired_job_list = get_matching_job_list(self.job_list, self.whitelist)
        problem_list = self.session.update_desired_job_list(desired_job_list)
        if problem_list:
            logger.warning(
                _("There were some problems with the selected jobs"))
            for problem in problem_list:
                logger.warning("- %s", problem)
            logger.warning(_("Problematic jobs will not be considered"))

    def _save_results(self):
        print(_("Saving results to {0}").format(self.config.fallback_file))
        with open(self.config.fallback_file, "wt", encoding="UTF-8") as stream:
            translating_stream = ByteStringStreamTranslator(stream, "UTF-8")
            self.exporter.dump_from_session_manager(self.session.manager,
                                                    translating_stream)

    def _submit_results(self):
        print(_("Submitting results to {0} for secure_id {1}").format(
              self.config.c3_url, self.config.secure_id))
        options_string = "secure_id={0}".format(self.config.secure_id)
        # Create the transport object
        transport = CertificationTransport(self.config.c3_url, options_string)
        # Prepare the data for submission
        with tempfile.NamedTemporaryFile(mode='w+b') as stream:
            # Dump the data to the temporary file
            self.exporter.dump_from_session_manager(self.session.manager,
                                                    stream)
            # Flush and rewind
            stream.flush()
            stream.seek(0)
            try:
                # Send the data, reading from the temporary file
                result = transport.send(stream, self.config, self.session)
                if 'url' in result:
                    print(_("Successfully sent, submission status at"
                            " {0}").format(result['url']))
                else:
                    print(_("Successfully sent, server response: {0}").format(
                        result))
            except (ValueError, TransportError) as exc:
                print(str(exc))
            except IOError as exc:
                print(_("Problem reading a file: {0}").format(exc))

    def _run_all_jobs(self):
        again = True
        while again:
            again = False
            for job in self.session.run_list:
                # Skip jobs that already have result, this is only needed when
                # we run over the list of jobs again, after discovering new
                # jobs via the local job output
                result = self.session.job_state_map[job.id].result
                if result.outcome is not None:
                    continue
                self._run_single_job(job)
                self.session.persistent_save()
                if job.plugin == "local":
                    # After each local job runs rebuild the list of matching
                    # jobs and run everything again
                    self._set_job_selection()
                    again = True
                    break

    def _run_single_job(self, job):
        print("- {}:".format(job.id), end=' ')
        sys.stdout.flush()
        job_state, job_result = run_job_if_possible(
            self.session, self.runner, self.config, job)
        print("{0}".format(job_result.outcome))
        sys.stdout.flush()
        if job_result.comments is not None:
            print(_("comments: {0}").format(job_result.comments))
        if job_state.readiness_inhibitor_list:
            print(_("inhibitors:"))
        for inhibitor in job_state.readiness_inhibitor_list:
            print("  * {}".format(inhibitor))
        self.session.update_job_result(job, job_result)


class SRUCommand(PlainBoxCommand, CheckBoxCommandMixIn):
    """
    Command for running Stable Release Update (SRU) tests.

    Stable release updates are periodic fixes for nominated bugs that land in
    existing supported Ubuntu releases. To ensure a certain level of quality
    all SRU updates affecting hardware enablement are automatically tested
    on a pool of certified machines.

    This command is _temporary_ and will eventually migrate to the checkbox
    side. Its intended lifecycle is for the development and validation of
    plainbox core on realistic workloads.
    """

    gettext_domain = "checkbox-ng"

    def __init__(self, provider_loader, config_loader):
        self.provider_loader = provider_loader
        # This command does funky things to the command line parser and it
        # needs to load the config subsystem *early* so let's just load it now.
        self.config = config_loader()

    def invoked(self, ns):
        # Copy command-line arguments over configuration variables
        try:
            if ns.secure_id:
                self.config.secure_id = ns.secure_id
            if ns.fallback_file and ns.fallback_file is not Unset:
                self.config.fallback_file = ns.fallback_file
            if ns.c3_url:
                self.config.c3_url = ns.c3_url
        except ValidationError as exc:
            print(_("Configuration problems prevent running SRU tests"))
            print(exc)
            return 1
        # Run check-config, if requested
        if ns.check_config:
            retval = CheckConfigInvocation(lambda: self.config).run()
            if retval != 0:
                return retval
        # To maintain the illusion (aka API) the config loader we're presenting
        # to the invocation class is just a simple lambda that returns the
        # already loaded config.
        return _SRUInvocation(
            self.provider_loader, lambda: self.config, ns).run()

    def register_parser(self, subparsers):
        parser = subparsers.add_parser(
            "sru", help=_("run automated stable release update tests"))
        parser.set_defaults(command=self)
        parser.add_argument(
            "--check-config",
            action="store_true",
            help=_("run check-config before starting"))
        group = parser.add_argument_group("sru-specific options")
        # Set defaults from based on values from the config file
        group.set_defaults(
            secure_id=self.config.secure_id,
            c3_url=self.config.c3_url,
            fallback_file=self.config.fallback_file)
        group.add_argument(
            '--secure-id', metavar=_("SECURE-ID"),
            action='store',
            # NOTE: --secure-id is optional only when set in a config file
            required=self.config.secure_id is Unset,
            # TRANSLATORS: Do not translate %(default)
            help=(_("associate submission with a machine using this SECURE-ID"
                  " (%(default)s)")))
        group.add_argument(
            '--fallback', metavar=_("FILE"),
            dest='fallback_file',
            action='store',
            default=Unset,
            # TRANSLATORS: Do not translate %(default)s
            help=(_("if submission fails save the test report as FILE"
                  " (%(default)s)")))
        group.add_argument(
            '--destination', metavar=_("URL"),
            dest='c3_url',
            action='store',
            # TRANSLATORS: Do not translate %(default)s
            help=(_("POST the test report XML to this URL"
                  " (%(default)s)")))
        group.add_argument(
            '--staging',
            dest='c3_url',
            action='store_const',
            const='https://certification.staging.canonical.com/'
                  'submissions/submit/',
            help=_('override --destination to use the staging '
                   'certification website'))
        group = parser.add_argument_group(title="execution options")
        group.add_argument(
            '-n', '--dry-run',
            action='store_true',
            default=False,
            help=_("don't really run most jobs"))
        # Call enhance_parser from CheckBoxCommandMixIn
        self.enhance_parser(parser)
