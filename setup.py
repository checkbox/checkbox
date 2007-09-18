#!/usr/bin/env python

import os
import sys
from glob import glob
from types import StringType

from distutils.command import install_data
from distutils.core import setup
from distutils.util import change_root, convert_path

from hwtest import VERSION

project_name = 'hwtest'

# Directories
applications_subdir = os.path.join('share', 'applications')
pixmaps_subdir = os.path.join('share', 'pixmaps')
share_subdir = os.path.join('share', project_name)
gui_subdir = os.path.join(share_subdir, 'gui')
lib_subdir = os.path.join(share_subdir, 'lib')
lib_hwtest_subdir = os.path.join(lib_subdir, 'hwtest')
lib_hwtest_contrib_subdir = os.path.join(lib_hwtest_subdir, 'contrib')
lib_hwtest_lib_subdir = os.path.join(lib_hwtest_subdir, 'lib')
lib_hwtest_plugins_subdir = os.path.join(lib_hwtest_subdir, 'plugins')

class my_install_data (install_data.install_data, object):
    def finalize_options (self):
        """Add wildcard support for filenames.  Generate hwtest"""
        script_file = os.path.join('bin', 'hwtest')
        super(my_install_data, self).finalize_options()
        for f in self.data_files:
            if type(f) != StringType:
                files = f[1]
                i = 0
                while i < len(files):
                    if files[i][0].find('*') > -1:
                        for e in glob(files[i][0]):
                            files.append((e, files[i][1]))
                        files.pop(i)
                        i -= 1
                    i += 1

        if os.geteuid():
            sys.stderr.write("Warning, uid!=0, not writing hwtest\n")
            return

        share_dir = os.path.join(self.install_dir, share_subdir)
        hwtest_script = os.path.join(self.install_dir, 'bin', 'hwtest')
        if self.root:
            root = self.root
            if root.endswith(os.sep):
                root = root.rstrip(os.sep)

            share_dir = share_dir.replace(root, '')
            hwtest_script = hwtest_script.replace(root, '')

            hwtest_script = os.path.normpath(hwtest_script)
            if os.path.isabs(hwtest_script):
                hwtest_script = hwtest_script[1:]
            hwtest_script = os.path.join(root, hwtest_script)

        os.makedirs(os.path.dirname(hwtest_script), 0755)
        f_in = file("%s.in" % script_file, "r")
        f_out = file(hwtest_script, "w")
        for line in f_in.readlines():
            line = line.replace("@SHARE_DIR@", share_dir)
            f_out.write(line)

        f_in.close()
        f_out.close()
        os.chmod(hwtest_script, 0755)

    def run (self):
        self.mkpath(self.install_dir)
        for f in self.data_files:
            # it's a tuple with dict to install to and a list of files
            tdict = f[0]
            dir = convert_path(tdict['path'])
            if not os.path.isabs(dir):
                dir = os.path.join(self.install_dir, dir)
            elif self.root:
                dir = change_root(self.root, dir)
            self.mkpath(dir)
            os.chmod(dir, tdict['mode'])

            if not f[1]:
                # If there are no files listed, the user must be
                # trying to create an empty directory, so add the
                # directory to the list of output files.
                self.outfiles.append(dir)
            else:
                # Copy files, adding them to the list of output files.
                for data, mode in f[1]:
                    data = convert_path(data)
                    (out, _) = self.copy_file(data, dir)
                    self.outfiles.append(out)
                    os.chmod(out, mode)

setup(
    name = project_name,
    version = VERSION,
    author = 'Marc Tardif',
    author_email = 'marc.tardif@canonical.com',
    license = 'GPL',
    description = 'Self Certification',
    long_description = '''
Tool to perform hardware certification.
''',
    data_files = [
        ({'path': applications_subdir,
          'mode': 0755},
         [('hwtest.desktop', 0644)]),
        ({'path': pixmaps_subdir,
          'mode': 0755},
         [('hwtest.xpm', 0644)]),
        ({'path': share_subdir,
          'mode': 0755},
         [('questions.txt', 0644)]),
        ({'path': gui_subdir,
          'mode': 0755},
         [('gui/*', 0644)]),
        ({'path': lib_subdir,
          'mode': 0755},
         []),
        ({'path': lib_hwtest_subdir,
          'mode': 0755},
         [('hwtest/*.py', 0664)]),
        ({'path': lib_hwtest_contrib_subdir,
          'mode': 0755},
         [('hwtest/contrib/*.py', 0664)]),
        ({'path': lib_hwtest_lib_subdir,
          'mode': 0755},
         [('hwtest/lib/*.py', 0664)]),
        ({'path': lib_hwtest_plugins_subdir,
          'mode': 0755},
         [('hwtest/plugins/*.py', 0664)])],
    cmdclass = {
        'install_data': my_install_data}
)
