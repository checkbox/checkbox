#
# This file is part of Checkbox.
#
# Copyright 2012 Canonical Ltd.
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
#
import os
import unittest
import configparser
import glob

class SetupFiles(unittest.TestCase):

    def test_job_files_in_setup_cfg(self):
        #setup_cfg is a python config file
        config = configparser.ConfigParser()
        config.read('setup.cfg')
        #config.get returns a string, so we have to eval it and then get the second
        #element of the first element. The values are declared as an array of nested
        #tuples.
        rfc822deb_from_config = sorted(eval(config.get('build_i18n', 
                                                       'rfc822deb_files'))[0][1])
        existing_files = sorted(glob.glob('jobs/*.in'))
        self.assertEqual(rfc822deb_from_config, existing_files)

    def test_job_files_in_potfiles(self):
        potfile_lines = [line.strip() for line in open('po/POTFILES.in','r')]
        potfile_jobfiles = [file for file in potfile_lines if "rfc822deb" in file]
        potfile_jobfiles = [line.split(']')[1].strip() for line in potfile_jobfiles if ']' in line]

        potfile_jobfiles = sorted(potfile_jobfiles)
        existing_files = sorted(glob.glob('jobs/*.in'))
        print (potfile_jobfiles)
        self.assertEqual(potfile_jobfiles, existing_files)
