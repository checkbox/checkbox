# This file is part of Checkbox.
#
# Copyright 2015 Canonical Ltd.
# Written by:
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
:mod:`sudo_with_pass_ctrl` -- Self Providing Sudo Execution Controller
======================================================================

This module defines an Execution Controller capable of running plainbox' jobs
as the user supplied in job definition. It does so by launching `sudo -S (...)`
in a subprocess and writing password to the subprocess' stdin.
"""
try:
    import grp
except ImportError:
    grp = None
import logging
import os
try:
    import posix
except ImportError:
    posix = None
import subprocess

from plainbox.i18n import gettext as _
from plainbox.impl.ctrl import CheckBoxDifferentialExecutionController

logger = logging.getLogger("checkbox_touch.sudo_with_pass_ctrl")


class RootViaSudoWithPassExecutionController(
        CheckBoxDifferentialExecutionController):
    """
    Execution controller that gains root by using sudo, automatically
    supplying password to the sudo process.

    This controller should be used for jobs that need root in front-ends that
    are not CLI based.
    """

    def __init__(self, provider_list, password_provider_cls):
        """
        Initialize a new RootViaSudoWithPassExecutionController

        :param provider_list:
            A list of Provider1 objects that will be available for script
            dependency resolutions. Currently all of the scripts are makedirs
            available but this will be refined to the minimal set later.
        :param password_provider_cls:
            A callable that will be used to obtain user's password.
            It is called when the controller runs a sudo command.
        """
        super().__init__(provider_list)
        try:
            in_sudo_group = grp.getgrnam("sudo").gr_gid in posix.getgroups()
        except KeyError:
            in_sudo_group = False
        try:
            in_admin_group = grp.getgrnam("admin").gr_gid in posix.getgroups()
        except KeyError:
            in_admin_group = False
        self.user_can_sudo = in_sudo_group or in_admin_group
        self._password_provider = password_provider_cls

    def get_execution_command(self, job, job_state, config, session_dir,
                              nest_dir):
        """
        Get the command to execute the specified job

        :param job:
            job definition with the command and environment definitions
        :param job_state:
            The JobState associated to the job to execute.
        :param config:
            A PlainBoxConfig instance which can be used to load missing
            environment definitions that apply to all jobs. It is used to
            provide values for missing environment variables that are required
            by the job (as expressed by the environ key in the job definition
            file).
        :param session_dir:
            Base directory of the session this job will execute in.
            This directory is used to co-locate some data that is unique to
            this execution as well as data that is shared by all executions.
        :param nest_dir:
            A directory with a nest of symlinks to all executables required to
            execute the specified job. This argument may or may not be used,
            depending on how PATH is passed to the command (via environment or
            via the commant line)
        :returns:
            List of command arguments
        """
        # Run env(1) as the required user
        # --prompt is used to set sudo promp to an empty string so we don't
        # pollute command output
        # --reset-timestamp makes sudo ask for password even if it has been
        # supplied recently
        cmd = ['sudo', '--prompt=', '--reset-timestamp', '--stdin',
               '--user', job.user, 'env']
        # Append all environment data
        env = self.get_differential_execution_environment(
            job, job_state, config, session_dir, nest_dir)
        cmd += ["{key}={value}".format(key=key, value=value)
                for key, value in sorted(env.items())]
        # Lastly use job.shell -c, to run our command
        cmd += [job.shell, '-c', job.command]
        return cmd

    def execute_job(self, job, job_state, config, session_dir, extcmd_popen):
        """
        Execute the job using standard subprocess.Popen

        :param job:
            The JobDefinition to execute
        :param job_state:
            The JobState associated to the job to execute.
        :param config:
            A PlainBoxConfig instance which can be used to load missing
            environment definitions that apply to all jobs. It is used to
            provide values for missing environment variables that are required
            by the job (as expressed by the environ key in the job definition
            file).
        :param session_dir:
            Base directory of the session this job will execute in.
            This directory is used to co-locate some data that is unique to
            this execution as well as data that is shared by all executions.
        :param extcmd_popen:
            A subprocess.Popen like object - ignored
        :returns:
            The return code of the command, as returned by subprocess.call()

        The reason behind not using extcmd_popen is that it doesn't support
        connecting pipe to stdin of the process it spawns. And this is required
        for running 'sudo -S'.
        """
        if not os.path.isdir(self.get_CHECKBOX_DATA(session_dir)):
            os.makedirs(self.get_CHECKBOX_DATA(session_dir))
        # Setup the executable nest directory
        with self.configured_filesystem(job, config) as nest_dir:
            # Get the command and the environment.
            # of this execution controller
            cmd = self.get_execution_command(
                job, job_state, config, session_dir, nest_dir)
            env = self.get_execution_environment(
                job, job_state, config, session_dir, nest_dir)
            with self.temporary_cwd(job, config) as cwd_dir:
                # run the command
                # TRANSLATORS: Please leave %(CMD)r, %(ENV)r, %(DIR)r as-is
                logger.debug(_("job[%(ID)s] executing %(CMD)r with env %(ENV)r"\
                               " in cwd %(DIR)r"),
                             {"ID": job.id, "CMD": cmd,
                             "ENV": env, "DIR": cwd_dir})
                p = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                     env=env, cwd=cwd_dir)
                #  sudo manpage explicitly states that \n should be appended
                pass_bytes = bytes(self._password_provider() + '\n', 'UTF-8')
                p.communicate(input=pass_bytes)
                return_code = p.returncode
                if 'noreturn' in job.get_flag_set():
                    self._halt()
                return return_code

    def get_checkbox_score(self, job):
        """
        Compute how applicable this controller is for the specified job.

        :returns:
            -1 if the job does not have a user override or the user cannot use
            sudo and 2 otherwise
        """
        # Only makes sense with jobs that need to run as another user
        if job.user is not None and self.user_can_sudo:
            return 2
        else:
            return -1
