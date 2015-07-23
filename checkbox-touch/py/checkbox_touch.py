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
import itertools
import json
import logging
import os
import pyotherside
import re
import time
import traceback

from plainbox.abc import IJobResult
from plainbox.impl import pod
from plainbox.impl.applogic import PlainBoxConfig
from plainbox.impl.clitools import ToolBase
from plainbox.impl.commands.inv_run import SilentUI
from plainbox.impl.result import JobResultBuilder
from plainbox.impl.runner import JobRunner
from plainbox.impl.secure.origin import Origin
from plainbox.impl.secure.qualifiers import FieldQualifier
from plainbox.impl.secure.qualifiers import OperatorMatcher
from plainbox.impl.secure.qualifiers import select_jobs
from plainbox.impl.session import SessionManager
from plainbox.impl.session import SessionMetaData
from plainbox.impl.session import SessionPeekHelper
from plainbox.impl.session import SessionResumeError
from plainbox.impl.session.storage import SessionStorageRepository
from plainbox.impl.unit.job import JobDefinition
from plainbox.impl.unit.validators import compute_value_map
from plainbox.public import get_providers
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

    __version__ = (1, 2, 0, 'final', 0)

    def __init__(self):
        if plainbox.__version__ < (0, 21):
            raise SystemExit("plainbox 0.21 required, you have {}".format(
                ToolBase.format_version_tuple(plainbox.__version__)))
        # adjust_logging(logging.INFO, ['checkbox.touch'], True)
        self.manager = None
        self.context = None
        self.runner = None
        self.index = 0  # NOTE: next test index
        # NOTE: This may also have "" representing None
        self.desired_category_ids = frozenset()
        self.desired_test_ids = frozenset()
        self.test_plan_id = ""
        self.resume_candidate_storage = None
        self.session_storage_repo = None
        self.timestamp = datetime.datetime.utcnow().isoformat()
        self.config = PlainBoxConfig()
        self._password = None
        self.ui = CheckboxTouchUI()

    def __repr__(self):
        return "app"

    @view
    def get_version_pair(self):
        return {
            'plainbox_version': ToolBase.format_version_tuple(
                plainbox.__version__),
            'application_version': ToolBase.format_version_tuple(
                self.__version__)
        }

    @view
    def start_session(self, providers_dir):
        if self.manager is not None:
            _logger.warning("start_session() should not be called twice!")
        else:
            self._init_session_storage_repo()
            self.manager = SessionManager.create(self.session_storage_repo)
            self.manager.add_local_device_context()
            self.context = self.manager.default_device_context
            # Add some all providers into the context
            for provider in self._get_default_providers(providers_dir):
                self.context.add_provider(provider)
            # Fill in the meta-data
            self.context.state.metadata.app_id = 'checkbox-touch'
            self.context.state.metadata.title = 'Checkbox Touch Session'
            self.context.state.metadata.flags.add('bootstrapping')
            # Checkpoint the session so that we have something to see
            self._checkpoint()

            # Prepare custom execution controller list
            from plainbox.impl.ctrl import UserJobExecutionController
            from sudo_with_pass_ctrl import \
                RootViaSudoWithPassExecutionController
            controllers = [
                RootViaSudoWithPassExecutionController(
                    self.context.provider_list, self._password_provider),
                UserJobExecutionController(self.context.provider_list),
            ]
            self.runner = JobRunner(
                self.manager.storage.location,
                self.context.provider_list,
                # TODO: tie this with well-known-dirs helper
                os.path.join(self.manager.storage.location, 'io-logs'),
                execution_ctrl_list=controllers)
        app_cache_dir = self._get_app_cache_directory()
        if not os.path.exists(app_cache_dir):
            os.makedirs(app_cache_dir)
        with open(os.path.join(app_cache_dir, 'session_id'),
                  'w') as f:
            f.write(self.manager.storage.id)
        return {
            'session_id': self.manager.storage.id,
            'session_dir': self.manager.storage.location
        }

    @view
    def resume_session(self, rerun_last_test, providers_dir):
        all_units = list(itertools.chain(
            *[p.unit_list for p in self._get_default_providers(
                providers_dir)]))
        try:
            self.manager = SessionManager.load_session(
                all_units, self.resume_candidate_storage)
        except IOError as exc:
            _logger.info("Exception raised when trying to resume"
                         "session: %s", str(exc))
            return {
                'session_id': None
            }
        self.context = self.manager.default_device_context
        metadata = self.context.state.metadata
        app_blob = json.loads(metadata.app_blob.decode("UTF-8"))
        self.runner = JobRunner(
            self.manager.storage.location,
            self.context.provider_list,
            os.path.join(self.manager.storage.location, 'io-logs'))
        self.index = app_blob['index_in_run_list']
        _logger.error(self.context.state.run_list)
        _logger.error(self.index)
        if not rerun_last_test:
            # Skip current test
            test = self.get_next_test()['result']
            test['outcome'] = 'skip'
            self.register_test_result(test)
        return {
            'session_id': self.manager.storage.id
        }

    @view
    def clear_session(self):
        self.manager = None
        self.context = None
        self.runner = None
        self.index = 0
        self.timestamp = datetime.datetime.utcnow().isoformat()
        self.desired_category_ids = frozenset()
        self.desired_test_ids = frozenset()
        self.resume_candidate_storage = None
        self.session_storage_repo = None
        os.unlink(os.path.join(self._get_app_cache_directory(), 'session_id'))

    @view
    def is_session_resumable(self):
        """
        Checks whether given session is resumable
        """
        resumable = False
        try:
            with open(os.path.join(self._get_app_cache_directory(),
                      'session_id')) as f:
                session_id = f.readline().rstrip('\n')
        except (OSError, IOError):
            session_id = None
        self._init_session_storage_repo()
        for storage in self.session_storage_repo.get_storage_list():
            data = storage.load_checkpoint()
            if len(data) == 0:
                continue
            try:
                metadata = SessionPeekHelper().peek(data)
                if (metadata.app_id == 'checkbox-touch'
                        and storage.id == session_id
                        and SessionMetaData.FLAG_INCOMPLETE in
                        metadata.flags):
                    self.resume_candidate_storage = storage
                    resumable = True
            except SessionResumeError as exc:
                _logger.info("Exception raised when trying to resume"
                             "session: %s", str(exc))
                return {
                    'resumable': False,
                    'errors_encountered': True
                }
        return {
            'resumable': resumable,
            'errors_encountered': False
        }

    @view
    def get_testplans(self):
        all_units = self.manager.default_device_context.unit_list
        return {
            'testplan_info_list': [{
                "mod_id": unit.id,
                "mod_name": unit.name,
                "mod_selected": False,
            } for unit in all_units if unit.Meta.name == 'test plan']
        }

    @view
    def remember_testplan(self, test_plan_id):
        self.context.invalidate_shared('potential_job_list')
        self.context.invalidate_shared('potential_category_map')
        self._init_test_plan_id(test_plan_id)

    @view
    def get_categories(self):
        """
        Get categories selection data.
        """
        potential_job_list = self.context.compute_shared(
            'potential_job_list', select_jobs,
            self.context.state.job_list, [self.test_plan.get_qualifier()])
        potential_category_map = self.context.compute_shared(
            'potential_category_map',
            self.test_plan.get_effective_category_map, potential_job_list)
        id_map = self.context.compute_shared(
            'id_map', compute_value_map, self.context, 'id')
        category_info_list = [{
            "mod_id": category.id,
            "mod_name": category.name,
            "mod_selected": True,
        } for category in (
            id_map[category_id][0]
            for category_id in set(potential_category_map.values())
        )]
        category_info_list.sort(key=lambda ci: ci['mod_name'])
        return {
            'category_info_list': category_info_list
        }

    @view
    def remember_categories(self, selected_id_list):
        """
        Save category selection
        """
        self.desired_category_ids = frozenset(selected_id_list)
        self.context.invalidate_shared('subset_job_list')
        self.context.invalidate_shared('effective_category_map')
        _logger.info("Selected categories: %s", self.desired_category_ids)

    @view
    def get_available_tests(self):
        """
        Get all tests for selection purposes.

        The response object will contain only tests with category matching
        previously set list. Tests are sorted by (category, name)
        """
        subset_job_list = self.context.compute_shared(
            'subset_job_list', select_jobs,
            self.context.state.job_list, [
                # Select everything the test plan selected
                self.test_plan.get_qualifier(),
                # Except jobs not matching the selected group of categories
                FieldQualifier(
                    JobDefinition.Meta.fields.category_id,
                    OperatorMatcher(not_contains, self.desired_category_ids),
                    Origin.get_caller_origin(), inclusive=False),
            ])
        effective_category_map = self.context.compute_shared(
            'effective_category_map',
            self.test_plan.get_effective_category_map, subset_job_list)
        for job_id, effective_category_id in effective_category_map.items():
            job_state = self.context.state.job_state_map[job_id]
            job_state.effective_category_id = effective_category_id
        id_map = self.context.compute_shared(
            'id_map', compute_value_map, self.context, 'id')
        test_info_list = [{
            "mod_id": job_id,
            "mod_name": id_map[job_id][0].tr_summary(),
            "mod_group": id_map[category_id][0].tr_name(),
            "mod_selected": True,
        } for job_id, category_id in effective_category_map.items()]
        test_info_list.sort(key=lambda ti: (ti['mod_group'], ti['mod_name']))
        return {
            'test_info_list': test_info_list
        }

    @view
    def remember_tests(self, selected_id_list):
        """
        Save test selection
        """
        self.desired_test_ids = frozenset(selected_id_list)
        _logger.info("Selected tests: %s", self.desired_test_ids)
        desired_job_list = self.context.compute_shared(
            'desired_job_list', select_jobs,
            self.context.state.job_list, [
                # Select everything the test plan selected
                self.test_plan.get_qualifier(),
                # Except all the jobs that weren't marked by the user
                FieldQualifier(
                    JobDefinition.Meta.fields.id,
                    OperatorMatcher(not_contains, self.desired_test_ids),
                    Origin.get_caller_origin(), inclusive=False)])
        _logger.info("Desired job list: %s", desired_job_list)
        self.context.state.update_desired_job_list(desired_job_list)
        _logger.info("Run job list: %s", self.context.state.run_list)
        self.context.state.metadata.flags.add('incomplete')
        self._checkpoint()

    @view
    def get_next_test(self):
        """
        Get next text that is scheduled to run
        Returns test object or None if all tests are completed
        """
        if self.index < len(self.context.state.run_list):
            job = self.context.state.run_list[self.index]
            job_state = self.context.state.job_state_map[job.id]
            # support for description field splitted into 3 subfields
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
                "user": job.user,
                "qml_file": job.qml_file,
                "start_time": time.time(),
                "test_number": self.index,
                "tests_count": len(self.context.state.run_list),
                "command": job.command,
                "flags": job.get_flag_set()
            }
            if not job_state.can_start():
                test["outcome"] = "skip"
                test["comments"] = job_state.get_readiness_description()
                self.register_test_result(test)
                return self.get_next_test()["result"]
            return test
        else:
            return {}

    @view
    def register_test_result(self, test):
        """
        Registers outcome of a test
        """
        _logger.info("Storing test result: %s", test)
        job_id = test['id']
        job = self.context.state.job_state_map[job_id].job
        builder_kwargs = {
            'outcome': test['outcome'],
            'comments': test.get('comments', pod.UNSET)
        }
        # some result may already have been saved if the job had some activity
        # to run, i.e. result object is available in the test object
        try:
            builder_kwargs['io_log_filename'] = test['result'].io_log_filename
        except KeyError:
            builder_kwargs['execution_duration'] = (
                time.time() - test['start_time'])
        result = JobResultBuilder(**builder_kwargs).get_result()
        self.context.state.update_job_result(job, result)
        self.index += 1
        self._checkpoint()

    @view
    def run_test_activity(self, test):
        """
        Run command associated with given test
        """
        job_id = test['id']
        job_state = self.context.state.job_state_map[job_id]
        job = job_state.job
        self.context.state.running_job_name = job_id
        self._checkpoint()
        try:
            result = self.runner.run_job(job, job_state, self.config, self.ui)
        except OSError as exc:
            result = JobResultBuilder(
                outcome='fail',
                comment=str(exc),
            ).get_result()
        self.context.state.running_job_name = None
        self._checkpoint()
        test['outcome'] = result.outcome
        test['result'] = result
        return test

    @view
    def get_results(self):
        """
        Get results object
        """
        self.context.state.metadata.flags.remove('incomplete')
        self._checkpoint()
        stats = collections.defaultdict(int)
        for job_state in self.context.state.job_state_map.values():
            stats[job_state.result.outcome] += 1
        return {
            'totalPassed': stats[IJobResult.OUTCOME_PASS],
            'totalFailed': stats[IJobResult.OUTCOME_FAIL],
            'totalSkipped': stats[IJobResult.OUTCOME_SKIP],
        }

    @view
    def export_results(self, output_format, option_list):
        """
        Export results to file
        """
        # Export results in the user's Documents directory
        dirname = self._get_user_directory_documents()
        exporter = self.manager.create_exporter(output_format, option_list)
        extension = exporter.unit.file_extension
        filename = ''.join(['submission_', self.timestamp, '.', extension])
        output_file = os.path.join(dirname, filename)
        with open(output_file, 'wb') as stream:
            exporter.dump_from_session_manager(self.manager, stream)
        return output_file

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


    def _checkpoint(self):
        self.context.state.metadata.app_blob = self._get_app_blob()
        self.manager.checkpoint()

    def _get_app_blob(self):
        """
        Get json dump of with app-specific blob
        """
        return json.dumps(
            {
                'version': 1,
                'test_plan_id': self.test_plan_id,
                'index_in_run_list': self.index,
            }).encode("UTF-8")

    def _init_test_plan_id(self, test_plan_id):
        """
        Validates and stores test_plan_id
        """
        if not isinstance(test_plan_id, str):
            raise TypeError("test_plan_id must be a string")
        # Look up the test plan with the specified identifier
        id_map = self.context.compute_shared(
            'id_map', compute_value_map, self.context, 'id')
        try:
            test_plan = id_map[test_plan_id][0]
        except KeyError:
            raise ValueError(
                "cannot find any unit with id: {!r}".format(test_plan_id))
        if test_plan.Meta.name != 'test plan':
            raise ValueError(
                "unit {!r} is not a test plan".format(test_plan_id))
        self.test_plan = test_plan

    def _init_session_storage_repo(self):
        """
        Init storage repository.
        """
        self.session_storage_repo = SessionStorageRepository(
            self._get_app_cache_directory())

    def _get_default_providers(self, providers_dir):
        """
        Get providers

        :param providers_dir:
            Path within application tree from which to load providers
        :returns:
            list of loaded providers
        """
        provider_list = get_providers()
        # when running on ubuntu-touch device, APP_DIR env var is present
        # and points to touch application top directory
        app_root_dir = os.path.normpath(os.getenv(
            'APP_DIR', os.path.join(os.path.dirname(__file__), '..')))
        path = os.path.join(app_root_dir,
                            os.path.normpath(providers_dir))
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

    def remember_password(self, password):
        """
        Save password in app instance

        It deliberately doesn't use view decorator to omit all logging that
        might happen
        """
        self._password = password


def get_qml_logger(default_level):
    logging_level = collections.defaultdict(lambda:logging.INFO, {
        "debug": logging.DEBUG,
        "warning": logging.WARNING,
        "warn": logging.WARN,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
        "fatal": logging.FATAL})[default_level.lower()]
    logging.basicConfig(level=logging_level, stream=sys.stderr)
    return logging.getLogger('checkbox.touch.qml')


create_app_object = CheckboxTouchApplication
