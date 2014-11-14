# This file is part of Checkbox.
#
# Copyright 2014 Canonical Ltd.
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
import builtins
import collections
import datetime
import itertools
import json
import logging
import os
import re
import sys
import time
import traceback

from plainbox.abc import IJobResult
from plainbox.impl.clitools import ToolBase
from plainbox.impl.exporter import get_all_exporters
from plainbox.impl.providers.special import get_categories
from plainbox.impl.providers.special import get_stubbox
from plainbox.impl.providers.v1 import all_providers
from embedded_providers import EmbeddedProvider1PlugInCollection
from plainbox.impl.runner import JobRunner
from plainbox.impl.secure.origin import Origin
from plainbox.impl.secure.qualifiers import FieldQualifier
from plainbox.impl.secure.qualifiers import OperatorMatcher
from plainbox.impl.secure.qualifiers import select_jobs
from plainbox.impl.session import SessionManager
from plainbox.impl.session import SessionMetaData
from plainbox.impl.session import SessionPeekHelper
from plainbox.impl.session.storage import SessionStorageRepository
from plainbox.impl.unit.job import JobDefinition
from plainbox.impl.unit.validators import compute_value_map
import plainbox

_logger = logging.getLogger('checkbox.touch')
_manager = None


class VerboseLifecycle:
    """
    Mix-in class for verbose lifecycle reporting
    """

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        _logger.debug("new %s %x", cls.__name__, id(self))
        return self

    def __del__(self):
        _logger.debug("del %s %x", self.__class__.__name__, id(self))


class RemoteObjectLifecycleManager(VerboseLifecycle):
    """
    Remote object life-cycle manager

    This class aids in handling non-trivial objects that are referenced from
    QML (via pyotherside) but really stored on the python side.
    """

    def __init__(self):
        self._count = 0
        self._handle_map = {}

    def unref(self, handle: int):
        """
        Remove a reference represented by the specified handle
        """
        _logger.debug("unref %s", handle)
        del self._handle_map[handle]

    def ref(self, obj: object) -> int:
        """
        Store a reference to an object and return the handle
        """
        self._count += 1
        handle = self._count
        self._handle_map[handle] = obj
        _logger.debug("ref %r -> %s", obj, handle)
        return handle

    def invoke(self, handle: int, func: str, args):
        """
        Call a method on a object represented by the handle

        :param handle:
            A (numeric) handle to the objecet
        :param func:
            The (name of the) function to call
        :param args:
            A list of positional arguments to pass
        :returns:
            The value returned by the called method
        """
        obj = self._handle_map[handle]
        impl = getattr(obj, func)
        retval = impl(*args)
        return retval


class PlainboxApplication(VerboseLifecycle, metaclass=abc.ABCMeta):
    """
    Base class for plainbox-based applications.

    Concrete subclasses of this class should implement get_version_pair() and
    add any additional methods that they would like to call.
    """

    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)

    @classmethod
    def create_and_get_handle(cls):
        """
        Create an instance of the high-level PlainBox object

        :returns:
            A handle to a fresh instance of :class:`PlainBox`
        """
        return _manager.ref(cls())

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


