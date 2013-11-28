# -*- coding: utf-8 -*-
#
# This file is part of Checkbox.
#
# Copyright 2012 Canonical Ltd.
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
#
import configparser
import glob
import re
import unittest

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
        with open('po/POTFILES.in', 'rt') as stream:
            potfile_lines = [line.strip() for line in stream]
        potfile_jobfiles = [file for file in potfile_lines if "rfc822deb" in file]
        potfile_jobfiles = [line.split(']')[1].strip() 
                            for line in potfile_jobfiles if ']' in line]

        potfile_jobfiles = sorted(potfile_jobfiles)
        existing_files = sorted(glob.glob('jobs/*.in'))
        self.assertEqual(potfile_jobfiles, existing_files)

    def test_job_files_in_local_txt(self):
        with open('jobs/local.txt.in','rt') as stream:
            local_lines = [line.strip() for line in stream]
        local_jobfiles = [file for file in local_lines if "$CHECKBOX_SHARE/jobs" in file]
        local_jobfiles = [re.search('\$CHECKBOX_SHARE\/(?P<job_file>jobs\/(.+)\.txt)\?.*',
                          file).group('job_file')+".in" for file in local_jobfiles]

        local_jobfiles = sorted(local_jobfiles)
        existing_files = sorted(glob.glob('jobs/*.in'))
        #We need to remove local.txt.in from existing_files since it doesn't contain 
        #itself, also removing resource.txt.in which does not need
        #to be included in a suite.
        existing_files.remove("jobs/local.txt.in")
        existing_files.remove("jobs/resource.txt.in")
        self.assertEqual(local_jobfiles, existing_files)

