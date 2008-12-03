#!/usr/bin/env python

import os
import re
import posixpath
from glob import glob

from distutils.core import setup
from distutils.util import change_root, convert_path

from distutils.command.install_data import install_data
from distutils.command.install_scripts import install_scripts
from DistUtilsExtra.command.build_extra import build_extra
from DistUtilsExtra.command.build_i18n import build_i18n


def changelog_version(changelog="debian/changelog"):
    version = "dev"
    if posixpath.exists(changelog):
        head=open(changelog).readline()
        match = re.compile(".*\((.*)\).*").match(head)
        if match:
            version = match.group(1)

    return version

def substitute_variables(infile, outfile, variables={}):
    file_in = open(infile, "r")
    file_out = open(outfile, "w")
    for line in file_in.readlines():
        for key, value in variables.items():
            line = line.replace(key, value)
        file_out.write(line)


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
        etcdir = convert_path("/etc/checkbox.d")
        if not posixpath.isabs(etcdir):
            etcdir = posixpath.join(self.install_dir, etcdir)
        elif self.root:
            etcdir = change_root(self.root, etcdir)
        self.mkpath(etcdir)

        # Create configs symbolic link
        dstdir = posixpath.dirname(examplesfiles[0]).replace("examples",
            "configs")
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
                "CHECKBOX_DATA:-.": "CHECKBOX_DATA:-/var/lib/checkbox"})


setup(
    name = "checkbox",
    version = changelog_version(),
    author = "Marc Tardif",
    author_email = "marc.tardif@canonical.com",
    license = "GPL",
    description = "Checkbox System Testing",
    long_description = """
This project provides an extensible interface for system testing. The
results can then be sent to Launchpad.
""",
    data_files = [
        ("share/pixmaps/", ["gtk/checkbox-gtk.xpm"]),
        ("share/checkbox/", ["run"]),
        ("share/checkbox/data/", ["data/*"]),
        ("share/checkbox/examples/", ["examples/*"]),
        ("share/checkbox/install/", ["install/*"]),
        ("share/checkbox/plugins/", ["plugins/*.py"]),
        ("share/checkbox/registries/", ["registries/*.py"]),
        ("share/checkbox/scripts/", ["scripts/*"]),
        ("share/checkbox/gtk/", ["gtk/checkbox-gtk.glade", "gtk/*.png"])],
    scripts = ["bin/checkbox-gtk", "bin/checkbox-cli"],
    packages = ["checkbox", "checkbox.contrib", "checkbox.lib", "checkbox.reports",
        "checkbox.registries", "checkbox_cli", "checkbox_gtk"],
    cmdclass = {
        "install_data": checkbox_install_data,
        "install_scripts": checkbox_install_scripts,
        "build" : build_extra,
        "build_i18n" :  build_i18n }
)
