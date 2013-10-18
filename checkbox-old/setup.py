#!/usr/bin/env python3

import os
import re
import errno
import posixpath
import subprocess
from glob import glob

from setuptools import setup, find_packages

from distutils.ccompiler import new_compiler
from distutils.command.build import build
from distutils.command.clean import clean
from distutils.command.install_data import install_data
from distutils.command.install_scripts import install_scripts
try:
    from DistUtilsExtra.command.build_extra import build_extra
    from DistUtilsExtra.command.build_i18n import build_i18n
    from DistUtilsExtra.command.build_icons import build_icons
except ImportError:
    from distutils.cmd import Command

    class build_extra(build):
        """Adds fake support for i18n and icons to the build target."""
        def __init__(self, dist):
            build.__init__(self, dist)
            self.user_options.extend([("i18n", None, "use the localisation"),
                                      ("icons", None, "use icons"),
                                     ])

        def initialize_options(self):
            build.initialize_options(self)
            self.i18n = False
            self.icons = False

    class build_i18n(Command):
        """Placeholder concrete class for fake i18n support."""

    class build_icons(Command):
        """Placeholder concrete class for fake icons support."""


DATA_FILES = [
    ("share/checkbox/", ["backend", "run"]),
    ("share/checkbox/data/audio/", ["data/audio/*"]),
    ("share/checkbox/data/documents/", ["data/documents/*"]),
    ("share/checkbox/data/images/", ["data/images/*.*"]),
    ("share/checkbox/data/images/oem-config",
        ["data/images/oem-config/*"]),
    ("share/checkbox/data/video/", ["data/video/*"]),
    ("share/checkbox/data/settings/", ["data/settings/*"]),
    ("share/checkbox/data/websites/", ["data/websites/*"]),
    ("share/checkbox/data/whitelists/", ["data/whitelists/*.*"]),
    ("share/checkbox/data/whitelists/certification/",
        ["data/whitelists/certification/*.*"]),
    ("share/checkbox/examples/", ["examples/*"]),
    ("share/checkbox/install/", ["install/*"]),
    ("share/checkbox/patches/", ["patches/*"]),
    ("share/checkbox/plugins/", ["plugins/*.py"]),
    ("share/plainbox-providers-1/", ["providers-1/*"]),
    ("share/checkbox/report/", ["report/*.*"]),
    ("share/checkbox/report/images/", ["report/images/*"]),
    ("share/checkbox/scripts/", ["scripts/*"]),
    ("share/dbus-1/services/", ["qt/com.canonical.QtCheckbox.service"]),
    ("share/apport/package-hooks/", ["apport/source_checkbox.py"]),
    ("share/apport/general-hooks/", ["apport/checkbox.py"])]


def changelog_version(changelog="debian/changelog"):
    version = "dev"
    if posixpath.exists(changelog):
        head = open(changelog).readline()
        match = re.compile(".*\((.*)\).*").match(head)
        if match:
            version = match.group(1)

    return version


def expand_data_files(data_files):
    for f in data_files:
        if type(f) != str:
            files = f[1]
            i = 0
            while i < len(files):
                if files[i].find("*") > -1:
                    for e in glob(files[i]):
                        files.append(e)
                    files.pop(i)
                    i -= 1
                i += 1

    return data_files


def extract_sources_from_data_files(data_files):
    all_sources = []
    data_files = expand_data_files(data_files)
    for destination, sources in data_files:
        all_sources.extend([s for s in sources if s.endswith(".c")])

    return all_sources


def extract_executables_from_data_files(data_files):
    sources = extract_sources_from_data_files(data_files)
    return [os.path.splitext(s)[0] for s in sources]


def substitute_variables(infile, outfile, variables={}):
    file_in = open(infile, "r")
    file_out = open(outfile, "w")
    for line in file_in.readlines():
        for key, value in variables.items():
            line = line.replace(key, value)
        file_out.write(line)


