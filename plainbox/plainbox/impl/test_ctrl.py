# This file is part of Checkbox.
#
# Copyright 2012, 2013 Canonical Ltd.
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
plainbox.impl.test_ctrl
=======================

Test definitions for plainbox.impl.ctrl module
"""

from subprocess import CalledProcessError
from unittest import TestCase
import os

from plainbox.abc import IJobResult
from plainbox.abc import IProvider1
from plainbox.abc import IProviderBackend1
from plainbox.impl.applogic import PlainBoxConfig
from plainbox.impl.ctrl import CheckBoxExecutionController
from plainbox.impl.ctrl import CheckBoxSessionStateController
from plainbox.impl.ctrl import QmlJobExecutionController
from plainbox.impl.ctrl import RootViaPTL1ExecutionController
from plainbox.impl.ctrl import RootViaPkexecExecutionController
from plainbox.impl.ctrl import RootViaSudoExecutionController
from plainbox.impl.ctrl import SymLinkNest
from plainbox.impl.ctrl import UserJobExecutionController
from plainbox.impl.ctrl import gen_rfc822_records_from_io_log
from plainbox.impl.ctrl import get_via_cycle
from plainbox.impl.job import JobDefinition
from plainbox.impl.resource import Resource
from plainbox.impl.resource import ResourceExpression
from plainbox.impl.result import MemoryJobResult
from plainbox.impl.secure.origin import JobOutputTextSource
from plainbox.impl.secure.origin import Origin
from plainbox.impl.secure.providers.v1 import Provider1
from plainbox.impl.secure.rfc822 import RFC822Record
from plainbox.impl.secure.rfc822 import RFC822SyntaxError
from plainbox.impl.session import InhibitionCause
from plainbox.impl.session import JobReadinessInhibitor
from plainbox.impl.session import JobState
from plainbox.impl.session import SessionState
from plainbox.vendor import extcmd
from plainbox.vendor import mock


class CheckBoxSessionStateControllerTests(TestCase):

    def setUp(self):
        self.ctrl = CheckBoxSessionStateController()

    def test_get_dependency_set(self):
        # Job with no dependencies
        job_a = JobDefinition({})
        self.assertEqual(
            self.ctrl.get_dependency_set(job_a), set())
        # Job with direct dependencies
        job_b = JobDefinition({
            'depends': 'j1, j2'
        })
        self.assertEqual(
            self.ctrl.get_dependency_set(job_b),
            {('direct', 'j1'), ('direct', 'j2')})
        # Job with resouce dependencies
        job_c = JobDefinition({
            'requires': 'j3.attr == 1'
        })
        self.assertEqual(
            self.ctrl.get_dependency_set(job_c),
            {('resource', 'j3')})
        # Job with ordering dependencies
        job_d = JobDefinition({
            'after': 'j1, j2'
        })
        self.assertEqual(
            self.ctrl.get_dependency_set(job_d),
            {('ordering', 'j1'), ('ordering', 'j2')})
        # Job with both direct and resource dependencies
        job_e = JobDefinition({
            'depends': 'j4',
            'requires': 'j5.attr == 1'
        })
        self.assertEqual(
            self.ctrl.get_dependency_set(job_e),
            {('direct', 'j4'), ('resource', 'j5')})
        # Job with both direct and resource dependencies
        # on the same job (j6)
        job_f = JobDefinition({
            'depends': 'j6',
            'requires': 'j6.attr == 1'
        })
        self.assertEqual(
            self.ctrl.get_dependency_set(job_f),
            {('direct', 'j6'), ('resource', 'j6')})

    def test_get_inhibitor_list_PENDING_RESOURCE(self):
        # verify that jobs that require a resource that hasn't been
        # invoked yet produce the PENDING_RESOURCE inhibitor
        j1 = JobDefinition({
            'id': 'j1',
            'requires': 'j2.attr == "ok"'
        })
        j2 = JobDefinition({
            'id': 'j2'
        })
        session_state = mock.MagicMock(spec=SessionState)
        session_state.job_state_map['j2'].job = j2
        session_state.resource_map = {}
        self.assertEqual(
            self.ctrl.get_inhibitor_list(session_state, j1),
            [JobReadinessInhibitor(
                InhibitionCause.PENDING_RESOURCE,
                j2, ResourceExpression('j2.attr == "ok"'))])

    def test_get_inhibitor_list_FAILED_RESOURCE(self):
        # verify that jobs that require a resource that has been
        # invoked and produced resources but the expression dones't
        # evaluate to True produce the FAILED_RESOURCE inhibitor
        j1 = JobDefinition({
            'id': 'j1',
            'requires': 'j2.attr == "ok"'
        })
        j2 = JobDefinition({
            'id': 'j2'
        })
        session_state = mock.MagicMock(spec=SessionState)
        session_state.job_state_map['j2'].job = j2
        session_state.resource_map = {
            'j2': [Resource({'attr': 'not-ok'})]
        }
        self.assertEqual(
            self.ctrl.get_inhibitor_list(session_state, j1),
            [JobReadinessInhibitor(
                InhibitionCause.FAILED_RESOURCE,
                j2, ResourceExpression('j2.attr == "ok"'))])

    def test_get_inhibitor_list_good_resource(self):
        # verify that jobs that require a resource that has been invoked and
        # produced resources for which the expression evaluates to True don't
        # have any inhibitors
        j1 = JobDefinition({
            'id': 'j1',
            'requires': 'j2.attr == "ok"'
        })
        j2 = JobDefinition({
            'id': 'j2'
        })
        session_state = mock.MagicMock(spec=SessionState)
        session_state.resource_map = {
            'j2': [Resource({'attr': 'ok'})]
        }
        session_state.job_state_map['j2'].job = j2
        self.assertEqual(
            self.ctrl.get_inhibitor_list(session_state, j1), [])

    def test_get_inhibitor_list_PENDING_DEP(self):
        # verify that jobs that depend on another job or wait (via after) for
        # another  that hasn't been invoked yet produce the PENDING_DEP
        # inhibitor
        j1 = JobDefinition({
            'id': 'j1',
            'depends': 'j2',
            'after': 'j3',
        })
        j2 = JobDefinition({
            'id': 'j2'
        })
        j3 = JobDefinition({
            'id': 'j3'
        })
        session_state = mock.MagicMock(spec=SessionState)
        session_state.job_state_map = {
            'j1': mock.Mock(spec_set=JobState),
            'j2': mock.Mock(spec_set=JobState),
            'j3': mock.Mock(spec_set=JobState),
        }
        jsm_j2 = session_state.job_state_map['j2']
        jsm_j2.job = j2
        jsm_j2.result.outcome = IJobResult.OUTCOME_NONE
        jsm_j3 = session_state.job_state_map['j3']
        jsm_j3.job = j3
        jsm_j3.result.outcome = IJobResult.OUTCOME_NONE
        self.assertEqual(self.ctrl.get_inhibitor_list(session_state, j1), [
            JobReadinessInhibitor(InhibitionCause.PENDING_DEP, j2, None),
            JobReadinessInhibitor(InhibitionCause.PENDING_DEP, j3, None),
        ])

    def test_get_inhibitor_list_FAILED_DEP(self):
        # verify that jobs that depend on another job that ran but
        # didn't result in OUTCOME_PASS produce the FAILED_DEP
        # inhibitor.
        j1 = JobDefinition({
            'id': 'j1',
            'depends': 'j2',
            'after': 'j3',
        })
        j2 = JobDefinition({
            'id': 'j2'
        })
        j3 = JobDefinition({
            'id': 'j3'
        })
        session_state = mock.MagicMock(spec=SessionState)
        session_state.job_state_map = {
            'j1': mock.Mock(spec_set=JobState),
            'j2': mock.Mock(spec_set=JobState),
            'j3': mock.Mock(spec_set=JobState),
        }
        jsm_j2 = session_state.job_state_map['j2']
        jsm_j2.job = j2
        jsm_j2.result.outcome = IJobResult.OUTCOME_FAIL
        jsm_j3 = session_state.job_state_map['j3']
        jsm_j3.job = j3
        jsm_j3.result.outcome = IJobResult.OUTCOME_FAIL
        self.assertEqual(
            self.ctrl.get_inhibitor_list(session_state, j1),
            [JobReadinessInhibitor(
                InhibitionCause.FAILED_DEP, j2, None)])

    def test_get_inhibitor_list_good_dep(self):
        # verify that jobs that depend on another job that ran and has outcome
        # equal to OUTCOME_PASS don't have any inhibitors
        j1 = JobDefinition({
            'id': 'j1',
            'depends': 'j2',
            'after': 'j3'
        })
        j2 = JobDefinition({
            'id': 'j2'
        })
        j3 = JobDefinition({
            'id': 'j3'
        })
        session_state = mock.MagicMock(spec=SessionState)
        session_state.job_state_map = {
            'j1': mock.Mock(spec_set=JobState),
            'j2': mock.Mock(spec_set=JobState),
            'j3': mock.Mock(spec_set=JobState),
        }
        jsm_j2 = session_state.job_state_map['j2']
        jsm_j2.job = j2
        jsm_j2.result.outcome = IJobResult.OUTCOME_PASS
        jsm_j3 = session_state.job_state_map['j3']
        jsm_j3.job = j3
        jsm_j3.result.outcome = IJobResult.OUTCOME_PASS
        self.assertEqual(
            self.ctrl.get_inhibitor_list(session_state, j1), [])

    def test_observe_result__normal(self):
        job = mock.Mock(spec=JobDefinition)
        result = mock.Mock(spec=IJobResult)
        session_state = mock.MagicMock(spec=SessionState)
        self.ctrl.observe_result(session_state, job, result)
        # Ensure that result got stored
        self.assertIs(
            session_state.job_state_map[job.id].result, result)
        # Ensure that signals got fired
        session_state.on_job_state_map_changed.assert_called_once_with()
        session_state.on_job_result_changed.assert_called_once_with(
            job, result)

    def test_observe_result__OUTCOME_NONE(self):
        job = mock.Mock(spec=JobDefinition, plugin='resource')
        result = mock.Mock(spec=IJobResult, outcome=IJobResult.OUTCOME_NONE)
        session_state = mock.MagicMock(spec=SessionState)
        self.ctrl.observe_result(session_state, job, result)
        # Ensure that result got stored
        self.assertIs(
            session_state.job_state_map[job.id].result, result)
        # Ensure that signals got fired
        session_state.on_job_state_map_changed.assert_called_once_with()
        session_state.on_job_result_changed.assert_called_once_with(
            job, result)
        # Ensure that a resource was *not* defined
        self.assertEqual(session_state.set_resource_list.call_count, 0)

    def test_observe_result__resource(self):
        job = mock.Mock(spec=JobDefinition, plugin='resource')
        result = mock.Mock(spec=IJobResult, outcome=IJobResult.OUTCOME_PASS)
        result.get_io_log.return_value = [
            (0, 'stdout', b'attr: value1\n'),
            (0, 'stdout', b'\n'),
            (0, 'stdout', b'attr: value2\n')]
        session_state = mock.MagicMock(spec=SessionState)
        self.ctrl.observe_result(session_state, job, result)
        # Ensure that result got stored
        self.assertIs(
            session_state.job_state_map[job.id].result, result)
        # Ensure that signals got fired
        session_state.on_job_state_map_changed.assert_called_once_with()
        session_state.on_job_result_changed.assert_called_once_with(
            job, result)
        # Ensure that new resource was defined
        session_state.set_resource_list.assert_called_once_with(
            job.id, [
                Resource({'attr': 'value1'}), Resource({'attr': 'value2'})])

    @mock.patch('plainbox.impl.ctrl.logger')
    def test_observe_result__broken_resource(self, mock_logger):
        job = mock.Mock(spec=JobDefinition, plugin='resource')
        result = mock.Mock(spec=IJobResult, outcome=IJobResult.OUTCOME_PASS)
        result.get_io_log.return_value = [(0, 'stdout', b'barf\n')]
        session_state = mock.MagicMock(spec=SessionState)
        self.ctrl.observe_result(session_state, job, result)
        # Ensure that result got stored
        self.assertIs(
            session_state.job_state_map[job.id].result, result)
        # Ensure that signals got fired
        session_state.on_job_state_map_changed.assert_called_once_with()
        session_state.on_job_result_changed.assert_called_once_with(
            job, result)
        # Ensure that a warning was logged
        mock_logger.warning.assert_called_once_with(
            "local script %s returned invalid RFC822 data: %s",
            job.id, RFC822SyntaxError(
                None, 1, "Unexpected non-empty line: 'barf\\n'"))

    @mock.patch('plainbox.impl.ctrl.gen_rfc822_records_from_io_log')
    def test_observe_result__local_typical(self, mock_gen):
        """
        verify side effects of using observe_result() that would define a new
        job
        """
        # Job A is any example job
        job_a = JobDefinition({'id': 'a', 'plugin': 'shell', 'command': ':'})
        # Job B is a job that prints the definition of job A
        job_b = JobDefinition({'id': 'b', 'plugin': 'local'})
        # Result B is a fake result of running job B
        result_b = MemoryJobResult({'outcome': 'pass'})
        # Session knows about just B
        session_state = SessionState([job_b])
        # Mock gen_rfc822_records_from_io_log to produce one mock record
        mock_gen.return_value = [RFC822Record({})]
        # Mock job B to create job A as a child if asked to
        with mock.patch.object(job_b, 'create_child_job_from_record') as fn:
            fn.side_effect = lambda record: job_a
            # Pretend that we are observing a 'result_b' of 'job_b'
            self.ctrl.observe_result(session_state, job_b, result_b)
        # Ensure that result got stored
        self.assertIs(session_state.job_state_map[job_b.id].result, result_b)
        # Ensure that job A is now via-connected to job B
        self.assertIs(session_state.job_state_map[job_a.id].via_job, job_b)

    @mock.patch('plainbox.impl.ctrl.gen_rfc822_records_from_io_log')
    @mock.patch('plainbox.impl.ctrl.logger')
    def test_observe_result__local_imperfect_clash(
            self, mock_logger, mock_gen):
        """
        verify side effects of using observe_result() that would define a
        already existing job with the non-identical definition.

        We basically hope to see the old job being there intact and a warning
        to be logged.
        """
        # Jobs A1 and A2 are simple example jobs (different, with same id)
        job_a1 = JobDefinition(
            {'id': 'a', 'plugin': 'shell', 'command': 'true'})
        job_a2 = JobDefinition(
            {'id': 'a', 'plugin': 'shell', 'command': 'false'})
        # Job B is a job that prints the definition of job A2
        job_b = JobDefinition({'id': 'b', 'plugin': 'local'})
        # Result B is a fake result of running job B
        result_b = MemoryJobResult({'outcome': 'pass'})
        # Session knows about A1 and B
        session_state = SessionState([job_a1, job_b])
        # Mock gen_rfc822_records_from_io_log to produce one mock record
        mock_gen.return_value = [RFC822Record({})]
        # Mock job B to create job A2 as a child if asked to
        with mock.patch.object(job_b, 'create_child_job_from_record') as fn:
            fn.side_effect = lambda record: job_a2
            # Pretend that we are observing a 'result_b' of 'job_b'
            self.ctrl.observe_result(session_state, job_b, result_b)
        # Ensure that result got stored
        self.assertIs(session_state.job_state_map[job_b.id].result, result_b)
        # Ensure that we didn't change via_job of the job A1
        self.assertIsNot(session_state.job_state_map[job_a1.id].via_job, job_b)
        # Ensure that a warning was logged
        mock_logger.warning.assert_called_once_with(
            ("Local job %s produced job %s that collides with"
             " an existing job %s (from %s), the new job was"
             " discarded"),
            job_b.id, job_a2.id, job_a1.id, job_a1.origin)

    @mock.patch('plainbox.impl.ctrl.gen_rfc822_records_from_io_log')
    def test_observe_result__local_perfect_clash(self, mock_gen):
        """
        verify side effects of using observe_result() that would define a
        already existing job with the exactly identical definition.

        We basically hope to see the old job being there but the origin field
        should be updated to reflect the new association between 'existing_job'
        and 'job'
        """
        # Job A is any example job
        job_a = JobDefinition({'id': 'a', 'plugin': 'shell', 'command': ':'})
        # Job B is a job that prints the definition of job A
        job_b = JobDefinition({'id': 'b', 'plugin': 'local'})
        # Result B is a fake result of running job B
        result_b = MemoryJobResult({'outcome': 'pass'})
        # Session knows about A and B
        session_state = SessionState([job_a, job_b])
        # Mock gen_rfc822_records_from_io_log to produce one mock record
        mock_gen.return_value = [RFC822Record({})]
        # Mock job B to create job A as a child if asked to
        with mock.patch.object(job_b, 'create_child_job_from_record') as fn:
            fn.side_effect = lambda record: job_a
            # Pretend that we are observing a 'result_b' of 'job_b'
            self.ctrl.observe_result(session_state, job_b, result_b)
        # Ensure that result got stored
        self.assertIs(session_state.job_state_map[job_b.id].result, result_b)
        # Ensure that job A is now via-connected to job B
        self.assertIs(session_state.job_state_map[job_a.id].via_job, job_b)


class FunctionTests(TestCase):
    """
    unit tests for gen_rfc822_records_from_io_log() and other functions.
    """

    def test_parse_typical(self):
        """
        verify typical operation without any parsing errors
        """
        # Setup a mock job and result, give some io log to the result
        job = mock.Mock(spec=JobDefinition)
        result = mock.Mock(spec=IJobResult)
        result.get_io_log.return_value = [
            (0, 'stdout', b'attr: value1\n'),
            (0, 'stdout', b'\n'),
            (0, 'stdout', b'attr: value2\n')]
        # Parse the IO log records
        records = list(gen_rfc822_records_from_io_log(job, result))
        # Ensure that we saw both records
        self.assertEqual(records, [
            RFC822Record(
                {'attr': 'value1'}, Origin(JobOutputTextSource(job), 1, 1)),
            RFC822Record(
                {'attr': 'value2'}, Origin(JobOutputTextSource(job), 3, 3)),
        ])

    @mock.patch('plainbox.impl.ctrl.logger')
    def test_parse_error(self, mock_logger):
        # Setup a mock job and result, give some io log to the result
        job = mock.Mock(spec=JobDefinition)
        result = mock.Mock(spec=IJobResult)
        result.get_io_log.return_value = [
            (0, 'stdout', b'attr: value1\n'),
            (0, 'stdout', b'\n'),
            (0, 'stdout', b'error\n'),
            (0, 'stdout', b'\n'),
            (0, 'stdout', b'attr: value2\n')]
        # Parse the IO log records
        records = list(gen_rfc822_records_from_io_log(job, result))
        # Ensure that only the first record was generated
        self.assertEqual(records, [
            RFC822Record(
                {'attr': 'value1'}, Origin(JobOutputTextSource(job), 1, 1)),
        ])
        # Ensure that a warning was logged
        mock_logger.warning.assert_called_once_with(
            "local script %s returned invalid RFC822 data: %s",
            job.id, RFC822SyntaxError(
                None, 3, "Unexpected non-empty line: 'error\\n'"))

    def test_get_via_cycle__no_cycle(self):
        job_a = mock.Mock(spec_set=JobDefinition, name='job_a')
        job_a.id = 'a'
        job_state_a = mock.Mock(spec_set=JobState, name='job_state_a')
        job_state_a.job = job_a
        job_state_a.via_job = None
        job_state_map = {job_a.id: job_state_a}
        self.assertEqual(get_via_cycle(job_state_map, job_a), ())

    def test_get_via_cycle__trivial(self):
        job_a = mock.Mock(spec_set=JobDefinition, name='job_a')
        job_a.id = 'a'
        job_state_a = mock.Mock(spec_set=JobState, name='job_state_b')
        job_state_a.job = job_a
        job_state_a.via_job = job_a
        job_state_map = {job_a.id: job_state_a}
        self.assertEqual(get_via_cycle(job_state_map, job_a), [job_a, job_a])

    def test_get_via_cycle__indirect(self):
        job_a = mock.Mock(spec_set=JobDefinition, name='job_a')
        job_a.id = 'a'
        job_b = mock.Mock(spec_set=JobDefinition, name='job_b')
        job_b.id = 'b'
        job_state_a = mock.Mock(spec_set=JobState, name='job_state_a')
        job_state_a.job = job_a
        job_state_a.via_job = job_b
        job_state_b = mock.Mock(spec_set=JobState, name='job_state_b')
        job_state_b.job = job_b
        job_state_b.via_job = job_a
        job_state_map = {
            job_a.id: job_state_a,
            job_b.id: job_state_b,
        }
        self.assertEqual(
            get_via_cycle(job_state_map, job_a),
            [job_a, job_b, job_a])


class SymLinkNestTests(TestCase):
    """
    Tests for SymLinkNest class
    """

    NEST_DIR = "nest"

    def setUp(self):
        self.nest = SymLinkNest(self.NEST_DIR)

    def test_init(self):
        """
        verify that SymLinkNest.__init__() stores its argument
        """
        self.assertEqual(self.nest._dirname, self.NEST_DIR)

    def test_add_provider(self):
        """
        verify that add_provider() adds each executable
        """
        provider = mock.Mock(name='provider', spec=Provider1)
        provider.executable_list = ['exec1', 'exec2']
        with mock.patch.object(self.nest, 'add_executable'):
            self.nest.add_provider(provider)
            self.nest.add_executable.assert_has_calls([
                (('exec1',), {}),
                (('exec2',), {})])

    @mock.patch('os.symlink')
    def test_add_executable(self, mock_symlink):
        self.nest.add_executable('/usr/lib/foo/exec')
        mock_symlink.assert_called_with(
            '/usr/lib/foo/exec', 'nest/exec')


class CheckBoxExecutionControllerTestsMixIn:
    """
    Mix-in class that defines tests for CheckBoxExecutionController
    """

    SESSION_DIR = 'session-dir'
    PROVIDER_LIST = []  # we don't need any here
    NEST_DIR = 'nest-dir'  # used as fake data only

    CLS = CheckBoxExecutionController

    @mock.patch('plainbox.impl.ctrl.check_output')
    def setUp(self, mock_check_output):
        self.ctrl = self.CLS(self.PROVIDER_LIST)
        # Create mocked job definition.
        # Put a mocked provider on the job and give it some values for:
        # * extra_PYTHONPATH (optional, set it to None),
        # * CHECKBOX_SHARE (mandatory)
        self.job = mock.Mock(
            name='job',
            spec=JobDefinition,
            provider=mock.Mock(
                name='provider',
                spec=IProvider1,
                extra_PYTHONPATH=None,
                CHECKBOX_SHARE='CHECKBOX_SHARE',
                data_dir='data_dir', units_dir='units_dir'))
        self.job_state = mock.Mock(name='job_state', spec=JobState)
        # Mock the default flags (empty set)
        self.job.get_flag_set.return_value = frozenset()
        # Create mocked config.
        # Put an empty dictionary of environment overrides
        # that is expected by get_execution_environment()
        self.config = mock.Mock(
            name='config',
            spec=PlainBoxConfig,
            environment={})
        # Create a mocked extcmd_popen
        self.extcmd_popen = mock.Mock(
            name='extcmd_popen',
            spec=extcmd.ExternalCommand)

    @mock.patch('plainbox.impl.ctrl.check_output')
    def test_init(self, mock_check_output):
        """
        verify that __init__() stores session_dir
        """
        provider_list = mock.Mock()
        ctrl = self.CLS(provider_list)
        self.assertIs(ctrl._provider_list, provider_list)

    @mock.patch('os.path.isdir')
    @mock.patch('os.makedirs')
    def test_execute_job(self, mock_makedirs, mock_os_path_isdir):
        """
        verify that execute_job() correctly glues all the basic pieces
        """
        # Call the tested method, execute_job() but mock-away
        # methods that we're not testing here,
        # get_execution_{command,environment}() and configured_filesystem()
        with mock.patch.object(self.ctrl, 'get_execution_command'), \
                mock.patch.object(self.ctrl, 'get_execution_environment'), \
                mock.patch.object(self.ctrl, 'configured_filesystem'), \
                mock.patch.object(self.ctrl, 'temporary_cwd'):
            retval = self.ctrl.execute_job(
                self.job, self.job_state, self.config, self.SESSION_DIR,
                self.extcmd_popen)
            # Ensure that call was invoked with command end environment (passed
            # as keyword argument). Extract the return value of
            # configured_filesystem() as nest_dir so that we can pass it to
            # other calls to get their mocked return values.
            # Urgh! is this doable somehow without all that?
            nest_dir = self.ctrl.configured_filesystem().__enter__()
            cwd_dir = self.ctrl.temporary_cwd().__enter__()
            self.extcmd_popen.call.assert_called_with(
                self.ctrl.get_execution_command(
                    self.job, self.job_state, self.config, self.SESSION_DIR,
                    nest_dir),
                env=self.ctrl.get_execution_environment(
                    self.job, self.job_state, self.config, self.SESSION_DIR,
                    nest_dir),
                cwd=cwd_dir)
        # Ensure that execute_job() returns the return value of call()
        self.assertEqual(retval, self.extcmd_popen.call())
        # Ensure that presence of CHECKBOX_DATA directory was checked for
        mock_os_path_isdir.assert_called_with(
            self.ctrl.get_CHECKBOX_DATA(self.SESSION_DIR))

    def test_get_score_for_random_jobs(self):
        # Ensure that score for random jobs is -1
        self.assertEqual(self.ctrl.get_score(mock.Mock()), -1)

    def test_get_score_for_checkbox_jobs(self):
        # Ensure that mock for JobDefinition (which is checkbox job in
        # disguise) is whatever get_checkbox_score() returns.
        with mock.patch.object(
                self.ctrl, 'get_checkbox_score') as mock_get_checkbox_score:
            self.assertEqual(
                self.ctrl.get_score(mock.Mock(spec=JobDefinition)),
                mock_get_checkbox_score())

    def test_CHECKBOX_DATA(self):
        """
        verify the value of CHECKBOX_DATA
        """
        self.assertEqual(
            self.ctrl.get_CHECKBOX_DATA(self.SESSION_DIR),
            "session-dir/CHECKBOX_DATA")

    @mock.patch('json.dumps')
    @mock.patch('json.loads')
    @mock.patch('os.fdopen')
    def test_noreturn_flag_hangs(self, mock_os_fdopen, mock_json_loads,
                                 mock_json_dumps):
        """
        verify that jobs having 'noreturn' flag call _halt after executing
        command
        """
        self.job.get_flag_set.return_value = {'noreturn'}
        with mock.patch.object(self.ctrl, 'get_execution_command'), \
                mock.patch.object(self.ctrl, 'get_execution_environment'), \
                mock.patch.object(self.ctrl, 'configured_filesystem'), \
                mock.patch.object(self.ctrl, 'temporary_cwd'), \
                mock.patch.object(self.ctrl, '_halt'):
            self.ctrl.execute_job(
                self.job, self.job_state, self.config, self.SESSION_DIR,
                self.extcmd_popen)
            self.ctrl._halt.assert_called_once_with()


class UserJobExecutionControllerTests(CheckBoxExecutionControllerTestsMixIn,
                                      TestCase):
    """
    Tests for UserJobExecutionController
    """

    CLS = UserJobExecutionController

    def test_get_command(self):
        """
        verify that we simply execute the command via job.shell
        """
        self.assertEqual(
            self.ctrl.get_execution_command(
                self.job, self.job_state, self.config, self.SESSION_DIR,
                self.NEST_DIR),
            [self.job.shell, '-c', self.job.command])

    def test_get_checkbox_score_for_jobs_without_user(self):
        """
        verify that score for jobs without user override is one
        """
        self.job.user = None
        self.assertEqual(self.ctrl.get_checkbox_score(self.job), 1)

    @mock.patch('sys.platform')
    @mock.patch('os.getuid')
    def test_get_checkbox_score_for_jobs_with_user(
            self, mock_getuid, mock_plat):
        """
        verify that score for jobs with an user override is minus one
        """
        mock_plat.return_value = 'linux'
        # Ensure we're not root, in case test suite *is* run by root.
        mock_getuid.return_value = 1000
        self.job.user = 'root'
        self.assertEqual(self.ctrl.get_checkbox_score(self.job), -1)

    @mock.patch('sys.platform')
    @mock.patch('os.getuid')
    def test_get_checkbox_score_as_root(self, mock_getuid, mock_plat):
        """
        verify that score for jobs with an user override is 4 if I am root
        """
        mock_plat.return_value = 'linux'
        mock_getuid.return_value = 0  # Pretend to be root
        self.job.user = 'root'
        self.assertEqual(self.ctrl.get_checkbox_score(self.job), 4)

    @mock.patch.dict('os.environ', clear=True)
    def test_get_execution_environment_resets_locales(self):
        # Call the tested method
        env = self.ctrl.get_execution_environment(
            self.job, self.job_state, self.config, self.SESSION_DIR,
            self.NEST_DIR)
        # Ensure that LANG is reset to C.UTF-8
        self.assertEqual(env['LANG'], 'C.UTF-8')

    @mock.patch.dict('os.environ', clear=True, LANG='fake_LANG',
                     LANGUAGE='fake_LANGUAGE', LC_ALL='fake_LC_ALL')
    def test_get_execution_environment_preserves_locales_if_requested(self):
        self.job.get_flag_set.return_value = {'preserve-locale'}
        # Call the tested method
        env = self.ctrl.get_execution_environment(
            self.job, self.job_state, self.config, self.SESSION_DIR,
            self.NEST_DIR)
        # Ensure that locale variables are what we mocked them to be
        self.assertEqual(env['LANG'], 'fake_LANG')
        self.assertEqual(env['LANGUAGE'], 'fake_LANGUAGE')
        self.assertEqual(env['LC_ALL'], 'fake_LC_ALL')

    @mock.patch.dict('os.environ', clear=True, PYTHONPATH='PYTHONPATH')
    def test_get_execution_environment_keeps_PYTHONPATH(self):
        # Call the tested method
        env = self.ctrl.get_execution_environment(
            self.job, self.job_state, self.config, self.SESSION_DIR,
            self.NEST_DIR)
        # Ensure that extra_PYTHONPATH is preprended to PYTHONPATH
        self.assertEqual(env['PYTHONPATH'], 'PYTHONPATH')

    @mock.patch.dict('os.environ', clear=True)
    def test_get_execution_environment_uses_extra_PYTHONPATH(self):
        # Set a extra_PYTHONPATH on the provider object
        self.job.provider.extra_PYTHONPATH = 'extra_PYTHONPATH'
        # Call the tested method
        env = self.ctrl.get_execution_environment(
            self.job, self.job_state, self.config, self.SESSION_DIR,
            self.NEST_DIR)
        # Ensure that extra_PYTHONPATH is preprended to PYTHONPATH
        self.assertTrue(env['PYTHONPATH'].startswith(
            self.job.provider.extra_PYTHONPATH))

    @mock.patch.dict('os.environ', clear=True, PYTHONPATH='PYTHONPATH')
    def test_get_execution_environment_merges_PYTHONPATH(self):
        # Set a extra_PYTHONPATH on the provider object
        self.job.provider.extra_PYTHONPATH = 'extra_PYTHONPATH'
        # Call the tested method
        env = self.ctrl.get_execution_environment(
            self.job, self.job_state, self.config, self.SESSION_DIR,
            self.NEST_DIR)
        # Ensure that extra_PYTHONPATH is preprended to PYTHONPATH
        self.assertTrue(env['PYTHONPATH'].startswith(
            self.job.provider.extra_PYTHONPATH))
        self.assertTrue(env['PYTHONPATH'].endswith('PYTHONPATH'))

    @mock.patch.dict('os.environ', clear=True)
    def test_get_execution_environment_sets_CHECKBOX_SHARE(self):
        # Call the tested method
        env = self.ctrl.get_execution_environment(
            self.job, self.job_state, self.config, self.SESSION_DIR,
            self.NEST_DIR)
        # Ensure that CHECKBOX_SHARE is set to what the job provider wants
        self.assertEqual(
            env['CHECKBOX_SHARE'], self.job.provider.CHECKBOX_SHARE)

    @mock.patch.dict('os.environ', clear=True)
    def test_get_execution_environment_sets_CHECKBOX_DATA(self):
        # Call the tested method
        env = self.ctrl.get_execution_environment(
            self.job, self.job_state, self.config, self.SESSION_DIR,
            self.NEST_DIR)
        # Ensure that CHECKBOX_DATA is set to what the controller wants
        self.assertEqual(
            env['CHECKBOX_DATA'],
            self.ctrl.get_CHECKBOX_DATA(self.SESSION_DIR))

    @mock.patch.dict('os.environ', clear=True)
    def test_get_execution_environment_respects_config_environment(self):
        self.config.environment['key'] = 'value'
        # Call the tested method
        env = self.ctrl.get_execution_environment(
            self.job, self.job_state, self.config, self.SESSION_DIR,
            self.NEST_DIR)
        # Ensure that key=value was passed to the environment
        self.assertEqual(env['key'], 'value')

    @mock.patch.dict('os.environ', clear=True, key='old-value')
    def test_get_execution_environment_preferes_existing_environment(self):
        self.config.environment['key'] = 'value'
        # Call the tested method
        env = self.ctrl.get_execution_environment(
            self.job, self.job_state, self.config, self.SESSION_DIR,
            self.NEST_DIR)
        # Ensure that 'old-value' takes priority over 'value'
        self.assertEqual(env['key'], 'old-value')


class RootViaPTL1ExecutionControllerTests(
        CheckBoxExecutionControllerTestsMixIn, TestCase):
    """
    Tests for RootViaPTL1ExecutionController
    """

    CLS = RootViaPTL1ExecutionController

    def test_get_execution_environment_is_None(self):
        # Call the tested method
        env = self.ctrl.get_execution_environment(
            self.job, self.job_state, self.config, self.SESSION_DIR,
            self.NEST_DIR)
        # Ensure that the environment is None
        self.assertEqual(env, None)

    @mock.patch.dict('os.environ', clear=True, PATH='vanilla-path')
    def test_get_command(self):
        """
        verify that we run plainbox-trusted-launcher-1 as the desired user
        """
        self.job.get_environ_settings.return_value = []
        self.job_state.via_job = mock.Mock(
            name='generator_job',
            spec=JobDefinition,
            provider=mock.Mock(
                name='provider',
                spec=IProviderBackend1,
                extra_PYTHONPATH=None,
                data_dir="data_dir-generator",
                units_dir="units_dir-generator",
                CHECKBOX_SHARE='CHECKBOX_SHARE-generator'))
        # Mock the default flags (empty set)
        self.job_state.via_job.get_flag_set.return_value = frozenset()
        PATH = os.pathsep.join([self.NEST_DIR, 'vanilla-path'])
        expected = [
            'pkexec', '--user', self.job.user,
            'plainbox-trusted-launcher-1',
            '--generator', self.job_state.via_job.checksum,
            '-G', 'CHECKBOX_DATA=session-dir/CHECKBOX_DATA',
            '-G', 'CHECKBOX_SHARE=CHECKBOX_SHARE-generator',
            '-G', 'LANG=C.UTF-8',
            '-G', 'LANGUAGE=',
            '-G', 'LC_ALL=C.UTF-8',
            '-G', 'PATH={}'.format(PATH),
            '-G', 'PLAINBOX_PROVIDER_DATA=data_dir-generator',
            '-G', 'PLAINBOX_PROVIDER_UNITS=units_dir-generator',
            '-G', 'PLAINBOX_SESSION_SHARE=session-dir/CHECKBOX_DATA',
            '--target', self.job.checksum,
            '-T', 'CHECKBOX_DATA=session-dir/CHECKBOX_DATA',
            '-T', 'CHECKBOX_SHARE=CHECKBOX_SHARE',
            '-T', 'LANG=C.UTF-8',
            '-T', 'LANGUAGE=',
            '-T', 'LC_ALL=C.UTF-8',
            '-T', 'PATH={}'.format(PATH),
            '-T', 'PLAINBOX_PROVIDER_DATA=data_dir',
            '-T', 'PLAINBOX_PROVIDER_UNITS=units_dir',
            '-T', 'PLAINBOX_SESSION_SHARE=session-dir/CHECKBOX_DATA',
        ]
        actual = self.ctrl.get_execution_command(
            self.job, self.job_state, self.config, self.SESSION_DIR,
            self.NEST_DIR)
        self.assertEqual(actual, expected)

    @mock.patch.dict('os.environ', clear=True, PATH='vanilla-path')
    def test_get_command_without_via(self):
        """
        verify that we run plainbox-trusted-launcher-1 as the desired user
        """
        self.job.get_environ_settings.return_value = []
        self.job_state.via_job = None
        PATH = os.pathsep.join([self.NEST_DIR, 'vanilla-path'])
        expected = [
            'pkexec', '--user', self.job.user,
            'plainbox-trusted-launcher-1',
            '--target', self.job.checksum,
            '-T', 'CHECKBOX_DATA=session-dir/CHECKBOX_DATA',
            '-T', 'CHECKBOX_SHARE=CHECKBOX_SHARE',
            '-T', 'LANG=C.UTF-8',
            '-T', 'LANGUAGE=',
            '-T', 'LC_ALL=C.UTF-8',
            '-T', 'PATH={}'.format(PATH),
            '-T', 'PLAINBOX_PROVIDER_DATA=data_dir',
            '-T', 'PLAINBOX_PROVIDER_UNITS=units_dir',
            '-T', 'PLAINBOX_SESSION_SHARE=session-dir/CHECKBOX_DATA',
        ]
        actual = self.ctrl.get_execution_command(
            self.job, self.job_state, self.config, self.SESSION_DIR,
            self.NEST_DIR)
        self.assertEqual(actual, expected)

    def test_get_checkbox_score_for_other_providers(self):
        # Ensure that the job provider is not Provider1
        self.assertNotIsInstance(self.job.provider, Provider1)
        # Ensure that we get a negative score of minus one
        self.assertEqual(self.ctrl.get_checkbox_score(self.job), -1)

    def test_get_checkbox_score_for_insecure_provider1(self):
        # Assume that the job is coming from Provider1 provider
        # but the provider itself is insecure
        self.job.provider = mock.Mock(spec=Provider1, secure=False)
        # Ensure that we get a negative score of minus one
        self.assertEqual(self.ctrl.get_checkbox_score(self.job), -1)

    @mock.patch.dict('plainbox.impl.ctrl.os.environ', clear=True)
    def test_get_checkbox_score_for_secure_provider_and_user_job(self):
        # Assume that the job is coming from Provider1 provider
        # and the provider is secure
        self.job.provider = mock.Mock(spec=Provider1, secure=True)
        # Assume that the job runs as the current user
        self.job.user = None
        # Ensure that we get a neutral score of zero
        self.assertEqual(self.ctrl.get_checkbox_score(self.job), 0)

    @mock.patch.dict('plainbox.impl.ctrl.os.environ', clear=True)
    @mock.patch('plainbox.impl.ctrl.check_output')
    def test_get_checkbox_score_for_secure_provider_root_job_with_policy(
            self, mock_check_output):
        # Assume that the job is coming from Provider1 provider
        # and the provider is secure
        self.job.provider = mock.Mock(spec=Provider1, secure=True)
        # Assume that the job runs as root
        self.job.user = 'root'
        # Ensure we get the right action id from pkaction(1)
        mock_check_output.return_value = \
            b"org.freedesktop.policykit.pkexec.run-plainbox-job\n"
        # Ensure that we get a positive score of three
        ctrl = self.CLS(self.PROVIDER_LIST)
        self.assertEqual(ctrl.get_checkbox_score(self.job), 3)

    @mock.patch.dict('plainbox.impl.ctrl.os.environ', clear=True)
    @mock.patch('plainbox.impl.ctrl.check_output')
    def test_get_checkbox_score_for_secure_provider_root_job_with_policy_2(
            self, mock_check_output):
        # Assume that the job is coming from Provider1 provider
        # and the provider is secure
        self.job.provider = mock.Mock(spec=Provider1, secure=True)
        # Assume that the job runs as root
        self.job.user = 'root'
        # Ensure we get the right action id from pkaction(1) even with
        # polikt version < 0.110 (pkaction always exists with status 1), see:
        # https://bugs.freedesktop.org/show_bug.cgi?id=29936#attach_78263
        mock_check_output.side_effect = CalledProcessError(
            1, '', b"org.freedesktop.policykit.pkexec.run-plainbox-job\n")
        # Ensure that we get a positive score of three
        ctrl = self.CLS(self.PROVIDER_LIST)
        self.assertEqual(ctrl.get_checkbox_score(self.job), 3)

    @mock.patch.dict('plainbox.impl.ctrl.os.environ', values={
        'SSH_CONNECTION': '1.2.3.4 123 1.2.3.5 22'
    })
    @mock.patch('plainbox.impl.ctrl.check_output')
    def test_get_checkbox_score_for_normally_supported_job_over_ssh(
            self, mock_check_output):
        # Assume that the job is coming from Provider1 provider
        # and the provider is secure
        self.job.provider = mock.Mock(spec=Provider1, secure=True)
        # Assume that the job runs as root
        self.job.user = 'root'
        # Assume we get the right action id from pkaction(1) even with
        # polikt version < 0.110 (pkaction always exists with status 1), see:
        # https://bugs.freedesktop.org/show_bug.cgi?id=29936#attach_78263
        mock_check_output.side_effect = CalledProcessError(
            1, '', b"org.freedesktop.policykit.pkexec.run-plainbox-job\n")
        # Ensure that we get a positive score of three
        ctrl = self.CLS(self.PROVIDER_LIST)
        self.assertEqual(ctrl.get_checkbox_score(self.job), -1)

    @mock.patch.dict('plainbox.impl.ctrl.os.environ', clear=True)
    @mock.patch('plainbox.impl.ctrl.check_output')
    def test_get_checkbox_score_for_secure_provider_root_job_no_policy(
            self, mock_check_output):
        # Assume that the job is coming from Provider1 provider
        # and the provider is secure
        self.job.provider = mock.Mock(spec=Provider1, secure=True)
        # Assume that the job runs as root
        self.job.user = 'root'
        # Ensure pkaction(1) return nothing
        mock_check_output.return_value = "No action with action id BLAHBLAH"
        # Ensure that we get a positive score of two
        ctrl = self.CLS(self.PROVIDER_LIST)
        self.assertEqual(ctrl.get_checkbox_score(self.job), 0)


class RootViaPkexecExecutionControllerTests(
        CheckBoxExecutionControllerTestsMixIn, TestCase):
    """
    Tests for RootViaPkexecExecutionController
    """

    CLS = RootViaPkexecExecutionController

    def test_get_execution_environment_is_None(self):
        # Call the tested method
        env = self.ctrl.get_execution_environment(
            self.job, self.job_state, self.config, self.SESSION_DIR,
            self.NEST_DIR)
        # Ensure that the environment is None
        self.assertEqual(env, None)

    @mock.patch.dict('os.environ', clear=True, PATH='vanilla-path')
    def test_get_command(self):
        """
        verify that we run env(1) + job.shell as the target user
        """
        self.job.get_environ_settings.return_value = []
        self.assertEqual(
            self.ctrl.get_execution_command(
                self.job, self.job_state, self.config, self.SESSION_DIR,
                self.NEST_DIR),
            ['pkexec', '--user', self.job.user,
             'env',
             'CHECKBOX_DATA=session-dir/CHECKBOX_DATA',
             'CHECKBOX_SHARE=CHECKBOX_SHARE',
             'LANG=C.UTF-8',
             'LANGUAGE=',
             'LC_ALL=C.UTF-8',
             'PATH={}'.format(
                 os.pathsep.join([self.NEST_DIR, 'vanilla-path'])),
             'PLAINBOX_PROVIDER_DATA=data_dir',
             'PLAINBOX_PROVIDER_UNITS=units_dir',
             'PLAINBOX_SESSION_SHARE=session-dir/CHECKBOX_DATA',
             self.job.shell, '-c', self.job.command])

    def test_get_checkbox_score_for_user_jobs(self):
        # Assume that the job runs as the current user
        self.job.user = None
        # Ensure that we get a neutral score of zero
        self.assertEqual(self.ctrl.get_checkbox_score(self.job), 0)

    def test_get_checkbox_score_for_root_jobs(self):
        # Assume that the job runs as the root user
        self.job.user = 'root'
        # Ensure that we get a positive score of one
        self.assertEqual(self.ctrl.get_checkbox_score(self.job), 1)


class RootViaSudoExecutionControllerTests(
        CheckBoxExecutionControllerTestsMixIn, TestCase):
    """
    Tests for RootViaSudoExecutionController
    """

    CLS = RootViaSudoExecutionController

    @mock.patch.dict('os.environ', clear=True, PATH='vanilla-path')
    def test_get_command(self):
        """
        verify that we run sudo(8)
        """
        self.job.get_environ_settings.return_value = []
        self.assertEqual(
            self.ctrl.get_execution_command(
                self.job, self.job_state, self.config, self.SESSION_DIR,
                self.NEST_DIR),
            ['sudo', '-u', self.job.user, 'env',
             'CHECKBOX_DATA=session-dir/CHECKBOX_DATA',
             'CHECKBOX_SHARE=CHECKBOX_SHARE',
             'LANG=C.UTF-8',
             'LANGUAGE=',
             'LC_ALL=C.UTF-8',
             'PATH={}'.format(
                 os.pathsep.join([self.NEST_DIR, 'vanilla-path'])),
             'PLAINBOX_PROVIDER_DATA=data_dir',
             'PLAINBOX_PROVIDER_UNITS=units_dir',
             'PLAINBOX_SESSION_SHARE=session-dir/CHECKBOX_DATA',
             self.job.shell, '-c', self.job.command])

    SUDO, ADMIN = range(2)

    # Mock gid's for 'sudo' and 'admin'
    def fake_getgrnam(self, name):
        if name == 'sudo':
            return mock.Mock(gr_gid=self.SUDO)
        elif name == 'admin':
            return mock.Mock(gr_gid=self.ADMIN)
        else:
            raise ValueError("unexpected group name")

    @mock.patch('grp.getgrnam')
    @mock.patch('posix.getgroups')
    def test_user_can_sudo__sudo_group(self, mock_getgroups, mock_getgrnam):
        # Mock gid's for 'sudo' and 'admin'
        mock_getgrnam.side_effect = self.fake_getgrnam
        # Mock that the current user is a member of group 1 ('sudo')
        mock_getgroups.return_value = [self.SUDO]
        # Create a fresh execution controller
        ctrl = self.CLS(self.PROVIDER_LIST)
        # Ensure that the user can use sudo
        self.assertTrue(ctrl.user_can_sudo)

    @mock.patch('grp.getgrnam')
    @mock.patch('posix.getgroups')
    def test_user_can_sudo__admin_group(self, mock_getgroups, mock_getgrnam):
        sudo, admin = range(2)
        # Mock gid's for 'sudo' and 'admin'
        mock_getgrnam.side_effect = self.fake_getgrnam
        # Mock that the current user is a member of group 1 ('admin')
        mock_getgroups.return_value = [self.ADMIN]
        # Create a fresh execution controller
        ctrl = self.CLS(self.PROVIDER_LIST)
        # Ensure that the user can use sudo
        self.assertTrue(ctrl.user_can_sudo)

    @mock.patch('grp.getgrnam')
    @mock.patch('posix.getgroups')
    def test_user_can_sudo__no_groups(self, mock_getgroups, mock_getgrnam):
        sudo, admin = range(2)
        # Mock gid's for 'sudo' and 'admin'
        mock_getgrnam.side_effect = self.fake_getgrnam
        # Mock that the current user not a member of any group
        mock_getgroups.return_value = []
        # Create a fresh execution controller
        ctrl = self.CLS(self.PROVIDER_LIST)
        # Ensure that the user can use sudo
        self.assertFalse(ctrl.user_can_sudo)

    def test_get_checkbox_score_without_sudo(self):
        # Assume that the user cannot use sudo
        self.ctrl.user_can_sudo = False
        # Ensure that we get a negative score for this controller
        self.assertEqual(self.ctrl.get_checkbox_score(self.job), -1)

    def test_get_checkbox_score_with_sudo(self):
        # Assume that the user can use sudo
        self.ctrl.user_can_sudo = True
        # Ensure that we get a positive score for this controller
        # The score is actually 2 to be better than the pkexec controller
        self.assertEqual(self.ctrl.get_checkbox_score(self.job), 2)

    def test_get_checkbox_score_for_non_root_jobs(self):
        # Assume that the user can use sudo
        self.ctrl.user_can_sudo = True
        # But don't require root for the jobs itself
        self.job.user = None
        # Ensure that we get a negative score for this controller
        self.assertEqual(self.ctrl.get_checkbox_score(self.job), -1)


class QmlJobExecutionControllerTests(CheckBoxExecutionControllerTestsMixIn,
                                     TestCase):
    """
    Tests for QmlJobExecutionController
    """
    CLS = QmlJobExecutionController

    SHELL_OUT_FD = 6
    SHELL_IN_FD = 7

    def test_job_repr(self):
        self.assertEqual(
            self.ctrl.gen_job_repr(self.job),
            {'id': self.job.id,
             'summary': self.job.tr_summary(),
             'description': self.job.tr_description()})

    def test_get_execution_command(self):
        """
        Tests gluing of commandline arguments when running QML exec. ctrl.
        """
        self.assertEqual(
            self.ctrl.get_execution_command(
                self.job, self.job_state, self.config, self.SESSION_DIR,
                self.NEST_DIR, self.SHELL_OUT_FD, self.SHELL_IN_FD),
            ['qmlscene', '-I', self.ctrl.QML_MODULES_PATH, '--job',
             self.job.qml_file, '--fd-out', self.SHELL_OUT_FD, '--fd-in',
             self.SHELL_IN_FD, self.ctrl.QML_SHELL_PATH])

    @mock.patch('json.dumps')
    @mock.patch('os.path.isdir')
    @mock.patch('os.fdopen')
    @mock.patch('os.pipe')
    @mock.patch('os.write')
    @mock.patch('os.close')
    def test_execute_job(self, mock_os_close, mock_os_write, mock_os_pipe,
                         mock_os_fdopen, mock_os_path_isdir, mock_json_dumps):
        """
        Test if qml exec. ctrl. correctly runs piping
        """
        mock_os_pipe.side_effect = [("pipe0_r", "pipe0_w"),
                                    ("pipe1_r", "pipe1_w")]
        with mock.patch.object(self.ctrl, 'get_execution_command'), \
                mock.patch.object(self.ctrl, 'get_execution_environment'), \
                mock.patch.object(self.ctrl, 'configured_filesystem'), \
                mock.patch.object(self.ctrl, 'temporary_cwd'), \
                mock.patch.object(self.ctrl, 'gen_job_repr', return_value={}):
            retval = self.ctrl.execute_job(
                self.job, self.job_state, self.config, self.SESSION_DIR,
                self.extcmd_popen)
            # Ensure that call was invoked with command end environment (passed
            # as keyword argument). Extract the return value of
            # configured_filesystem() as nest_dir so that we can pass it to
            # other calls to get their mocked return values.
            # Urgh! is this doable somehow without all that?
            nest_dir = self.ctrl.configured_filesystem().__enter__()
            cwd_dir = self.ctrl.temporary_cwd().__enter__()
            self.extcmd_popen.call.assert_called_with(
                self.ctrl.get_execution_command(
                    self.job, self.config, self.SESSION_DIR, nest_dir),
                env=self.ctrl.get_execution_environment(
                    self.job, self.config, self.SESSION_DIR, nest_dir),
                cwd=cwd_dir,
                pass_fds=["pipe0_w", "pipe1_r"])
        # Ensure that execute_job() returns the return value of call()
        self.assertEqual(retval, self.extcmd_popen.call())
        # Ensure that presence of CHECKBOX_DATA directory was checked for
        mock_os_path_isdir.assert_called_with(
            self.ctrl.get_CHECKBOX_DATA(self.SESSION_DIR))
        self.assertEqual(mock_os_pipe.call_count, 2)
        self.assertEqual(mock_os_fdopen.call_count, 2)
        self.assertEqual(mock_os_close.call_count, 6)
        # Ensure that testing_shell_data is properly created
        mock_json_dumps.assert_called_once_with({
            "job_repr": {},
            "session_dir": self.ctrl.get_CHECKBOX_DATA(self.SESSION_DIR)
        })
        mock_os_fdopen().write.assert_called_with(mock_json_dumps())

    @mock.patch('os.path.isdir')
    @mock.patch('os.fdopen')
    @mock.patch('os.pipe')
    @mock.patch('os.write')
    @mock.patch('os.close')
    def test_pipes_closed_when_cmd_raises(
            self, mock_os_close, mock_os_write, mock_os_pipe, mock_os_fdopen,
            mock_os_path_isdir):
        """
        Test if all pipes used by execute_job() are properly closed if
        exception is raised during execution of command
        """
        mock_os_pipe.side_effect = [("pipe0_r", "pipe0_w"),
                                    ("pipe1_r", "pipe1_w")]
        with mock.patch.object(self.ctrl, 'get_execution_command'), \
                mock.patch.object(self.ctrl, 'get_execution_environment'), \
                mock.patch.object(self.ctrl, 'configured_filesystem'), \
                mock.patch.object(self.ctrl, 'temporary_cwd'), \
                mock.patch.object(self.ctrl, 'gen_job_repr', return_value={}), \
                mock.patch.object(self.extcmd_popen, 'call',
                                  side_effect=Exception('Boom')):
            with self.assertRaises(Exception):
                self.ctrl.execute_job(
                    self.job, self.job_state, self.config, self.SESSION_DIR,
                    self.extcmd_popen)
        os.close.assert_any_call('pipe0_r')
        os.close.assert_any_call('pipe1_r')
        os.close.assert_any_call('pipe0_w')
        os.close.assert_any_call('pipe1_w')

    def test_get_checkbox_score_for_qml_job(self):
        self.job.plugin = 'qml'
        self.assertEqual(self.ctrl.get_checkbox_score(self.job), 4)
