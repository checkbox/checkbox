# This file is part of Checkbox.
#
# Copyright 2014-2015 Canonical Ltd.
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
import json
import logging
import os
import pyotherside
import sqlite3
import re
import time
import traceback

from plainbox.abc import IJobResult
from plainbox.impl import pod
from plainbox.impl.clitools import ToolBase
from plainbox.impl.commands.inv_run import SilentUI
from plainbox.impl.result import JobResultBuilder
from plainbox.impl.session.assistant import SessionAssistant
import plainbox

from embedded_providers import EmbeddedProvider1PlugInCollection

_logger = logging.getLogger('checkbox.touch')


class CheckboxTouchUI(SilentUI):
    """
    Class that connects checkbox-touch with plainbox.

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


class CheckboxTouchApplication(PlainboxApplication):
    """
    Class implementing the whole checkbox-touch application logic.

    This class exposes methods that can be called by the javascript embedded
    into many of the QML views. Each method implements a request / response
    semantics where the request is the set of data passed to python from
    javascript and the response is the python dictionary returned and processed
    back on the javascript side.

    This model follows the similar web development mechanics where the browser
    can issue asynchronous requests in reaction to user interactions and uses
    response data to alter the user interface.
    """

    __version__ = (1, 3, 0, 'dev', 0)

    def __init__(self):
        if plainbox.__version__ < (0, 22):
            raise SystemExit("plainbox 0.22 required, you have {}".format(
                ToolBase.format_version_tuple(plainbox.__version__)))
        self.assistant = SessionAssistant('checkbox-converged')
        self.ui = CheckboxTouchUI()
        self.index = 0
        self._password = None
        self._timestamp = None
        self._latest_session = None
        self.test_plan_id = None
        self.resume_candidate_storage = None
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

    def __repr__(self):
        return "app"

    @view
    def load_providers(self, providers_dir):
        self.assistant.select_providers(
            '*',
            additional_providers=self._get_embedded_providers(providers_dir))

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
    def resume_session(self, rerun_last_test):
        """
        Resume latest sesssion.

        :param rerun_last_test:
            A bool stating whether runtime should repeat the test, that the app
            was executing when it was interrupted.
        """
        metadata = self.assistant.resume_session(self._latest_session)
        app_blob = json.loads(metadata.app_blob.decode("UTF-8"))
        self.index = app_blob['index_in_run_list']
        self.test_plan_id = app_blob['test_plan_id']
        self.assistant.select_test_plan(self.test_plan_id)
        self.assistant.bootstrap()

        if not rerun_last_test:
            # Skip current test
            test = self.get_next_test()['result']
            test['outcome'] = 'skip'
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
        test_plan_units = [self.assistant.get_test_plan(tp_id) for tp_id in
                           self.assistant.get_test_plans()]
        return {
            'testplan_info_list': [{
                "mod_id": tp.id,
                "mod_name": tp.name,
                "mod_selected": False,
                "mod_disabled": False,
            } for tp in test_plan_units]
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
            "mod_name": category.name,
            "mod_selected": True,
            "mod_disabled": False,
        } for category in (
            self.assistant.get_category(category_id)
            for category_id in self.assistant.get_participating_categories()
        )]
        return {'category_info_list': category_info_list}

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
        return {'test_info_list': test_info_list}

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
            'execution_duration': time.time() - test['start_time']
        }
        try:
            # if we're registering skipped test as an outcome of resuming
            # session, the result field of the test object will be missing
            builder_kwargs['io_log_filename'] = test['result'].io_log_filename
        except KeyError:
            pass

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
            stats[IJobResult.OUTCOME_NOT_SUPPORTED]
        }

    @view
    def export_results(self, output_format, option_list):
        """Export results to file(s) in the user's 'Documents' directory.."""
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
    return logging.getLogger('checkbox.touch.qml')


create_app_object = CheckboxTouchApplication
