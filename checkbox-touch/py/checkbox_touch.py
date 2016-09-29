# This file is part of Checkbox.
#
# Copyright 2014-2016 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
#   Maciej Kisielewski <maciej.kisielewski@canonical.com>
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
:mod:`checkbox_stack` -- Python Interface to Checkbox QML Stack
===============================================================

This module is a part of the implementation of the Checkbox QML Stack. It is
being imported at startup of all QML applications that are using Checkbox.
"""
import sys

# Sanitize sys.path so that it doesn't cause issues while loading on a
# sandboxed Ubuntu environment.
sys.path = [item for item in sys.path if not item.startswith('/usr/local')]

import abc
import collections
import datetime
import fnmatch
import json
import logging
import os
try:
    import pyotherside
except ImportError:
    class FakePyOtherSide():
        """
        Bogus pyotherside that does nothing.

        CheckboxConvergedUI uses pyotherside to propagate the output of running
        job's command to the QML side.

        pyotherside module is only available when python is run by PyOtherSide;
        If this module is imported elsewhere (e.g. tests, packaging, etc.),
        this bogus class is used instead.
        """
        def send(self, event, *args):
            pass
    pyotherside = FakePyOtherSide()
import sqlite3
import re
import time
import traceback

from plainbox.abc import IJobResult
from plainbox.impl import pod
from plainbox.impl.clitools import ToolBase
from plainbox.impl.commands.inv_run import SilentUI
from plainbox.impl.launcher import DefaultLauncherDefinition
from plainbox.impl.launcher import LauncherDefinition
from plainbox.impl.launcher import LauncherDefinitionLegacy
from plainbox.impl.result import JobResultBuilder
from plainbox.impl.session.assistant import SessionAssistant
from plainbox.impl.transport import get_all_transports
import plainbox

from embedded_providers import EmbeddedProvider1PlugInCollection

_logger = logging.getLogger('converged')


class CheckboxConvergedUI(SilentUI):
    """
    Class that connects checkbox-converged with plainbox.

    This class inherits SilentUI as most of the events happening in plainbox
    back-end are handled elsewhere.
    """

    def got_program_output(self, stream_name, line):
        pyotherside.send("command_output", line)


class PlainboxApplication(metaclass=abc.ABCMeta):
    """
    Base class for plainbox-based applications.

    Concrete subclasses of this class should implement get_version_pair() and
    add any additional methods that they would like to call.
    """

    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)

    @abc.abstractmethod
    def get_version_pair(self):
        """
        Get core (plainbox) and application version
        """


def view(func):
    """
    Decorator for QML view functions
    """
    def wrapper(*args, **kwargs):
        _logger.debug(
            "%s(%s)", func.__name__, ', '.join(
                [repr(arg) for arg in args]
                + ['{}={!r}'.format(ka, kv) for ka, kv in kwargs.items()]))
        try:
            result = func(*args, **kwargs)
        except Exception as exc:
            _logger.error("%s(...) raised %r", func.__name__, exc)
            traceback.print_exc()
            return {
                'code': 500,
                'error': str(exc),
                'traceback': traceback.format_exc()
            }
        else:
            _logger.debug("%s(...) -> %r", func.__name__, result)
            return {
                'code': 200,
                'result': result
            }
    return wrapper


def not_contains(a, b):
    """
    The 'b not in a' operator, notably missing from the operator module
    """
    return b not in a


class CheckboxConvergedApplication(PlainboxApplication):
    """
    Class implementing the whole checkbox-converged application logic.

    This class exposes methods that can be called by the javascript embedded
    into many of the QML views. Each method implements a request / response
    semantics where the request is the set of data passed to python from
    javascript and the response is the python dictionary returned and processed
    back on the javascript side.

    This model follows the similar web development mechanics where the browser
    can issue asynchronous requests in reaction to user interactions and uses
    response data to alter the user interface.
    """

    __version__ = (1, 5, 0, 'dev', 0)

    def __init__(self, launcher_definition=None):
        if plainbox.__version__ < (0, 22):
            raise SystemExit("plainbox 0.22 required, you have {}".format(
                ToolBase.format_version_tuple(plainbox.__version__)))
        self.assistant = SessionAssistant('checkbox-converged')
        self.ui = CheckboxConvergedUI()
        self.index = 0
        self._password = None
        self._timestamp = None
        self._latest_session = None
        self._available_test_plans = []
        self.test_plan_id = None
        self.resume_candidate_storage = None
        self.launcher = None
        self.assistant.use_alternate_repository(
            self._get_app_cache_directory())

        # Prepare custom execution controller list
        from plainbox.impl.ctrl import UserJobExecutionController
        from sudo_with_pass_ctrl import RootViaSudoWithPassExecutionController
        ctrl_setup_list = [(RootViaSudoWithPassExecutionController,
                           [self._password_provider], {}),
                           (UserJobExecutionController, [], {}),
                           ]
        self.assistant.use_alternate_execution_controllers(ctrl_setup_list)

        if launcher_definition:
            generic_launcher = LauncherDefinition()
            generic_launcher.read([launcher_definition])
            config_filename = os.path.expandvars(
                generic_launcher.config_filename)
            if not os.path.split(config_filename)[0]:
                configs = [
                    '/etc/xdg/{}'.format(config_filename),
                    os.path.expanduser('~/.config/{}'.format(config_filename))]
            else:
                configs = [config_filename]
            self.launcher = generic_launcher.get_concrete_launcher()
            configs.append(launcher_definition)
            self.launcher.read(configs)
            # Checkbox-Converged supports new launcher syntax, so if we have
            # LauncherDefinitionLegacy as launcher right now, let's replace it
            # with a default one
            if type(self.launcher) == LauncherDefinitionLegacy:
                self.launcher = DefaultLauncherDefinition()
            self.assistant.use_alternate_configuration(self.launcher)
            self._prepare_transports()
        else:
            self.launcher = DefaultLauncherDefinition()

    def __repr__(self):
        return "app"

    @view
    def get_launcher_settings(self):
        # this pseudo-adapter exists so qml can now know some bits about the
        # launcher, if you need another setting in the QML fron-end, just add
        # it to the returned dict below
        return {
            'ui_type': self.launcher.ui_type,
        }

    @view
    def load_providers(self, providers_dir):
        if self.launcher:
            self.assistant.select_providers(
                *self.launcher.providers,
                additional_providers=self._get_embedded_providers(
                    providers_dir))
        else:
            self.assistant.select_providers(
                '*',
                additional_providers=self._get_embedded_providers(
                    providers_dir))

    @view
    def get_version_pair(self):
        return {
            'plainbox_version': ToolBase.format_version_tuple(
                plainbox.__version__),
            'application_version': ToolBase.format_version_tuple(
                self.__version__)
        }

    @view
    def start_session(self):
        """Start a new session."""
        self.assistant.start_new_session('Checkbox Converged session')
        self._timestamp = datetime.datetime.utcnow().isoformat()
        return {
            'session_id': self.assistant.get_session_id(),
            'session_dir': self.assistant.get_session_dir()
        }

    @view
    def resume_session(self, rerun_last_test, outcome='skip'):
        """
        Resume latest sesssion.

        :param rerun_last_test:
            A bool stating whether runtime should repeat the test, that the app
            was executing when it was interrupted.
        :param outcome:
            Outcome to set to the last job run. Option useless when rerunning.
        """
        assert outcome in ['pass', 'skip', 'fail', None]
        metadata = self.assistant.resume_session(self._latest_session)
        app_blob = json.loads(metadata.app_blob.decode("UTF-8"))
        self.index = app_blob['index_in_run_list']
        self.test_plan_id = app_blob['test_plan_id']
        self.assistant.select_test_plan(self.test_plan_id)
        self.assistant.bootstrap()

        if not rerun_last_test:
            # Skip current test
            test = self.get_next_test()['result']
            test['outcome'] = outcome
            self.register_test_result(test)
        return {
            'session_id': self._latest_session,
            'session_dir': self.assistant.get_session_dir()
        }

    @view
    def clear_session(self):
        """Reset app-custom state info about the session."""
        self.index = 0
        self._timestamp = datetime.datetime.utcnow().isoformat()
        self._finalize_session()

    @view
    def is_session_resumable(self):
        """Check whether there is a session that can be resumed."""
        for session_id, session_md in self.assistant.get_resumable_sessions():
            if session_md.app_blob is None:
                continue
            # we're interested in the latest session only, this is why we
            # return early
            self._latest_session = session_id
            return {
                'resumable': True,
                'running_job_name': session_md.running_job_name,
                'error_encountered': False,
            }
        else:
            return {
                'resumable': False,
                'error_encountered': False,
            }

    @view
    def get_testplans(self):
        """Get the list of available test plans."""
        if not self._available_test_plans:
            if self.launcher:
                if self.launcher.test_plan_forced:
                    self._available_test_plans = [
                        self.assistant.get_test_plan(
                            self.launcher.test_plan_default_selection)]
                else:
                    test_plan_ids = self.assistant.get_test_plans()
                    filtered_tp_ids = set()
                    for filter in self.launcher.test_plan_filters:
                        filtered_tp_ids.update(
                            fnmatch.filter(test_plan_ids, filter))
                    filtered_tp_ids = list(filtered_tp_ids)
                    filtered_tp_ids.sort(
                        key=lambda tp_id: self.assistant.get_test_plan(
                            tp_id).name)
                    self._available_test_plans = [
                        self.assistant.get_test_plan(tp_id) for tp_id in
                        filtered_tp_ids]
                return {
                    'testplan_info_list': [{
                        "mod_id": tp.id,
                        "mod_name": tp.name,
                        "mod_selected":
                            tp.id == self.launcher.test_plan_default_selection,
                        "mod_disabled": False,
                    } for tp in self._available_test_plans],
                    'forced_selection': self.launcher.test_plan_forced
                }
            else:
                self._available_test_plans = [
                    self.assistant.get_test_plan(tp_id) for tp_id in
                    self.assistant.get_test_plans()]
        return {
            'testplan_info_list': [{
                "mod_id": tp.id,
                "mod_name": tp.name,
                "mod_selected": False,
                "mod_disabled": False,
            } for tp in self._available_test_plans],
            'forced_selection': False
        }

    @view
    def remember_testplan(self, test_plan_id):
        """Pick the test plan as the one in force."""
        if self.test_plan_id:
            # test plan has been previously selected. User changed mind, we
            # have to abandon the session
            self._finalize_session()
            self.assistant.start_new_session('Checkbox Converged session')
            self._timestamp = datetime.datetime.utcnow().isoformat()
        self.test_plan_id = test_plan_id
        self.assistant.select_test_plan(test_plan_id)
        self.assistant.bootstrap()
        # because session id (and storage) might have changed, let's share this
        # info with the qml side
        return {
            'session_id': self.assistant.get_session_id(),
            'session_dir': self.assistant.get_session_dir()
        }

    @view
    def get_categories(self):
        """Get categories selection data."""
        category_info_list = [{
            "mod_id": category.id,
            "mod_name": category.tr_name(),
            "mod_selected": True,
            "mod_disabled": False,
        } for category in (
            self.assistant.get_category(category_id)
            for category_id in self.assistant.get_participating_categories()
        )]
        category_info_list.sort(key=lambda ci: (ci['mod_name']))
        return {
            'category_info_list': category_info_list,
            'forced_selection': self.launcher.test_selection_forced
        }

    @view
    def remember_categories(self, selected_id_list):
        """Save category selection."""
        _logger.info("Selected categories: %s", selected_id_list)
        # Remove previously set filters
        self.assistant.remove_all_filters()
        self.assistant.filter_jobs_by_categories(selected_id_list)

    @view
    def get_available_tests(self):
        """
        Get all tests for selection purposes.

        The response object will contain only tests with category matching
        previously set list. Tests are sorted by (category, name)
        """
        category_names = {
            cat_id: self.assistant.get_category(cat_id).tr_name() for
            cat_id in self.assistant.get_participating_categories()}
        job_units = [self.assistant.get_job(job_id) for job_id in
                     self.assistant.get_static_todo_list()]
        mandatory_jobs = self.assistant.get_mandatory_jobs()
        test_info_list = [{
            "mod_id": job.id,
            "mod_name": job.tr_summary(),
            "mod_group": category_names[job.category_id],
            "mod_selected": True,
            "mod_disabled": job.id in mandatory_jobs,
        } for job in job_units]
        test_info_list.sort(key=lambda ti: (ti['mod_group'], ti['mod_name']))
        return {
            'test_info_list': test_info_list,
            'forced_selection': self.launcher.test_selection_forced
        }

    @view
    def get_rerun_candidates(self):
        """Get all the tests that might be selected for rerunning."""
        def rerun_predicate(job_state):
            return job_state.result.outcome in (
                IJobResult.OUTCOME_FAIL, IJobResult.OUTCOME_CRASH,
                IJobResult.OUTCOME_NOT_SUPPORTED, IJobResult.OUTCOME_SKIP)
        rerun_candidates = []
        todo_list = self.assistant.get_static_todo_list()
        job_units = {job_id: self.assistant.get_job(job_id) for job_id
                     in todo_list}
        job_states = {job_id: self.assistant.get_job_state(job_id) for job_id
                      in todo_list}
        category_names = {
            cat_id: self.assistant.get_category(cat_id).tr_name() for cat_id
            in self.assistant.get_participating_categories()}
        for job_id, job_state in job_states.items():
            if rerun_predicate(job_state):
                rerun_candidates.append({
                    "mod_id": job_id,
                    "mod_name": job_units[job_id].tr_summary(),
                    "mod_group": category_names[job_units[job_id].category_id],
                    "mod_selected": False
                    })
        return rerun_candidates

    @view
    def remember_tests(self, selected_id_list):
        """Save test selection."""
        self.index = 0
        self.assistant.use_alternate_selection(selected_id_list)
        self.assistant.update_app_blob(self._get_app_blob())
        _logger.info("Selected tests: %s", selected_id_list)
        return

    @view
    def get_next_test(self):
        """
        Get next text that is scheduled to run.

        :returns:
        Dictionary resembling JobDefinition or None if all tests are completed
        """
        todo_list = self.assistant.get_static_todo_list()
        if self.index < len(todo_list):
            job = self.assistant.get_job(todo_list[self.index])
            description = ""
            if job.tr_purpose() is not None:
                description = job.tr_purpose() + "\n"
            if job.tr_steps() is not None:
                    description += job.tr_steps()
            if not description:
                description = job.tr_description()
            test = {
                "name": job.tr_summary(),
                "description": description,
                "verificationDescription": job.tr_verification() if
                job.tr_verification() is not None else description,
                "plugin": job.plugin,
                "id": job.id,
                "partial_id": job.partial_id,
                "user": job.user,
                "qml_file": job.qml_file,
                "start_time": time.time(),
                "test_number": todo_list.index(job.id),
                "tests_count": len(todo_list),
                "command": job.command,
                "flags": job.get_flag_set()
            }
            return test
        else:
            return {}

    @view
    def register_test_result(self, test):
        """Registers outcome of a test."""
        _logger.info("Storing test result: %s", test)
        job_id = test['id']
        builder_kwargs = {
            'outcome': test['outcome'],
            'comments': test.get('comments', pod.UNSET),
            'execution_duration': time.time() - test['start_time'],
        }
        if 'result' in test:
            # if we're registering skipped test as an outcome of resuming
            # session, the result field of the test object will be missing
            builder_kwargs['return_code'] = test['result'].return_code
            builder_kwargs['io_log_filename'] = test['result'].io_log_filename
            builder_kwargs['io_log'] = test['result'].io_log
        else:
            builder_kwargs['return_code'] = 0
        result = JobResultBuilder(**builder_kwargs).get_result()
        self.assistant.use_job_result(job_id, result)
        self.index += 1
        self.assistant.update_app_blob(self._get_app_blob())

    @view
    def run_test_activity(self, test):
        """Run command associated with given test."""
        plugins_handled_natively = ['qml']
        res_builder = self.assistant.run_job(
            test['id'], self.ui, test['plugin'] in plugins_handled_natively)
        test['outcome'] = res_builder.outcome
        test['result'] = res_builder
        return test

    @view
    def get_results(self):
        """Get results object."""
        stats = self.assistant.get_summary()
        return {
            'totalPassed': stats[IJobResult.OUTCOME_PASS],
            'totalFailed': stats[IJobResult.OUTCOME_FAIL],
            'totalSkipped': stats[IJobResult.OUTCOME_SKIP] +
            stats[IJobResult.OUTCOME_NOT_SUPPORTED] +
            stats[IJobResult.OUTCOME_UNDECIDED]
        }

    @view
    def export_results(self, output_format, option_list):
        """Export results to file(s) in the user's 'Documents' directory."""
        self.assistant.finalize_session()
        dirname = self._get_user_directory_documents()
        return self.assistant.export_to_file(
            output_format, option_list, dirname)

    @view
    def submit_results(self, config):
        """Submit results to a service configured by config."""

        self.assistant.finalize_session()
        transport = {
            'hexr': self.assistant.get_canonical_hexr_transport,
            'hexr-staging': (
                lambda: self.assistant.get_canonical_hexr_transport(
                    staging=True)),
            'c3': (
                lambda: self.assistant.get_canonical_certification_transport(
                    config['secure_id'])),
            'c3-staging': (
                lambda: self.assistant.get_canonical_certification_transport(
                    config['secure_id'], staging=True)),
            'oauth': lambda: self.assistant.get_ubuntu_sso_oauth_transport(config),
        }[config['type']]()
        # Default to 'hexr' exporter as it provides xml submission format
        # (CertificationTransport expects xml format for instance.)
        submission_format = config.get(
            'submission_format',
            '2013.com.canonical.plainbox::hexr'
        )
        submission_options = config.get('submission_options', [])
        return self.assistant.export_to_transport(
            submission_format,
            transport,
            submission_options
        )

    def _prepare_transports(self):
        self._available_transports = get_all_transports()
        self.transports = dict()

    @view
    def get_certification_transport_config(self):
        """Returns the c3 (certification) transport configuration."""
        for report in self.launcher.stock_reports:
            self._prepare_stock_report(report)
        if 'c3' in self.launcher.transports:
            return self.launcher.transports['c3']
        elif 'c3-staging' in self.launcher.transports:
            return self.launcher.transports['c3-staging']
        return {}

    @view
    def export_results_with_launcher_settings(self):
        """
        Export results to file(s) in the user's 'Documents' directory.
        This method follows the launcher reports configuration.
        """
        self.assistant.finalize_session()
        for report in self.launcher.stock_reports:
            self._prepare_stock_report(report)
        # reports are stored in an ordinary dict(), so sorting them ensures
        # the same order of submitting them between runs.
        html_url = ""
        for name, params in sorted(self.launcher.reports.items()):
            exporter_id = self.launcher.exporters[params['exporter']]['unit']
            if self.launcher.transports[params['transport']]['type'] == 'file':
                path = self.launcher.transports[params['transport']]['path']
                cls = self._available_transports['file']
                self.transports[params['transport']] = cls(path)
                transport = self.transports[params['transport']]
                result = self.assistant.export_to_transport(
                    exporter_id, transport)
                if (
                    result and 'url' in result and
                    result['url'].endswith('html')
                ):
                    html_url = result['url']
        return html_url

    def _prepare_stock_report(self, report):
        # this is purposefully not using pythonic dict-keying for better
        # readability
        if not self.launcher.transports:
            self.launcher.transports = dict()
        if not self.launcher.exporters:
            self.launcher.exporters = dict()
        if not self.launcher.reports:
            self.launcher.reports = dict()
        if report == 'certification':
            self.launcher.exporters['hexr'] = {
                'unit': '2013.com.canonical.plainbox::hexr'}
            self.launcher.transports['c3'] = {
                'type': 'certification',
                'secure_id': self.launcher.transports.get('c3', {}).get(
                    'secure_id', None)}
            self.launcher.reports['upload to certification'] = {
                'transport': 'c3', 'exporter': 'hexr'}
        elif report == 'certification-staging':
            self.launcher.exporters['hexr'] = {
                'unit': '2013.com.canonical.plainbox::hexr'}
            self.launcher.transports['c3-staging'] = {
                'type': 'certification',
                'secure_id': self.launcher.transports.get('c3', {}).get(
                    'secure_id', None),
                'staging': 'yes'}
            self.launcher.reports['upload to certification-staging'] = {
                'transport': 'c3-staging', 'exporter': 'hexr'}
        elif report == 'submission_files':
            timestamp = datetime.datetime.utcnow().isoformat()
            base_dir = self._get_user_directory_documents()
            for exporter, file_ext in [('hexr', '.xml'), ('html', '.html'),
                                       ('xlsx', '.xlsx'), ('tar', '.tar.xz')]:
                path = os.path.join(base_dir, ''.join(
                    ['submission_', timestamp, file_ext]))
                self.launcher.transports['{}_file'.format(exporter)] = {
                    'type': 'file',
                    'path': path}
                if exporter not in self.launcher.exporters:
                    self.launcher.exporters[exporter] = {
                        'unit': '2013.com.canonical.plainbox::{}'.format(
                            exporter)}
                self.launcher.reports['2_{}_file'.format(exporter)] = {
                    'transport': '{}_file'.format(exporter),
                    'exporter': '{}'.format(exporter)
                }

    @view
    def drop_permissions(self, app_id, services):
        # TODO: use XDG once available
        trust_dbs = {
            'camera': '~/.local/share/CameraService/trust.db',
            'audio': '~/.local/share/PulseAudio/trust.db',
            'location': '~/.local/share/UbuntuLocationServices/trust.db',
        }
        sql = 'delete from requests where ApplicationId = (?);'

        for service in services:
            conn = None
            try:
                conn = sqlite3.connect(
                    os.path.expanduser(trust_dbs[service]),
                    isolation_level='EXCLUSIVE')
                conn.execute(sql, (app_id,))
                conn.commit()
            finally:
                if conn:
                    conn.close()

    @view
    def get_incomplete_sessions(self):
        """Get ids of sessions with an 'incomplete' flag."""
        self._incomplete_sessions = [
            s[0] for s in self.assistant.get_old_sessions(
                flags={'incomplete'}, allow_not_flagged=False)]
        return self._incomplete_sessions

    @view
    def delete_old_sessions(self, additional_sessions):
        """
        Delete session storages.

        :param additional_sessions:
            List of ids of sessions that should be removed.

        This function removes all complete sessions (i.e. the ones that session
        assistant returns when get_old_sessions is run with the default params)
        with the addition of the ones specified in the ``additional_sessions``
        param.
        """
        garbage = [s[0] for s in self.assistant.get_old_sessions()]
        garbage += additional_sessions
        self.assistant.delete_sessions(garbage)

    def _get_user_directory_documents(self):
        xdg_config_home = os.environ.get('XDG_CONFIG_HOME') or \
            os.path.expanduser('~/.config')
        with open(os.path.join(xdg_config_home, 'user-dirs.dirs')) as f:
            match = re.search(r'XDG_DOCUMENTS_DIR="(.*)"\n', f.read())
            if match:
                return match.group(1).replace("$HOME", os.getenv("HOME"))
            else:
                return os.path.expanduser('~/Documents')

    def _get_app_cache_directory(self):
        xdg_cache_home = os.environ.get('XDG_CACHE_HOME') or \
            os.path.expanduser('~/.cache')
        app_id = os.environ.get('APP_ID')
        if app_id:
            # Applications will always have write access to directories they
            # own as determined by the XDG base directory specification.
            # Specifically: XDG_CACHE_HOME/<APP_PKGNAME>
            #               XDG_RUNTIME_DIR/<APP_PKGNAME>
            #               XDG_RUNTIME_DIR/confined/<APP_PKGNAME> (for TMPDIR)
            #               XDG_DATA_HOME/<APP_PKGNAME>
            #               XDG_CONFIG_HOME/<APP_PKGNAME>
            # Note that <APP_PKGNAME> is not the APP_ID. In order to easily
            # handle upgrades and sharing data between executables in the same
            # app, we use the unversioned app package name for the writable
            # directories.
            return os.path.join(xdg_cache_home, app_id.split('_')[0])
        else:
            path = os.path.join(xdg_cache_home, "com.ubuntu.checkbox")
            if not os.path.exists(path):
                os.makedirs(path)
            elif not os.path.isdir(path):
                # as unlikely as it is, situation where path exists and is a
                # regular file neeeds to be signalled
                raise IOError("{} exists and is not a directory".format(path))
            return path

    def _get_app_blob(self):
        """
        Get json dump of with app-specific blob
        """
        return json.dumps(
            {
                'version': 1,
                'test_plan_id': self.test_plan_id,
                'index_in_run_list': self.index,
                'session_timestamp': self._timestamp,
            }).encode("UTF-8")

    def _get_embedded_providers(self, providers_dir):
        """
        Get providers included with the app

        :param providers_dir:
            Path within application tree from which to load providers
        :returns:
            list of loaded providers
        """
        provider_list = []
        app_root_dir = os.path.normpath(os.getenv(
            'APP_DIR', os.path.join(os.path.dirname(__file__), '..')))
        path = os.path.join(app_root_dir, os.path.normpath(providers_dir))
        _logger.info("Loading all providers from %s", path)
        if os.path.exists(path):
            embedded_providers = EmbeddedProvider1PlugInCollection(path)
            provider_list += embedded_providers.get_all_plugin_objects()
        return provider_list

    def _password_provider(self):
        if self._password is None:
            raise RuntimeError("execute_job called without providing password"
                               " first")
        return self._password

    def _finalize_session(self):
        self.test_plan_id = ""
        self.assistant.finalize_session()

    def remember_password(self, password):
        """
        Save password in app instance

        It deliberately doesn't use view decorator to omit all logging that
        might happen
        """
        self._password = password


def get_qml_logger(default_level):
    logging_level = collections.defaultdict(lambda: logging.INFO, {
        "debug": logging.DEBUG,
        "warning": logging.WARNING,
        "warn": logging.WARN,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
        "fatal": logging.FATAL})[default_level.lower()]
    logging.basicConfig(level=logging_level, stream=sys.stderr)
    return logging.getLogger('converged.qml')


create_app_object = CheckboxConvergedApplication
