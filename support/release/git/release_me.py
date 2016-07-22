#!/usr/bin/env python3
# This file is part of Checkbox.
#
# Copyright 2016 Canonical Ltd.
# Written by:
#   Sylvain Pineau <sylvain.pineau@canonical.com>
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

# Requires python3.5 and bumpversion, both available as of 16.04,
# twine and lptools.
# Quiet with: echo 'no-tty' >> ~/.gnupg/gpg.conf

import configparser
import glob
import logging
import os
import shutil
import subprocess

from guacamole import Command


projects = (
    # 'checkbox-converged',
    'plainbox-provider-certification-client',
    'plainbox-provider-certification-server',
)


class ConsoleFormatter(logging.Formatter):

    """Custom Logging Formatter to ease copy paste of commands."""

    def format(self, record):
        fmt = '%(message)s'
        if record.levelno == logging.ERROR:
            fmt = "%(levelname)-8s %(message)s"
        result = logging.Formatter(fmt).format(record)
        return result

# create logger
logger = logging.getLogger('release')
logger.setLevel(logging.INFO)
# create file handler which logs even debug messages
fh = logging.FileHandler('release.log')
# create console handler with a higher log level
ch = logging.StreamHandler()
# create formatter and add it to the handlers
fh_formatter = logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s')
fh.setFormatter(fh_formatter)
ch.setFormatter(ConsoleFormatter())
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


