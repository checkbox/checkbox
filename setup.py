#!/usr/bin/env python

import os
import re
from glob import glob

from distutils import sysconfig
from distutils.core import setup

from distutils.command.install_data import install_data
from distutils.command.install_scripts import install_scripts
from DistUtilsExtra.command.build_extra import build_extra
from DistUtilsExtra.command.build_i18n import build_i18n


def changelog_version(changelog="debian/changelog"):
    version = "dev"
    if os.path.exists(changelog):
        head=open(changelog).readline()
        match = re.compile(".*\((.*)\).*").match(head)
        if match:
            version = match.group(1)

    return version

def substitute_variables(infile, outfile, variables={}):
    f_in = file(infile, "r")
    f_out = file(outfile, "w")
    for line in f_in.readlines():
        for key, value in variables.items():
            line = line.replace(key, value)
        f_out.write(line)


class hwtest_install_data(install_data, object):

    def finalize_options(self):
        """Add wildcard support for filenames."""
        super(hwtest_install_data, self).finalize_options()

        for f in self.data_files:
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

    def run(self):
        """Run substitutions on files."""
        super(hwtest_install_data, self).run()

        # Substitute version in examples
        version = changelog_version()
        outfiles = [o for o in self.outfiles if o.endswith(".ini")]
        for outfile in outfiles:
            infile = os.path.join("examples", os.path.basename(outfile))
            substitute_variables(infile, outfile, {
                "version = dev": "version = %s" % version})


class hwtest_install_scripts(install_scripts, object):

    def run(self):
        """Run substitutions on files."""
        super(hwtest_install_scripts, self).run()

        # Substitute directory in defaults.py
        for outfile in self.outfiles:
            infile = os.path.join("bin", os.path.basename(outfile))
            substitute_variables(infile, outfile, {
                "HWTEST_DIRECTORY=.": "HWTEST_DIRECTORY=/usr/share/hwtest"})


setup(
    name = "hwtest",
    version = changelog_version(),
    author = "Marc Tardif",
    author_email = "marc.tardif@canonical.com",
    license = "GPL",
    description = "Hardware Test",
    long_description = """
This project provides an interfaces for gathering hardware details
and prompting the user for tests. This information can then be sent
to Launchpad.
""",
    data_files = [
        ("share/applications/", ["gtk/hwtest-gtk.desktop"]),
        ("share/pixmaps/", ["gtk/hwtest-gtk.xpm"]),
        ("share/hwtest/", ["run"]),
        ("share/hwtest/data/", ["data/*"]),
        ("share/hwtest/examples/", ["examples/*"]),
        ("share/hwtest/install/", ["install/*"]),
        ("share/hwtest/plugins/", ["plugins/*.py"]),
        ("share/hwtest/registries/", ["registries/*.py"]),
        ("share/hwtest/questions/", ["questions/*"]),
        ("share/hwtest/scripts/", ["scripts/*"]),
        ("share/hwtest/gtk/", ["gtk/hwtest-gtk.glade", "gtk/*.png"])],
    scripts = ["bin/hwtest-gtk", "bin/hwtest-cli"],
    packages = ["hwtest", "hwtest.contrib", "hwtest.lib", "hwtest.reports",
        "hwtest.registries", "hwtest_cli", "hwtest_gtk"],
    cmdclass = {
        "install_data": hwtest_install_data,
        "install_scripts": hwtest_install_scripts,
        "build" : build_extra,
        "build_i18n" :  build_i18n }
)
