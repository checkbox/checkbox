# This file is part of Checkbox.
#
# Copyright 2012 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.

"""
plainbox.impl.box
=================

Internal implementation of plainbox

 * THIS MODULE DOES NOT HAVE STABLE PUBLIC API *
"""


import sys
from argparse import ArgumentParser
from argparse import FileType
from fnmatch import fnmatch
from io import TextIOWrapper
from logging import basicConfig
from logging import getLogger
from os import listdir
from os.path import join

from plainbox import __version__ as version
from plainbox.impl.checkbox import CheckBox
from plainbox.impl.job import JobDefinition
from plainbox.impl.result import JobResult
from plainbox.impl.rfc822 import load_rfc822_records
from plainbox.impl.runner import JobRunner
from plainbox.impl.session import SessionState


logger = getLogger("plainbox.box")


class PlainBox:
    """
    High-level plainbox object
    """

    def __init__(self):
        self._checkbox = CheckBox()

    def main(self, argv=None):
        basicConfig(level="WARNING")
        # TODO: setup sane logging system that works just as well for Joe user
        # that runs checkbox from the CD as well as for checkbox developers and
        # custom debugging needs.  It would be perfect^Hdesirable not to create
        # another broken, never-rotated, uncapped logging crap that kills my
        # SSD by writing junk to ~/.cache/
        parser = ArgumentParser(prog="plainbox")
        parser.add_argument(
            "-v", "--version", action="version",
            version="{}.{}.{}".format(*version[:3]))
        parser.add_argument(
            "-l", "--log-level", action="store",
            choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'),
            help="Set logging level")
        group = parser.add_argument_group(title="user interface options")
        group.add_argument(
            "-u", "--ui", action="store",
            default=None, choices=('headless', 'text', 'graphics'),
            help="select the UI front-end (defaults to auto)")
        group.add_argument(
            '--not-interactive', action='store_true',
            help="Skip tests that require interactivity")
        group = parser.add_argument_group(title="job definition options")
        group.add_argument(
            "--load-extra", action="append",
            metavar="FILE", default=[],
            help="Load extra job definitions from FILE",
            type=FileType("rt"))
        group.add_argument(
            '-r', '--run-pattern', action="append",
            metavar='PATTERN', default=[], dest='run_pattern_list',
            help="Run jobs matching the given pattern")
        group.add_argument(
            '-n', '--dry-run', action='store_true',
            help="Don't actually run any jobs")
        group = parser.add_argument_group("special options")
        group.add_argument(
            '--list-jobs', help="List jobs instead of running them",
            action="store_const", const="list-jobs", dest="special")
        group.add_argument(
            '--list-expressions', help="List all unique resource expressions",
            action="store_const", const="list-expr", dest="special")
        group.add_argument(
            '--dot', help="Print a graph of jobs instead of running them",
            action="store_const", const="dep-graph", dest="special")
        group.add_argument(
            '--dot-resources', action='store_true',
            help="Render resource relationships (for --dot)")
        ns = parser.parse_args(argv)
        # Set the desired log level
        if ns.log_level:
            getLogger("").setLevel(ns.log_level)
        # Load built-in job definitions
        job_list = self.get_builtin_jobs()
        # Load additional job definitions
        job_list.extend(self._load_jobs(ns.load_extra))
        # Now either do a special action or run the jobs
        if ns.special == "list-jobs":
            self._print_job_list(ns, job_list)
        elif ns.special == "list-expr":
            self._print_expression_list(ns, job_list)
        elif ns.special == "dep-graph":
            self._print_dot_graph(ns, job_list)
        else:
            self._run_jobs(ns, job_list)

    def _get_matching_job_list(self, ns, job_list):
        # Find jobs that matched patterns
        matching_job_list = []
        for job in job_list:
            for pattern in ns.run_pattern_list:
                if fnmatch(job.name, pattern):
                    matching_job_list.append(job)
                    break
        # As a special exception, when ns.special is set and we're either
        # listing jobs or job dependencies then when no run pattern was
        # specified just operate on the whole set. The ns.special check
        # prevents people starting plainbox from accidentally running _all_
        # jobs without prompting.
        if ns.special is not None and not ns.run_pattern_list:
            matching_job_list = job_list
        return matching_job_list

    def _print_job_list(self, ns, job_list):
        matching_job_list = self._get_matching_job_list(ns, job_list)
        for job in matching_job_list:
            print("{}".format(job))

    def _print_expression_list(self, ns, job_list):
        matching_job_list = self._get_matching_job_list(ns, job_list)
        expressions = set()
        for job in matching_job_list:
            prog = job.get_resource_program()
            if prog is not None:
                for expression in prog.expression_list:
                    expressions.add(expression.text)
        for expression in sorted(expressions):
            print(expression)

    def _print_dot_graph(self, ns, job_list):
        matching_job_list = self._get_matching_job_list(ns, job_list)
        print('digraph dependency_graph {')
        print('\tnode [shape=box];')
        for job in matching_job_list:
            if job.plugin == "resource":
                print('\t"{}" [shape=ellipse,color=blue];'.format(job.name))
            elif job.plugin == "attachment":
                print('\t"{}" [color=green];'.format(job.name))
            elif job.plugin == "local":
                print('\t"{}" [shape=invtriangle,color=red];'.format(
                    job.name))
            elif job.plugin == "shell":
                print('\t"{}" [];'.format(job.name))
            elif job.plugin in ("manual", "user-verify", "user-interact"):
                print('\t"{}" [color=orange];'.format(job.name))
            for dep_name in job.get_direct_dependencies():
                print('\t"{}" -> "{}";'.format(job.name, dep_name))
            prog = job.get_resource_program()
            if ns.dot_resources and prog is not None:
                for expression in prog.expression_list:
                    print('\t"{}" [shape=ellipse,color=blue];'.format(
                        expression.resource_name))
                    print('\t"{}" -> "{}" [style=dashed, label="{}"];'.format(
                        job.name, expression.resource_name,
                        expression.text.replace('"', "'")))
        print("}")

    def _run_jobs(self, ns, job_list):
        # Compute the run list, this can give us notification about problems in
        # the selected jobs. Currently we just display each problem
        matching_job_list = self._get_matching_job_list(ns, job_list)
        print("[ Analyzing Jobs ]".center(80, '='))
        # Create a session that handles most of the stuff needed to run jobs
        session = SessionState(job_list)
        self._update_desired_job_list(session, matching_job_list)
        with session.open():
            if (sys.stdin.isatty() and sys.stdout.isatty() and not
                    ns.not_interactive):
                outcome_callback = self.ask_for_outcome
            else:
                outcome_callback = None
            runner = JobRunner(self._checkbox, session.session_dir,
                               outcome_callback=outcome_callback)
            self._run_jobs_with_session(ns, session, runner)
        print("[ Results ]".center(80, '='))
        for job_name in sorted(session.job_state_map):
            job_state = session.job_state_map[job_name]
            if job_state.result.outcome != JobResult.OUTCOME_NONE:
                print("{}: {}".format(job_name, job_state.result.outcome))

    def ask_for_outcome(self, prompt=None, allowed=None):
        if prompt is None:
            prompt = "what is the outcome? "
        if allowed is None:
            allowed = (JobResult.OUTCOME_PASS,
                       JobResult.OUTCOME_FAIL,
                       JobResult.OUTCOME_SKIP)
        answer = None
        while answer not in allowed:
            print("Allowed answers are: {}".format(", ".join(allowed)))
            answer = input(prompt)
        return answer

    def _update_desired_job_list(self, session, desired_job_list):
        problem_list = session.update_desired_job_list(desired_job_list)
        if problem_list:
            print("[ Warning ]".center(80, '*'))
            print("There were some problems with the selected jobs")
            for problem in problem_list:
                print(" * {}".format(problem))
            print("Problematic jobs will not be considered")

    def _run_jobs_with_session(self, ns, session, runner):
        # TODO: run all resource jobs concurrently with multiprocessing
        # TODO: make local job discovery nicer, it would be best if
        # desired_jobs could be managed entirely internally by SesionState. In
        # such case the list of jobs to run would be changed during iteration
        # but would be otherwise okay).
        print("[ Running All Jobs ]".center(80, '='))
        again = True
        while again:
            again = False
            for job in session.run_list:
                # Skip jobs that already have result, this is only needed when
                # we run over the list of jobs again, after discovering new
                # jobs via the local job output
                if session.job_state_map[job.name].result.outcome is not None:
                    continue
                self._run_single_job_with_session(ns, session, runner, job)
                if job.plugin == "local":
                    # After each local job runs rebuild the list of matching
                    # jobs and run everything again
                    new_matching_job_list = self._get_matching_job_list(
                        ns, session.job_list)
                    self._update_desired_job_list(
                        session, new_matching_job_list)
                    again = True
                    break

    def _run_single_job_with_session(self, ns, session, runner, job):
        print("[ {} ]".format(job.name).center(80, '-'))
        job_state = session.job_state_map[job.name]
        print("Job name: {}".format(job.name))
        print("Plugin: {}".format(job.plugin))
        print("Direct dependencies: {}".format(job.get_direct_dependencies()))
        print("Resource dependencies: {}".format(
            job.get_resource_dependencies()))
        print("Resource program: {!r}".format(job.requires))
        print("Command: {!r}".format(job.command))
        print("Can start: {}".format(job_state.can_start()))
        print("Readiness: {}".format(job_state.get_readiness_description()))
        if job_state.can_start():
            if ns.dry_run:
                print("Not really running anything in dry-run mode")
                job_result = JobResult({
                    'job': job,
                    'outcome': 'dry-run',
                })
            else:
                print("Running...")
                job_result = runner.run_job(job)
                print("Outcome: {}".format(job_result.outcome))
                print("Comments: {}".format(job_result.comments))
        else:
            job_result = JobResult({
                'job': job,
                'outcome': JobResult.OUTCOME_NOT_SUPPORTED
            })
        if job_result is None and not ns.dry_run:
            logger.warning("Job %s did not return a result", job)
        if job_result is not None:
            session.update_job_result(job, job_result)

    def get_builtin_jobs(self):
        logger.debug("Loading built-in jobs...")
        return self._load_builtin_jobs()

    def save(self, something, somewhere):
        raise NotImplementedError()

    def load(self, somewhere):
        if isinstance(somewhere, str):
            # Load data from a file with the given name
            filename = somewhere
            with open(filename, 'rt', encoding='UTF-8') as stream:
                return load(stream)
        if isinstance(somewhere, TextIOWrapper):
            stream = somewhere
            logger.debug("Loading jobs definitions from %r...", stream.name)
            record_list = load_rfc822_records(stream)
            job_list = []
            for record in record_list:
                job = JobDefinition.from_rfc822_record(record)
                logger.debug("Loaded %r", job)
                job_list.append(job)
            return job_list
        else:
            raise TypeError(
                "Unsupported type of 'somewhere': {!r}".format(
                    type(somewhere)))

    def _load_jobs(self, source_list):
        """
        Load jobs from the list of sources
        """
        job_list = []
        for source in source_list:
            job_list.extend(self.load(source))
        return job_list

    def _load_builtin_jobs(self):
        """
        Load jobs from built into CheckBox
        """
        return self._load_jobs([
            join(self._checkbox.jobs_dir, name)
            for name in listdir(self._checkbox.jobs_dir)
            if name.endswith(".txt") or name.endswith(".txt.in")])


# Instantiate a global plainbox instance
# XXX: Allow one to control the checkbox= argument via environment or config.
box = PlainBox()

# Extract the methods from the global instance, needed by the public API
get_builtin_jobs = box.get_builtin_jobs
save = box.save
load = box.load
run = None
main = box.main