class checkbox_build(build_extra, object):

    def initialize_options(self):
        super(checkbox_build, self).initialize_options()

        self.sources = []

    def finalize_options(self):
        super(checkbox_build, self).finalize_options()

        # Initialize sources
        data_files = self.distribution.data_files
        self.sources = extract_sources_from_data_files(data_files)

    def run(self):
        # This should always work when building a Debian package.
        if os.path.exists("/usr/bin/qmake-qt4"):
            retval = subprocess.call(
                "(cd qt/frontend; qmake-qt4; make)", shell=True)
            if retval:
                raise SystemExit(retval)

            DATA_FILES.append(("lib/checkbox/qt/",
              ["qt/frontend/checkbox-qt-service"]))

        super(checkbox_build, self).run()

        cc = new_compiler()
        for source in self.sources:
            executable = os.path.splitext(source)[0]
            cc.link_executable(
                [source], executable, libraries=["rt", "pthread"],
                # Enforce security with dpkg-buildflags --get CFLAGS
                extra_preargs=[
                    "-g", "-O2", "-fstack-protector",
                    "--param=ssp-buffer-size=4", "-Wformat",
                    "-Werror=format-security"])


class checkbox_clean(clean, object):

    def initialize_options(self):
        super(checkbox_clean, self).initialize_options()

        self.executables = None

    def finalize_options(self):
        super(checkbox_clean, self).finalize_options()

        # Initialize sources
        data_files = self.distribution.data_files
        self.executables = extract_executables_from_data_files(data_files)

    def run(self):
        super(checkbox_clean, self).run()

        for executable in self.executables:
            try:
                os.unlink(executable)
            except OSError as error:
                if error.errno != errno.ENOENT:
                    raise


class checkbox_install_data(install_data, object):

    def finalize_options(self):
        """Add wildcard support for filenames."""
        super(checkbox_install_data, self).finalize_options()

        for f in self.data_files:
            if type(f) != str:
                files = f[1]
                i = 0
                while i < len(files):
                    if "*" in files[i]:
                        for e in glob(files[i]):
                            files.append(e)
                        files.pop(i)
                        i -= 1
                    i += 1

    def run(self):
        """Run substitutions on files."""
        super(checkbox_install_data, self).run()

        examplesfiles = [o for o in self.outfiles if "examples" in o]
        if not examplesfiles:
            return

        # Create etc directory
        if self.install_dir == "/usr":
            basedir = posixpath.sep
        else:
            basedir = self.install_dir
        etcdir = posixpath.join(basedir, "etc", "checkbox.d")
        self.mkpath(etcdir)

        # Create configs symbolic link
        dstdir = posixpath.dirname(examplesfiles[0]).replace("examples",
            "configs")
        if not os.path.exists(dstdir):
            os.symlink(etcdir, dstdir)

        # Substitute version in examplesfiles and etcfiles
        version = changelog_version()
        for examplesfile in examplesfiles:
            etcfile = posixpath.join(etcdir,
                posixpath.basename(examplesfile))
            infile = posixpath.join("examples",
                posixpath.basename(examplesfile))
            for outfile in examplesfile, etcfile:
                substitute_variables(infile, outfile, {
                    "version = dev": "version = %s" % version})


class checkbox_install_scripts(install_scripts, object):

    def run(self):
        """Run substitutions on files."""
        super(checkbox_install_scripts, self).run()

        # Substitute directory in defaults.py
        for outfile in self.outfiles:
            infile = posixpath.join("bin", posixpath.basename(outfile))
            substitute_variables(infile, outfile, {
                "CHECKBOX_SHARE:-.": "CHECKBOX_SHARE:-/usr/share/checkbox",
                "CHECKBOX_DATA:-.": "CHECKBOX_DATA:-$XDG_CACHE_HOME/checkbox"})


class checkbox_build_icons(build_icons, object):

    def initialize_options(self):
        super(checkbox_build_icons, self).initialize_options()

        self.icon_dir = "icons"


setup(
    name="checkbox",
    version=changelog_version(),
    author="Marc Tardif",
    author_email="marc.tardif@canonical.com",
    license="GPL",
    description="Checkbox System Testing",
    long_description="""
This project provides an extensible interface for system testing.
""",
    data_files=DATA_FILES,
    test_suite='checkbox.tests.test_suite',
    entry_points={
        'plainbox.parsers': [
            "pactl-list=checkbox.parsers.pactl:parse_pactl_output",
            "udevadm=checkbox.parsers.udevadm:parse_udevadm_output",
        ],
    },
    scripts=[
        "bin/checkbox-cli", "bin/checkbox-qt", "bin/checkbox-hw-collection"],
    packages=find_packages(),
    package_data={
        "": ["cputable"]},
    cmdclass={
        "build": checkbox_build,
        "build_i18n": build_i18n,
        "build_icons": checkbox_build_icons,
        "clean": checkbox_clean,
        "install_data": checkbox_install_data,
        "install_scripts": checkbox_install_scripts}
)