def run(*args, **kwargs):
    """wrapper for subprocess.run."""
    try:
        return subprocess.run(
            *args, **kwargs,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        logger.error('{}\n{}'.format(e, e.output.decode()))
        raise SystemExit(1)


class Release(Command):

    """The Release command."""

    BASE_URL = 'git+ssh://git.launchpad.net'

    def register_arguments(self, parser):
        """Register command line arguments."""
        parser.add_argument(
            'mode', metavar='MODE', choices=['rc', 'final'],
            help='new release candidate (rc) or final version (final)')
        parser.add_argument(
            '--user', default='checkbox-dev',
            help=("source repositories owner (default: %(default)s)"))
        parser.add_argument(
            '--target-user', default='checkbox-dev',
            help=("target repositories owner (default: %(default)s)"))

    def invoked(self, ctx):
        """Method called when the command is invoked."""
        for project in projects:
            # Clone the project source and packaging repositories
            self.clone(ctx, project)
            logger.info("".center(80, '#'))
            if not self.release_required(ctx, project):
                self._cleanup(ctx, project)
                logger.info("# Skipping {}...".format(project))
                logger.info("".center(80, '#'))
                continue
            logger.info("# Processing {}...".format(project))
            logger.info("".center(80, '#'))
            # Checkout the release branch
            process = run(['git', 'checkout', '-b', 'release'], cwd=project)
            if process.returncode:
                run(['git', 'checkout', 'release'], cwd=project, check=True)
            # Bump versions
            self.bump_version(ctx, project)
            # Tag the release (code repo)
            self.tag_version(ctx, project)
            # Create the release source tarball
            self.create_source_tarball(ctx, project)
            # Open for development if we did a final release
            if ctx.args.mode == 'final':
                self.open_for_development(ctx, project)
            # Do the git-dpm dance
            self.prepare_debian_tarball(ctx, project)
            self.dance(ctx, project)
            # Push code and packaging repositories to Launchpad
            logger.info("# Review the code and packaging repo "
                        "then push the updates to Launchpad with:")
            logger.info("git -C {} push {}/~{}/{} release --tags".format(
                project, self.BASE_URL, ctx.args.target_user, project))
            logger.info(
                "git -C {} push {}/~{}/{}/+git/packaging --all".format(
                    self.packaging, self.BASE_URL,
                    ctx.args.target_user, project))
            logger.info(
                "git -C {} push {}/~{}/{}/+git/packaging --tags".format(
                    self.packaging, self.BASE_URL,
                    ctx.args.target_user, project))
            if ctx.args.mode == 'final':
                # Propose to merge the release branch into master
                logger.info(
                    "# Propose to merge the release branch into master")
                logger.info(
                    "./lp-propose-merge ~{}/{}".format(
                        ctx.args.target_user, project))
                # Delete the release branch once merged into master
                logger.info(
                    "# Delete the release branch once merged into master")
                logger.info(
                    "git -C {} push origin --delete release".format(project))
            # Update the PPA recipe and kick-off the build
            logger.info("# Build the new package in Launchpad PPA")
            if ctx.args.mode == 'rc':
                logger.info(
                    "./lp-recipe-update-build {} --recipe {} -n {}".format(
                        project, project+'-testing', self.new_version))
            else:
                logger.info(
                    "./lp-recipe-update-build --recipe {} {} -n {}".format(
                        project, project+'-stable', self.new_version))
                # Release the current milestone (final only)
                logger.info(
                    "# Release the milestone and upload tarball to Launchpad")
                logger.info(
                    "./lp-release-milestone {} -m {}".format(
                        project, self.new_version))
                # Upload tarball to Launchpad (final only)
                logger.info(
                    "lp-project-upload {} {} {}".format(
                        project, self.new_version, self.tarball))
            if os.path.exists(os.path.relpath(project+'/setup.py')):
                # Upload tarball to PyPI (including RC) for setuptools projects
                logger.info("# Upload tarball to PyPI")
                logger.info("twine upload {}".format(self.tarball))

    def release_required(self, ctx, project):
        """Check both code and packaging repos for new commits."""
        run(["git", "update-index", "--refresh"])
        version_pattern = '*'
        if ctx.args.mode == 'final':
            version_pattern = '*[^c][0-9]'  # Up to 9 RC :)
        code_change = run(
            'git diff $(git describe --abbrev=0 --tags --match '
            '"v{}") --name-only'.format(version_pattern),
            shell=True, cwd=project, check=True).stdout
        packaging_change = run(
            'git diff $(git describe --abbrev=0 --tags --match '
            '"debian-{}") --name-only'.format(version_pattern),
            shell=True, cwd='packaging_{}'.format(project), check=True).stdout
        if code_change or packaging_change:
            return [code_change, packaging_change]
        else:
            return []

    def clone(self, ctx, project):
        """Clone code and packaging repositories."""
        self.packaging = 'packaging_{}'.format(project)
        run(['git', 'clone', '{}/~{}/{}'.format(
            self.BASE_URL, ctx.args.user, project)])
        run(['git', 'clone', '{}/~{}/{}/+git/packaging'.format(
            self.BASE_URL, ctx.args.user, project), self.packaging])
        for path in [project, self.packaging]:
            if not os.path.exists(path):
                logger.error('Unable to clone {}'.format(path))
                raise SystemExit(1)
        # Fetch the release branch if it exists
        run(['git', 'fetch', 'origin', 'release:release'], cwd=project)
        # Update origin url if needed
        if ctx.args.target_user != ctx.args.user:
            url = run(['git', 'remote', 'get-url', 'origin'],
                      cwd=project, check=True).stdout.decode().rstrip()
            url = url.replace(ctx.args.user, ctx.args.target_user)
            run(['git', 'remote', 'set-url', 'origin', url],
                cwd=project, check=True)

    def _cleanup(self, ctx, project):
        shutil.rmtree(project)
        shutil.rmtree(self.packaging)

    def bump_version(self, ctx, project):
        """
        Bump project version according to release mode.

        Using https://github.com/peritus/bumpversion
        Also available (16.04+) with: sudo apt install bumpversion
        """
        config = configparser.ConfigParser()
        try:
            config.read(os.path.relpath(project+'/.bumpversion.cfg'))
            self.current_version = config['bumpversion']['current_version']
        except KeyError:
            logger.error("{} .bumpversion.cfg not found".format(project))
            raise SystemExit(1)
        bumpversion_output = ''
        # XXX: Several calls to bumpversion are required until
        # https://github.com/peritus/bumpversion/issues/50 is solved
        # (Allow the part to be defined on the command line)
        if ctx.args.mode == 'final':
            if 'dev' in self.current_version:
                # bump to jump to rc0
                run(['bumpversion', 'release', '--allow-dirty', '--list'],
                    cwd=project, check=True)
                # bump to jump to final
                bumpversion_output = run(
                    ['bumpversion', 'release', '--allow-dirty', '--list'],
                    cwd=project, check=True).stdout.decode()
            elif 'rc' in self.current_version:
                # bump to jump to final
                bumpversion_output = run(
                    ['bumpversion', 'release', '--allow-dirty', '--list'],
                    cwd=project, check=True).stdout.decode()
            else:
                # bump to jump to dev0
                run(['bumpversion', 'minor', '--allow-dirty', '--list'],
                    cwd=project, check=True)
                # bump to jump to rc0
                run(['bumpversion', 'release', '--allow-dirty', '--list'],
                    cwd=project, check=True)
                # bump to jump to final
                bumpversion_output = run(
                    ['bumpversion', 'release', '--allow-dirty', '--list'],
                    cwd=project, check=True).stdout.decode()
        else:
            if 'dev' in self.current_version:
                # bump to jump to rc0
                run(['bumpversion', 'release', '--allow-dirty', '--list'],
                    cwd=project, check=True)
                # bump to jump to rc1
                bumpversion_output = run(
                    ['bumpversion', 'N', '--allow-dirty', '--list'],
                    cwd=project, check=True).stdout.decode()
            elif 'rc' in self.current_version:
                # bump to jump to rc(N+1)
                bumpversion_output = run(
                    ['bumpversion', 'N', '--allow-dirty', '--list'],
                    cwd=project, check=True).stdout.decode()
            else:
                # bump to jump to dev0
                run(['bumpversion', 'minor', '--allow-dirty', '--list'],
                    cwd=project, check=True)
                # bump to jump to rc0
                run(['bumpversion', 'release', '--allow-dirty', '--list'],
                    cwd=project, check=True)
                # bump to jump to rc1
                bumpversion_output = run(
                    ['bumpversion', 'N', '--allow-dirty', '--list'],
                    cwd=project, check=True).stdout.decode()
        self.new_version = bumpversion_output.splitlines()[-1].replace(
            'new_version=', '')
        run(['git', 'add', '--all'], cwd=project, check=True)
        run(['git', 'commit', '-m', 'Bump to v'+self.new_version],
            cwd=project, check=True)

    def tag_version(self, ctx, project):
        """Tag (and sign) the code version."""
        run(['git', 'tag', '-s', 'v'+self.new_version,
            '-m', 'Release {} v{}'.format(project, self.new_version)],
            cwd=project, check=True)

    def create_source_tarball(self, ctx, project):
        """Create and sign the project source tarball."""
        if os.path.exists(os.path.relpath(project+'/manage.py')):
            run(['./manage.py', 'sdist'], cwd=project, check=True)
        # XXX Add setup.py + make sdist + missing gpg sign commands

    def open_for_development(self, ctx, project):
        """Bump the project version to open a new release for development."""
        bumpversion_output = run(
            ['bumpversion', 'minor', '--allow-dirty', '--list'],
            cwd=project, check=True).stdout.decode()
        new_dev_version = bumpversion_output.splitlines()[-1].replace(
            'new_version=', '')
        run(['git', 'add', '--all'], cwd=project, check=True)
        run(['git', 'commit', '-m', 'increment version to v'+new_dev_version],
            cwd=project, check=True)

    def prepare_debian_tarball(self, ctx, project):
        """Copy the project release tarball to a debian suitable name."""
        self.debian_new_version = self.new_version.replace('rc', '~rc')
        archives = glob.glob('{}/dist/*{}.tar.gz'.format(
            project, self.new_version))
        self.orig_tarball = '{}_{}.orig.tar.gz'.format(
            project, self.debian_new_version)
        try:
            self.tarball = archives[-1]
            shutil.copyfile(self.tarball, self.orig_tarball)
        except (IndexError, FileNotFoundError):
            logger.error("{} sdist tarball not found".format(project))
            raise SystemExit(1)

    def dance(self, ctx, project):
        """Update the packaging repo with git-dpm."""
        run(['git-dpm', 'import-new-upstream',
            os.path.join('..', self.orig_tarball)],
            cwd=self.packaging, check=True)
        run(['pristine-tar', 'commit',
            os.path.join('..', self.orig_tarball)],
            cwd=self.packaging, check=True)
        run(['git-dpm', 'prepare'], cwd=self.packaging, check=True)
        run(['git-dpm', 'dch', '--', '-v', self.debian_new_version+'-1',
            '-D', 'UNRELEASED', '"new upstream version"'],
            cwd=self.packaging, check=True)
        run(['git-dpm', 'status'], cwd=self.packaging, check=True)
        run(['git-dpm', 'tag'], cwd=self.packaging, check=True)


if __name__ == "__main__":
    try:
        import bumpversion
        bumpversion.__VERSION__  # To make flake8 happy
    except ImportError:
        logger.error(
            "Please install bumpversion (sudo apt install bumpversion)")
        raise SystemExit(1)
    Release().main()
