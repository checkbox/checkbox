#!/usr/bin/python3
# This file is part of Checkbox.
#
# Copyright 2014 Canonical Ltd.
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

import glob
import os
import re
import shutil
from argparse import ArgumentParser
from subprocess import check_output, call, STDOUT

from pkg_resources import parse_version


BRANCH_PREFIX = "lp:~checkbox-dev/checkbox/"


class Package:

    def __init__(self, name, directory=".", packaging_release=None):
        self._name = name
        self._packaging_release = packaging_release
        self._trunk_tags_cache = None
        self._packaging_tags_cache = None
        self._directory = os.path.expanduser(directory)

    @property
    def name(self):
        return self._name

    @property
    def project(self):
        # Only for plainbox-provider-resource-generic, where the lp project is
        # just https://launchpad.net/plainbox-provider-resource/
        return self._name.replace('-generic', '')

    @property
    def ppa_packaging_branch(self):
        if self._packaging_release:
            return "ppa-packaging-{}-{}".format(self._name,
                                                self._packaging_release)
        return "ppa-packaging-{}".format(self._name)

    @property
    def ppa_packaging_release_branch(self):
        if self._packaging_release:
            return "ppa-packaging-{}-{}-release".format(self._name,
                                                     self._packaging_release)
        return "ppa-packaging-{}-release".format(self._name)

    @property
    def trunk_branch(self):
        return "trunk"

    @property
    def trunk_release_branch(self):
        return "release"

    @property
    def testing_recipe(self):
        if self._packaging_release:
            return "{}-{}-testing".format(self._name, self._packaging_release)
        return "{}-testing".format(self._name)

    @property
    def stable_recipe(self):
        if self._packaging_release:
            return "{}-{}-stable".format(self._name, self._packaging_release)
        return "{}-stable".format(self._name)

    @property
    def path(self):
        if self._name == "plainbox-provider-canonical-certification":
            return os.path.join("providers",
                                "plainbox-provider-certification-*")
        elif "plainbox-provider-" in self._name:
            return os.path.join("providers", self.name)
        elif self._name == "cdts":
            return "plainbox-provider-canonical-driver-test-suite"
        elif self._name == "checkbox-converged":
            return "checkbox-touch"
        else:
            return self._name

    @property
    def basedir(self):
        return os.path.join(self._directory, self.trunk_branch, self.path)

    @property
    def _trunk_tags(self):
        if self._trunk_tags_cache:
            return self._trunk_tags_cache
        else:
            # Asking for time-sorted tags helps with some later manipulations.
            self._trunk_tags_cache = check_output(
                ["bzr", "tags", "--sort=time", "-d",
                 os.path.join(self._directory, self.trunk_branch)],
                universal_newlines=True
                ).rstrip()
            return self._trunk_tags_cache

    @property
    def last_stable_tag_in_trunk(self):
        """Gives the last stable tag for the whole trunk (if no
        package_name is given). It will effectively return the most recent
        non-candidate tag added to the branch. Orphan tags (not pointing to any
        revision) are ignored."""
        tags_only = [t.split()[0] for t in self._trunk_tags.split("\n") if
                     "?" not in t.split()[-1] and
                     not re.search(r'\.\d+c\d+$', t.split()[0])]
        assert tags_only != []  # because there should be at least one
        if tags_only:
            return tags_only[-1]  # Last chronological tag, name only

    @property
    def last_stable_trunk_tag(self):
        name = self._name
        tags = sorted([tag for tag in self._trunk_tags.split()
                      if re.match(name, tag)], key=parse_version)
        tags.reverse()
        for tag in tags:
            if not re.search(r'\.\d+c\d+$', tag):
                return tag
        # FIXME: Raise a ValueError here

    @property
    def last_trunk_tag(self):
        tags = sorted([tag for tag in self._trunk_tags.split()
                      if re.match(self._name, tag)], key=parse_version)
        tags.reverse()
        for tag in tags:
            return tag
        # FIXME: Raise a ValueError here

    @property
    def _packaging_tags(self):
        if self._packaging_tags_cache:
            return self._packaging_tags_cache
        else:
            # Asking for time-sorted tags helps with some later manipulations.
            self._packaging_tags_cache = check_output(
                ["bzr", "tags", "--sort=time", "-d",
                 os.path.join(self._directory, self.ppa_packaging_branch)],
                universal_newlines=True
                ).rstrip()
            return self._packaging_tags_cache

    @property
    def last_stable_packaging_tag(self):
        tags = sorted([tag for tag in self._packaging_tags.split()
                      if re.match(self.ppa_packaging_branch, tag)],
                      key=parse_version)
        tags.reverse()
        for tag in tags:
            if not re.search(r'\.\d+c\d+$', tag):
                return tag
        # FIXME: Raise a ValueError here

    @property
    def last_stable_trunk_tag_rev(self):
        for tagline in self._trunk_tags.split("\n"):
            tag, rev = tagline.split()
            if tag != self.last_stable_trunk_tag:
                continue
            return re.sub(r'\..*$', '', rev)

    @property
    def last_stable_packaging_tag_rev(self):
        for tagline in self._packaging_tags.split("\n"):
            tag, rev = tagline.split()
            if tag != self.last_stable_packaging_tag:
                continue
            return re.sub(r'\..*$', '', rev)

    @property
    def release_required(self):
        return True
        log = check_output(
            ["bzr log --verbose --include-merged -r{}.. {}".format(
                self.last_stable_trunk_tag_rev, self.basedir)],
            shell=True)
        # Ignore version bump only (__init__.py and setup.py)
        new_rev = [
            rev for rev in re.findall(
                r'revno:.*?message:\n\s+(.*?\n)',
                log, re.M | re.S) if not re.search(
                r'(automatic merge by tarmac)|(: increment version to )', rev)]
        return True if new_rev else False

    @property
    def ppa_packaging_release_required(self):
        return True
        log = check_output(
            ["bzr log -S -v -r{}.. {}".format(
                self.last_stable_packaging_tag_rev, os.path.join(
                    self._directory, self.ppa_packaging_branch))], shell=True)
        changes = set(re.findall(r"\s+[AMD]  (debian/.*?)\n", log))
        # Ignore debian/changelog modifications only
        if changes == {'debian/changelog'}:
            return False
        elif changes:
            return True
        else:
            return False

    @property
    def sdist_command(self):
        if self._name == "plainbox-provider-canonical-certification":
            return None
        if os.path.exists(os.path.join(self.basedir, "setup.py")):
            return "./setup.py -q sdist"
        elif os.path.exists(os.path.join(self.basedir, "manage.py")):
            return "./manage.py sdist"
        else:
            return None


