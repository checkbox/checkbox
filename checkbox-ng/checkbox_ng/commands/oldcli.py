from gettext import gettext as _
from logging import getLogger
from os.path import join
from shutil import copyfileobj
import io
import os
import sys

from plainbox.abc import IJobResult
from plainbox.impl.applogic import get_whitelist_by_name
from plainbox.impl.commands.inv_checkbox import CheckBoxInvocationMixIn
from plainbox.impl.depmgr import DependencyDuplicateError
from plainbox.impl.exporter import ByteStringStreamTranslator
from plainbox.impl.exporter import get_all_exporters
from plainbox.impl.exporter.html import HTMLSessionStateExporter
from plainbox.impl.exporter.xml import XMLSessionStateExporter
from plainbox.impl.result import DiskJobResult, MemoryJobResult
from plainbox.impl.runner import JobRunner
from plainbox.impl.runner import slugify
from plainbox.impl.secure.config import Unset
from plainbox.impl.secure.origin import Origin
from plainbox.impl.secure.qualifiers import CompositeQualifier
from plainbox.impl.secure.qualifiers import NonLocalJobQualifier
from plainbox.impl.secure.qualifiers import WhiteList
from plainbox.impl.secure.qualifiers import select_jobs
from plainbox.impl.session import SessionManager
from plainbox.impl.session import SessionStorageRepository
from plainbox.vendor.textland import get_display

from checkbox_ng.ui import ScrollableTreeNode
from checkbox_ng.ui import ShowMenu
from checkbox_ng.ui import ShowWelcome
from checkbox_ng.misc import SelectableJobTreeNode


logger = getLogger("checkbox.ng.commands.oldcli")


