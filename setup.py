#!/usr/bin/env python

import os
import sys
from glob import glob
from ConfigParser import ConfigParser

from distutils import sysconfig
from distutils.core import setup
from distutils.command import install_data


config = ConfigParser()
config.read("examples/hwtest.conf")
config_directory = '/etc/hwtest.d'


class hwtest_install_data(install_data.install_data, object):

    def finalize_options(self):
        """Add wildcard support for filenames.  Generate defaults.py"""
        super(hwtest_install_data, self).finalize_options()

        for f in self.data_files:
            if type(f) != str:
                files = f[1]
                i = 0
                while i < len(files):
                    if files[i].find('*') > -1:
                        for e in glob(files[i]):
                            files.append(e)
                        files.pop(i)
                        i -= 1
                    i += 1

        if os.geteuid():
            sys.stderr.write("Warning, uid!=0, not writing defaults.py\n")
            return

        defaults_in = 'hwtest/defaults.py'
        defaults_out = os.path.join(sysconfig.get_python_lib(), defaults_in)
        if self.root:
            root = self.root
            if root.endswith('/'):
                root = root.rstrip('/')

            defaults_out = os.path.normpath(defaults_out)
            if os.path.isabs(defaults_out):
                defaults_out = defaults_out[1:]
            defaults_out = os.path.join(root, defaults_out)

        f_in = file("%s.in" % defaults_in, "r")
        f_out = file(defaults_out, "w")
        for line in f_in.readlines():
            line = line.replace("@CONFIG_DIRECTORY@", config_directory)
            f_out.write(line)


setup(
    name = 'hwtest',
    version = config.defaults()["version"],
    author = 'Marc Tardif',
    author_email = 'marc.tardif@canonical.com',
    license = 'GPL',
    description = 'Hardware Test',
    long_description = '''
This project provides an interfaces for gathering hardware details
and prompting the user for tests. This information can then be sent
to Launchpad.
''',
    data_files = [
        ('share/applications/', ['gtk/hwtest-gtk.desktop']),
        ('share/pixmaps/', ['gtk/hwtest-gtk.xpm']),
        ('share/hwtest/data/', ['data/*']),
        ('share/hwtest/install/', ['install/*']),
        ('share/hwtest/plugins/', ['plugins/*.py']),
        ('share/hwtest/registries/', ['registries/*.py']),
        ('share/hwtest/questions/', ['questions/*']),
        ('share/hwtest/scripts/', ['scripts/*']),
        ('share/hwtest-gtk/', ['gtk/hwtest-gtk.glade', 'gtk/*.png'])],
    scripts = ['bin/hwtest', 'bin/hwtest-gtk', 'bin/hwtest-cli'],
    packages = ['hwtest', 'hwtest.contrib', 'hwtest.lib', 'hwtest.reports',
        'hwtest.registries', 'hwtest_cli', 'hwtest_gtk'],
    cmdclass = {
        'install_data': hwtest_install_data}
)