class FakeCheckboxTouchApplication(PlainboxApplication):

    __version__ = (0, 2, 0, 'dev', 0)

    def __init__(self):
        if plainbox.__version__ < (0, 14):
            raise SystemExit("plainbox 0.14 required, you have {}".format(
                ToolBase.format_version_tuple(plainbox.__version__)))
        # adjust_logging(logging.INFO, ['checkbox.touch'], True)
        self.index = 0
        self.max_tests = 50
        self.max_categories = 30

    def __repr__(self):
        return "fake-app"

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
        return {
            'session_id': 'fake'
        }

    @view
    def get_testplans(self):
        return {
            'testplan_info_list': [{
                "mod_id": "id-{}".format(i),
                "mod_name": "name-{}".format(i),
                "mod_selected": True,
            } for i in range(self.max_categories)]
        }

    @view
    def remember_testplan(self):
        pass

    @view
    def get_categories(self):
        return {
            'category_info_list': [{
                "mod_id": "id-{}".format(i),
                "mod_name": "name-{}".format(i),
                "mod_selected": True,
            } for i in range(self.max_categories)]
        }

    @view
    def remember_categories(self, selected_id_list):
        pass

    @view
    def get_available_tests(self):
        return {
            'test_info_list': sorted([{
                "mod_id": "id-{}".format(i),
                "mod_name": "name-{}".format(i),
                "mod_group": "group-{}".format(i % 3),
                "mod_selected": True,
                } for i in range(self.max_tests)],
                key=lambda item: item['mod_group'])
        }

    @view
    def remember_tests(self, selected_id_list):
        pass

    @view
    def get_next_test(self):
        if self.index < self.max_tests:
            result = {
                "id": "id-{}".format(self.index),
                "name": 'name-{}'.format(self.index),
                "description": 'description-{}'.format(self.index),
                "verificationDescription": "Verification",
                "plugin": "manual"
            }
            self.index += 1
            return result
        else:
            return {}

    @view
    def register_test_result(self, test):
        pass

    @view
    def run_test_activity(self, test):
        test['outcome'] = 'pass'
        return test

    @view
    def get_results(self):
        return {
            'totalPassed': 31,
            'totalFailed': 9,
            'totalSkipped': 10
        }


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

    __version__ = (0, 2, 0, 'dev', 0)

    def __init__(self):
        if plainbox.__version__ < (0, 13):
            raise SystemExit("plainbox 0.13 required, you have {}".format(
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
    def start_session(self):
        if self.manager is not None:
            _logger.warning("start_session() should not be called twice!")
        else:
            self._init_session_storage_repo()
            self.manager = SessionManager.create(self.session_storage_repo)
            self.manager.add_local_device_context()
            self.context = self.manager.default_device_context
            # Add some all providers into the context
            for provider in self._get_default_providers():
                self.context.add_provider(provider)
            # Fill in the meta-data
            self.context.state.metadata.app_id = 'checkbox-touch'
            self.context.state.metadata.title = 'Checkbox Touch Session'
            self.context.state.metadata.flags.add('bootstrapping')
            # Checkpoint the session so that we have something to see
            self._checkpoint()
            self.runner = JobRunner(
                self.manager.storage.location,
                self.context.provider_list,
                # TODO: tie this with well-known-dirs helper
                os.path.join(self.manager.storage.location, 'io-logs'))
        return {
            'session_id':  self.manager.storage.id
        }

    @view
    def resume_session(self, rerun_last_test):
        all_units = list(
            itertools.chain(*[
                p.get_units()[0] for p in self._get_default_providers()]))
        self.manager = SessionManager.load_session(
            all_units, self.resume_candidate_storage)
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
            'session_id':  self.manager.storage.id
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

    @view
    def is_session_resumable(self, session_id):
        """
        Checks whether given session is resumable
        """
        resumable = False
        self._init_session_storage_repo()
        for storage in self.session_storage_repo.get_storage_list():
            data = storage.load_checkpoint()
            if len(data) == 0:
                continue
            metadata = SessionPeekHelper().peek(data)
            if (metadata.app_id == 'checkbox-touch'
                    and storage.id == session_id
                    and SessionMetaData.FLAG_INCOMPLETE in metadata.flags):
                self.resume_candidate_storage = storage
                resumable = True

        return {
            'resumable': resumable
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
            test = {
                "name": job.tr_summary(),
                "description": job.tr_description(),
                "verificationDescription": job.tr_description(),
                "plugin": job.plugin,
                "id": job.id,
                "start_time": time.time()
            }
            if not job_state.can_start():
                test["outcome"] = "skip"
                test["comments"] = job_state.get_readiness_description()
                self.register_test_result(test)
                return self.get_next_test()
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
        outcome = test['outcome']
        job = self.context.state.job_state_map[job_id].job
        result = self.context.state.job_state_map[job_id].result
        result.outcome = outcome
        result.execution_duration = time.time() - test['start_time']
        self.context.state.update_job_result(job, result)
        self.index += 1
        self._checkpoint()

    @view
    def run_test_activity(self, test):
        """
        Run command associated with given test
        """
        job_id = test['id']
        job = self.context.state.job_state_map[job_id].job
        self.context.state.running_job_name = job_id
        self._checkpoint()
        try:
            result = self.runner.run_job(job)
        except OSError as exc:
            result = self.context.state.job_state_map[job_id].result
            result.outcome = 'fail'
            result.comment = str(exc)
        self.context.state.update_job_result(job, result)
        self.context.state.running_job_name = None
        self._checkpoint()
        test['outcome'] = result.outcome
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
        filename = ''.join(['submission_', self.timestamp, '.', output_format])
        output_file = os.path.join(dirname, filename)
        with open(output_file, 'wb') as stream:
            self._export_session_to_stream(output_format, option_list, stream)
        return output_file

    def _get_user_directory_documents(self):
        xdg_config_home = os.environ.get('XDG_CONFIG_HOME') or \
                          os.path.expanduser('~/.config')
        with open(os.path.join(xdg_config_home, 'user-dirs.dirs')) as f:
            match = re.search(r'XDG_DOCUMENTS_DIR="(.*)"\n', f.read())
            if match:
                return match.group(1)
            else:
                return os.path.expanduser('~')

    def _export_session_to_stream(self, output_format, option_list,
                                  stream):
        exporter_cls = get_all_exporters()[output_format]
        exporter = exporter_cls(option_list)
        data_subset = exporter.get_session_data_subset(
            self.context.state)
        exporter.dump(data_subset, stream)

    def _checkpoint(self):
        self.context.state.metadata.app_blob = self._get_app_blob()
        self.manager.checkpoint()

    def _get_app_blob(self):
        """
        Get json dump of with app-specific blob
        """
        return json.dumps({
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
        self.session_storage_repo = SessionStorageRepository(
            os.path.expandvars(
                '$XDG_CACHE_HOME/'
                'com.canonical.certification.checkbox-touch'))

    def _get_default_providers(self):
        providers_collection = all_providers.get_all_plugin_objects()
        # when running on ubuntu-touch device, APP_DIR env var is present
        # and points to touch application top directory
        path = os.path.join(os.path.expandvars('$APP_DIR'), 'providers')
        if os.path.exists(path):
            embedded_providers = EmbeddedProvider1PlugInCollection(path)
            providers_collection += embedded_providers.get_all_plugin_objects()
        return providers_collection


def bootstrap():
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    logging.info("environ: %r", os.environ)
    logging.info("path: %r", sys.path)
    # from plainbox.impl.logging import adjust_logging
    # from plainbox.impl.logging import setup_logging
    # Setup logging
    # setup_logging()
    # adjust_logging(logging.DEBUG, ['checkbox.stack'], True)
    # Create the Javascript <=> Python remote object lifecycle manager
    manager = RemoteObjectLifecycleManager()
    # Expose top-level functions for pyotherside's simplicity
    builtins.py_ref = manager.ref
    builtins.py_unref = manager.unref
    builtins.py_invoke = manager.invoke
    return manager


create_app_object = CheckboxTouchApplication.create_and_get_handle
_manager = bootstrap()