class CliInvocation(CheckBoxInvocationMixIn):

    def __init__(self, provider_loader, config, settings, ns, display=None):
        super().__init__(provider_loader, config)
        self.settings = settings
        self.display = display
        self.ns = ns
        self.whitelists = []
        self._local_only = False  # Only run local jobs
        if self.ns.whitelist:
            for whitelist in self.ns.whitelist:
                self.whitelists.append(WhiteList.from_file(whitelist.name))
        elif self.config.whitelist is not Unset:
            self.whitelists.append(WhiteList.from_file(self.config.whitelist))
        elif self.ns.include_pattern_list:
            self.whitelists.append(WhiteList(self.ns.include_pattern_list))

    @property
    def is_interactive(self):
        """
        Flag indicating that this is an interactive invocation and we can
        interact with the user when we encounter OUTCOME_UNDECIDED
        """
        return (sys.stdin.isatty() and sys.stdout.isatty() and not
                self.ns.non_interactive)

    def run(self):
        ns = self.ns
        job_list = self.get_job_list(ns)
        previous_session_file = SessionStorageRepository().get_last_storage()
        resume_in_progress = False
        if previous_session_file:
            if self.is_interactive:
                if self.ask_for_resume():
                    resume_in_progress = True
                    manager = SessionManager.load_session(
                        job_list, previous_session_file)
                    self._maybe_skip_last_job_after_resume(manager)
            else:
                resume_in_progress = True
                manager = SessionManager.load_session(
                    job_list, previous_session_file)
        if not resume_in_progress:
            # Create a session that handles most of the stuff needed to run
            # jobs
            try:
                manager = SessionManager.create_with_unit_list(job_list)
            except DependencyDuplicateError as exc:
                # Handle possible DependencyDuplicateError that can happen if
                # someone is using plainbox for job development.
                print(_("The job database you are currently using is broken"))
                print(_("At least two jobs contend for the name {0}").format(
                    exc.job.id))
                print(_("First job defined in: {0}").format(exc.job.origin))
                print(_("Second job defined in: {0}").format(
                    exc.duplicate_job.origin))
                raise SystemExit(exc)
            manager.state.metadata.title = " ".join(sys.argv)
            if self.is_interactive:
                if self.display is None:
                    self.display = get_display()
                # FIXME: i18n problem, welcome text must be translatable but
                # comes from external source. It should be made a part of the
                # program.
                if self.settings['welcome_text']:
                    self.display.run(
                        ShowWelcome(self.settings['welcome_text']))
                if not self.whitelists:
                    whitelists = []
                    for p in self.provider_list:
                        if p.name in self.settings['default_providers']:
                            whitelists.extend(
                                [w.name for w in p.get_builtin_whitelists()])
                    selection = self.display.run(ShowMenu("Suite selection",
                                                          whitelists))
                    if not selection:
                        raise SystemExit(
                            _('No whitelists selected, aborting...'))
                    for s in selection:
                        self.whitelists.append(
                            get_whitelist_by_name(self.provider_list,
                                                  whitelists[s]))
            else:
                self.whitelists.append(
                    get_whitelist_by_name(
                        self.provider_list,
                        self.settings['default_whitelist']))
        manager.checkpoint()
        runner = JobRunner(
            manager.storage.location, self.provider_list,
            os.path.join(manager.storage.location, 'io-logs'),
            command_io_delegate=self)
        if self.is_interactive and not resume_in_progress:
            # Pre-run all local jobs
            desired_job_list = select_jobs(
                manager.state.job_list,
                [CompositeQualifier(
                    self.whitelists +
                    [NonLocalJobQualifier(
                        Origin.get_caller_origin(), inclusive=False)]
                )])
            self._update_desired_job_list(manager, desired_job_list)
            # Ask the password before anything else in order to run local jobs
            # requiring privileges
            warm_up_list = runner.get_warm_up_sequence(manager.state.run_list)
            if warm_up_list:
                print("[ {} ]".format(_("Authentication")).center(80, '='))
                for warm_up_func in warm_up_list:
                    warm_up_func()
            self._local_only = True
            self._run_jobs(runner, ns, manager)
            self._local_only = False

        if not resume_in_progress:
            # Run the rest of the desired jobs
            desired_job_list = select_jobs(manager.state.job_list,
                                           self.whitelists)
            self._update_desired_job_list(manager, desired_job_list)
            if self.is_interactive:
                # Ask the password before anything else in order to run jobs
                # requiring privileges
                warm_up_list = runner.get_warm_up_sequence(
                    manager.state.run_list)
                if warm_up_list:
                    print("[ {} ]".format(_("Authentication")).center(80, '='))
                    for warm_up_func in warm_up_list:
                        warm_up_func()
                tree = SelectableJobTreeNode.create_tree(
                    manager.state, manager.state.run_list)
                title = _('Choose tests to run on your system:')
                if self.display is None:
                    self.display = get_display()
                self.display.run(ScrollableTreeNode(tree, title))
                # NOTE: tree.selection is correct but ordered badly.  To retain
                # the original ordering we should just treat it as a mask and
                # use it to filter jobs from desired_job_list.
                wanted_set = frozenset(tree.selection)
                self._update_desired_job_list(
                    manager, [job for job in manager.state.run_list
                              if job in wanted_set])
                estimated_duration_auto, estimated_duration_manual = \
                    manager.state.get_estimated_duration()
                if estimated_duration_auto:
                    print(_("Estimated duration is {:.2f} for automated"
                            " jobs.").format(estimated_duration_auto))
                else:
                    print(_("Estimated duration cannot be determined for"
                            " automated jobs."))
                if estimated_duration_manual:
                    print(_("Estimated duration is {:.2f} for manual"
                            " jobs.").format(estimated_duration_manual))
                else:
                    print(_("Estimated duration cannot be determined for"
                            " manual jobs."))
        self._run_jobs(runner, ns, manager)
        manager.destroy()

        # FIXME: sensible return value
        return 0

    def ask_for_resume(self):
        return self.ask_user(
            _("Do you want to resume the previous session?"), (_('y'), _('n'))
        ).lower() == "y"

    def ask_for_resume_action(self):
        return self.ask_user(
            _("What do you want to do with that job?"),
            (_('skip'), _('fail'), _('run')))

    def ask_user(self, prompt, allowed):
        answer = None
        while answer not in allowed:
            answer = input("{} [{}] ".format(prompt, ", ".join(allowed)))
        return answer

    def _maybe_skip_last_job_after_resume(self, manager):
        last_job = manager.state.metadata.running_job_name
        if last_job is None:
            return
        print(_("We have previously tried to execute {}").format(last_job))
        action = self.ask_for_resume_action()
        if action == _('skip'):
            result = MemoryJobResult({
                'outcome': 'skip',
                'comment': _("Skipped after resuming execution")
            })
        elif action == _('fail'):
            result = MemoryJobResult({
                'outcome': 'fail',
                'comment': _("Failed after resuming execution")
            })
        elif action == 'run':
            result = None
        if result:
            manager.state.update_job_result(
                manager.state.job_state_map[last_job].job, result)
            manager.state.metadata.running_job_name = None
            manager.checkpoint()

    def _run_jobs(self, runner, ns, manager):
        self._run_jobs_with_session(ns, manager, runner)
        if not self._local_only:
            self.save_results(manager)

    def save_results(self, manager):
        if self.is_interactive:
            print("[ {} ]".format(_('Results')).center(80, '='))
            exporter = get_all_exporters()['text']()
            exported_stream = io.BytesIO()
            data_subset = exporter.get_session_data_subset(manager.state)
            exporter.dump(data_subset, exported_stream)
            exported_stream.seek(0)  # Need to rewind the file, puagh
            # This requires a bit more finesse, as exporters output bytes
            # and stdout needs a string.
            translating_stream = ByteStringStreamTranslator(
                sys.stdout, "utf-8")
            copyfileobj(exported_stream, translating_stream)
        # FIXME: this should probably not go to plainbox but checkbox-ng
        base_dir = os.path.join(
            os.getenv(
                'XDG_DATA_HOME', os.path.expanduser("~/.local/share/")),
            "plainbox")
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        results_file = os.path.join(base_dir, 'results.html')
        submission_file = os.path.join(base_dir, 'submission.xml')
        exporter_list = [XMLSessionStateExporter, HTMLSessionStateExporter]
        if 'xlsx' in get_all_exporters():
            from plainbox.impl.exporter.xlsx import XLSXSessionStateExporter
            exporter_list.append(XLSXSessionStateExporter)
        # We'd like these options for our reports.
        exp_options = ['with-sys-info', 'with-summary', 'with-job-description',
                       'with-text-attachments']
        for exporter_cls in exporter_list:
            # Exporters may support different sets of options, ensure we don't
            # pass an unsupported one (which would cause a crash)
            actual_options = [opt for opt in exp_options
                              if opt in exporter_cls.supported_option_list]
            exporter = exporter_cls(actual_options)
            data_subset = exporter.get_session_data_subset(manager.state)
            results_path = results_file
            if exporter_cls is XMLSessionStateExporter:
                results_path = submission_file
            # FIXME: replacing extension is ugly
            if 'xlsx' in get_all_exporters():
                if exporter_cls is XLSXSessionStateExporter:
                    results_path = results_path.replace('html', 'xlsx')
            with open(results_path, "wb") as stream:
                exporter.dump(data_subset, stream)
        print()
        print(_("Saving submission file to {}").format(submission_file))
        self.submission_file = submission_file
        print(_("View results") + " (HTML): file://{}".format(results_file))
        if 'xlsx' in get_all_exporters():
            # FIXME: replacing extension is ugly
            print(_("View results") + " (XLSX): file://{}".format(
                results_file.replace('html', 'xlsx')))

    def _interaction_callback(self, runner, job, config, prompt=None,
                              allowed_outcome=None):
        result = {}
        if prompt is None:
            prompt = _("Select an outcome or an action: ")
        if allowed_outcome is None:
            allowed_outcome = [IJobResult.OUTCOME_PASS,
                               IJobResult.OUTCOME_FAIL,
                               IJobResult.OUTCOME_SKIP]
        allowed_actions = [_('comments')]
        if job.command:
            allowed_actions.append(_('test'))
        result['outcome'] = IJobResult.OUTCOME_UNDECIDED
        while result['outcome'] not in allowed_outcome:
            print(_("Allowed answers are: {}").format(
                ", ".join(allowed_outcome + allowed_actions)))
            choice = input(prompt)
            if choice in allowed_outcome:
                result['outcome'] = choice
                break
            elif choice == _('test'):
                # NOTE: this can raise but oldcli is dead anyway
                ctrl = runner._get_ctrl_for_job(job)
                (result['return_code'],
                 result['io_log_filename']) = runner._run_command(
                     job, config, ctrl)
            elif choice == _('comments'):
                result['comments'] = input(_('Please enter your comments:\n'))
        return DiskJobResult(result)

    def _update_desired_job_list(self, manager, desired_job_list):
        problem_list = manager.state.update_desired_job_list(desired_job_list)
        if problem_list:
            print("[ {} ]".format(_('Warning')).center(80, '*'))
            print(_("There were some problems with the selected jobs"))
            for problem in problem_list:
                print(" * {}".format(problem))
            print(_("Problematic jobs will not be considered"))

    def _run_jobs_with_session(self, ns, manager, runner):
        # TODO: run all resource jobs concurrently with multiprocessing
        # TODO: make local job discovery nicer, it would be best if
        # desired_jobs could be managed entirely internally by SesionState. In
        # such case the list of jobs to run would be changed during iteration
        # but would be otherwise okay).
        if self._local_only:
            print("[ {} ]".format(
                _('Loading Jobs Definition')
            ).center(80, '='))
        else:
            print("[ {} ]".format(
                _('Running All Jobs')
            ).center(80, '='))
        again = True
        while again:
            again = False
            for job in manager.state.run_list:
                # Skip jobs that already have result, this is only needed when
                # we run over the list of jobs again, after discovering new
                # jobs via the local job output
                if (manager.state.job_state_map[job.id].result.outcome
                        is not None):
                    continue
                self._run_single_job_with_session(ns, manager, runner, job)
                manager.checkpoint()
                if job.plugin == "local":
                    # After each local job runs rebuild the list of matching
                    # jobs and run everything again
                    desired_job_list = select_jobs(manager.state.job_list,
                                                   self.whitelists)
                    if self._local_only:
                        desired_job_list = [
                            job for job in desired_job_list
                            if job.plugin == 'local']
                    self._update_desired_job_list(manager, desired_job_list)
                    again = True
                    break

    def _run_single_job_with_session(self, ns, manager, runner, job):
        if job.plugin not in ['local', 'resource']:
            print("[ {} ]".format(job.tr_summary()).center(80, '-'))
        job_state = manager.state.job_state_map[job.id]
        logger.debug(_("Job id: %s"), job.id)
        logger.debug(_("Plugin: %s"), job.plugin)
        logger.debug(_("Direct dependencies: %s"),
                     job.get_direct_dependencies())
        logger.debug(_("Resource dependencies: %s"),
                     job.get_resource_dependencies())
        logger.debug(_("Resource program: %r"), job.requires)
        logger.debug(_("Command: %r"), job.command)
        logger.debug(_("Can start: %s"), job_state.can_start())
        logger.debug(_("Readiness: %s"), job_state.get_readiness_description())
        if job_state.can_start():
            if job.plugin not in ['local', 'resource']:
                if job.description is not None:
                    print(job.description)
                    print("^" * len(job.description.splitlines()[-1]))
                    print()
                print(_("Running... (output in {}.*)").format(
                    join(manager.storage.location, slugify(job.id))))
            manager.state.metadata.running_job_name = job.id
            manager.checkpoint()
            # TODO: get a confirmation from the user for certain types of
            # job.plugin
            job_result = runner.run_job(job, job_state, self.config)
            if (job_result.outcome == IJobResult.OUTCOME_UNDECIDED
                    and self.is_interactive):
                job_result = self._interaction_callback(
                    runner, job, self.config)
            manager.state.metadata.running_job_name = None
            manager.checkpoint()
            if job.plugin not in ['local', 'resource']:
                print(_("Outcome: {}").format(job_result.outcome))
                if job_result.comments is not None:
                    print(_("Comments: {}").format(job_result.comments))
        else:
            job_result = MemoryJobResult({
                'outcome': IJobResult.OUTCOME_NOT_SUPPORTED,
                'comments': job_state.get_readiness_description()
            })
            if job.plugin not in ['local', 'resource']:
                print(_("Outcome: {}").format(job_result.outcome))
        if job_result is not None:
            manager.state.update_job_result(job, job_result)
