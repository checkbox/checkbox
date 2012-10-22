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
import unittest

from checkbox.job import Job


class JobTest(unittest.TestCase):

    def test_command_not_found(self):
        job = Job('xwonkt', '', 10)
        status, data, duration = job.execute()
        #data is expected to be bytes
        self.assertTrue(isinstance(data, bytes))

    def test_existing_command(self):
        test_string = 'checkbox'
        job = Job('echo -n "%s"' % test_string, '', 10)
        status, data, duration = job.execute()
        #data is expected to be bytes
        self.assertTrue(isinstance(data, bytes))
        self.assertEquals(data, test_string.encode())