def create_logs(packages, trunk_tag, dir="logs"):
    return
    if check_bzr_cb_format_support():
        log_format = "--cb"
    else:
        # A fallback in case the plugin wasn't copied properly
        log_format = "--short"
    if not os.path.isdir(dir):
        os.makedirs(dir)
    # Write a log for each packaging branch
    for pack in packages:
        command = ["bzr", "log", log_format,
                   "-r", pack.last_stable_packaging_tag + "..",
                   pack.ppa_packaging_branch]
        log_data = check_output(command, universal_newlines=True)
        with open(os.path.join(dir, pack.name), "w") as logfile:
            logfile.write("Command: {}".format(" ".join(command)))
            logfile.write("\n")
            logfile.write(log_data)
    # Finally write a global log to account for all changes in trunk
    command = ["bzr", "log", log_format,
               "-r", trunk_tag + "..",
               pack.trunk_branch]
    log_data = check_output(command)
    with open(os.path.join(dir, "trunk"), "wb") as logfile:
        logfile.write(log_data)


def check_bzr_cb_format_support():
    bzr_log_help_text = check_output(["bzr", "help", "log"],
                                     universal_newlines=True)
    return "--cb" in str(bzr_log_help_text)


def copy_bzr_cb_format_plugin():
    plugin_file = "checkbox_changelog.py"
    dest_path = os.path.join(os.environ['HOME'], '.bazaar', 'plugins')
    if os.path.isfile(plugin_file):
        try:
            shutil.copy(plugin_file, dest_path)
            return True
        except OSError as err:
            print("W: Unable to copy bazaar log formatter")
            print("W: {}".format(err))
            print("I will fall back to standard --short format for the logs")
            return False
    return False


if __name__ == "__main__":

    parser = ArgumentParser(description='Release Management Script')
    parser.add_argument(
        'mode', metavar='MODE', choices=['testing', 'stable'],
        help='build a release candidate or the final version')
    parser.add_argument(
        '--cdts', action='store_true',
        help='release Canonical Driver Test Suite only')

    args = parser.parse_args()

    packages = [
        Package('checkbox-support'),
        Package('plainbox'),
        #Package('plainbox-provider-canonical-certification'),
        Package('plainbox-provider-checkbox'),
        Package('plainbox-provider-sru'),
        Package('checkbox-ng'),
        Package('plainbox-provider-resource-generic'),
        Package('checkbox-converged'),
        Package('checkbox-converged', packaging_release='trusty'),
    ]

    if args.cdts:
        BRANCH_PREFIX = "lp:~checkbox-ihv-ng/cdts/"
        packages = [Package('cdts')]

    push_commands = []
    build_commands = []
    merge_commands = []
    sdist_commands = []
    twine_commands = []
    release_milestone_commands = []

    if not check_bzr_cb_format_support():
        copy_bzr_cb_format_plugin()

    if args.mode == 'stable':

        trunk_changelog_start_tag = packages[0].last_stable_tag_in_trunk
        for pack in packages:
            # In stable mode, build the logs *before* adding new stable tags
            create_logs(packages, trunk_changelog_start_tag, "logs/")
            if pack.release_required or pack.ppa_packaging_release_required:
                pack.current_version = pack.last_trunk_tag.replace(
                    pack.name+"-v", "")
                log = check_output(
                    ["./releasectl", pack.name, "--dry-run",
                     "--origin={}".format(pack.trunk_branch),
                     "--in-place",
                     "--current-version={}".format(pack.current_version),
                     "--final"], stderr=STDOUT, universal_newlines=True)
                final_version = re.search(
                    r'I: next version is (.*)', log).group(1)
                print("".center(80, '#'))
                print(" {}: (current version: {}) ".format(
                    pack.name, pack.current_version).center(80, '#'))
                print("".center(80, '#'))
                call("perl -pi -e 's/~dev//g' {}/debian/changelog".format(
                    pack.ppa_packaging_branch), shell=True)
                call('dch "New upstream release" -b --distribution UNRELEASED '
                     '-v {} -c {}/debian/changelog'.format(
                         final_version,
                         pack.ppa_packaging_branch), shell=True)
                call("perl -pi -e 's/\s+\* Open for development \(remove "
                     "this message before releasing\)\n//g' "
                     "{}/debian/changelog".format(pack.ppa_packaging_branch),
                     shell=True)
                call('cd {} && bzr commit -m "New upstream release" '
                     '--quiet'.format(pack.ppa_packaging_branch), shell=True)
                call(["./releasectl", pack.name,
                      "--origin={}".format(pack.trunk_branch),
                      "--in-place",
                      "--current-version={}".format(pack.current_version),
                      "--final"])
                call(["./releasectl", pack.ppa_packaging_branch,
                      "--origin={}".format(pack.ppa_packaging_branch),
                      "--in-place",
                      "--current-version={}".format(pack.current_version),
                      "--final"])
                if pack.sdist_command:
                    call('cd {} && {}'.format(pack.basedir,
                                              pack.sdist_command),
                         shell=True)
                    call('cd {} && {}'.format(os.path.join(pack.basedir,
                                                           'dist'),
                                              'gpg --armor --sign --detach-sig'
                                              ' *.tar.gz'),
                         shell=True)
                    sdist_commands.append("lp-project-upload {} {} {}".format(
                                          pack.project, final_version,
                                          glob.glob("{}/dist/*.tar.gz".format(
                                              pack.basedir))[-1]))
                    twine_commands.append("twine upload {}/dist/*".format(
                                          pack.basedir))
        # TODO: build/upload (to launchpad/pypi) the source tarballs here
        # before the next step where the version is updated to the next ~devel
        # Maybe 3 steps are needed: testing, tarballs, stable?
        for pack in packages:
            if pack.release_required or pack.ppa_packaging_release_required:
                log = check_output(
                    ["./releasectl", pack.name, "--dry-run",
                     "--origin={}".format(pack.trunk_branch),
                     "--in-place",
                     "--current-version={}".format(pack.current_version),
                     "--final"], stderr=STDOUT, universal_newlines=True)
                final_version = re.search(
                    r'I: next version is (.*)', log).group(1)
                log = check_output(
                    ["./releasectl", pack.name,
                     "--dry-run", "--origin={}".format(pack.trunk_branch),
                     "--in-place",
                     "--current-version={}".format(pack.current_version),
                     "--minor", "--final"], stderr=STDOUT,
                    universal_newlines=True)
                next_version = re.search(
                    r'I: next version is (.*)', log).group(1)
                print("".center(80, '@'))
                print(" {}: (next version: {}) ".format(
                    pack.name, next_version).center(80, '@'))
                print("".center(80, '@'))
                call("perl -pi -e 's/\) UNRELEASED;/\) unstable;/g' "
                     "{}/debian/changelog".format(pack.ppa_packaging_branch),
                     shell=True)
                call('dch "Open for development (remove this message before '
                     'releasing)" -b -v {} -c {}/debian/changelog'.format(
                         next_version, pack.ppa_packaging_branch), shell=True)
                call('cd {} && bzr commit -m "Open {} for development" '
                     '--quiet'.format(pack.ppa_packaging_branch, next_version),
                     shell=True)
                call(["./releasectl", pack.name,
                      "--origin={}".format(pack.trunk_branch),
                      "--in-place",
                      "--current-version={}".format(final_version),
                      "--minor", "--dev", "--tagging-policy=never"])
                push_commands.append(
                    "bzr push -d {} {}".format(
                        pack.trunk_branch,
                        BRANCH_PREFIX+pack.trunk_release_branch))
                push_commands.append(
                    "bzr push -d {} {}".format(
                        pack.ppa_packaging_branch,
                        BRANCH_PREFIX+pack.ppa_packaging_release_branch))
                build_commands.append(
                    "./lp-recipe-update-build --recipe {} {} -n {}".format(
                        pack.stable_recipe,
                        BRANCH_PREFIX+pack.trunk_branch, final_version))
                merge_commands.append(
                    "./lp-propose-merge -p {} -t {}".format(
                        BRANCH_PREFIX+pack.trunk_release_branch,
                        BRANCH_PREFIX+pack.trunk_branch))
                merge_commands.append(
                    "./lp-propose-merge -p {} -t {}".format(
                        BRANCH_PREFIX+pack.ppa_packaging_release_branch,
                        BRANCH_PREFIX+pack.ppa_packaging_branch))
                release_milestone_commands.append(
                    "./lp-release-milestone {} -m {}".format(
                        pack.project,
                        final_version))
        push_commands = set(push_commands)
        build_commands = set(build_commands)
        merge_commands = set(merge_commands)
        sdist_commands = set(sdist_commands)
        twine_commands = set(twine_commands)
        release_milestone_commands = set(release_milestone_commands)
        print("".center(80, '#'))
        print(" 1. Push the following release branch(es) to launchpad:")
        print("".center(80, '#'))
        for command in push_commands:
            print(command)
        print("".center(80, '#'))
        print(" 2. Propose to merge back into trunk the release branch(es):")
        print("".center(80, '#'))
        for command in merge_commands:
            print(command)
        print("".center(80, '#'))
        print(" 3. Kick off the PPA stable builds:")
        print("".center(80, '#'))
        for command in build_commands:
            print(command)
        print("".center(80, '#'))
        print(" 4. Release the current milestone(s):")
        print("".center(80, '#'))
        for command in release_milestone_commands:
            print(command)
        print("".center(80, '#'))
        print(" 5. Upload the source tarballs to LP:")
        print("".center(80, '#'))
        for command in sdist_commands:
            print(command)
        if not args.cdts:
            print("".center(80, '#'))
            print(" 6. Upload the source tarballs to PyPI:")
            print("".center(80, '#'))
            for command in twine_commands:
                print(command)
        print("".center(80, '#'))
        print(" 7. Trunk and packaging-branch changelogs are in logs/")
        print("".center(80, '#'))
    else:  # testing mode

        for pack in packages:
            if not os.path.exists(pack.trunk_branch):
                call(["bzr", "branch", "--quiet",
                     BRANCH_PREFIX+pack.trunk_branch])
            if not os.path.exists(pack.ppa_packaging_branch):
                call(["bzr", "branch", "--quiet",
                     BRANCH_PREFIX+pack.ppa_packaging_branch])
            # Cache this now, as it will change as work progresses
            trunk_changelog_start_tag = packages[0].last_stable_tag_in_trunk
            if pack.release_required or pack.ppa_packaging_release_required:
                name = pack.name
                bump = "--minor"
                if name == 'checkbox-converged':
                    bump = "--micro"
                current_version = pack.last_stable_trunk_tag.replace(
                    name+"-v", "")
                log = check_output(
                    ["./releasectl", pack.name, "--dry-run",
                     "--origin={}".format(pack.trunk_branch), "--in-place",
                     "--current-version={}".format(current_version),
                     bump, "--candidate"], stderr=STDOUT,
                    universal_newlines=True)
                next_candidate = re.search(
                    r'I: next version is (.*)', log).group(1)
                print("".center(80, '#'))
                print(" {}: (current version: {}) ".format(
                    pack.name, current_version).center(80, '#'))
                print("".center(80, '#'))
                call(["./releasectl", pack.name,
                      "--origin={}".format(pack.trunk_branch),
                      "--in-place",
                      "--current-version={}".format(current_version),
                      bump, "--candidate"])
                call(["./releasectl", pack.ppa_packaging_branch,
                      "--origin={}".format(pack.ppa_packaging_branch),
                      "--in-place",
                      "--current-version={}".format(current_version),
                      bump, "--candidate"])
                push_commands.append(
                    "bzr push -d {} {}".format(
                        pack.trunk_branch,
                        BRANCH_PREFIX+pack.trunk_release_branch))
                push_commands.append(
                    "bzr push -d {} {}".format(
                        pack.ppa_packaging_branch,
                        BRANCH_PREFIX+pack.ppa_packaging_release_branch))
                build_commands.append(
                    "./lp-recipe-update-build --recipe {} {} -n {}".format(
                        pack.testing_recipe,
                        BRANCH_PREFIX+pack.trunk_release_branch,
                        next_candidate))
        push_commands = set(push_commands)
        build_commands = set(build_commands)
        print("".center(80, '#'))
        print(" 1. Push the following release branch(es) to launchpad:")
        print("".center(80, '#'))
        for command in push_commands:
            print(command)
        print("".center(80, '#'))
        print(" 2. Kick off the PPA testing builds:")
        print("".center(80, '#'))
        for command in build_commands:
            print(command)
        # Try to build logs
        create_logs(packages, trunk_changelog_start_tag, "logs/")
        print("".center(80, '#'))
        print(" 3. Trunk and packaging-branch changelogs are in logs/")
        print("".center(80, '#'))
