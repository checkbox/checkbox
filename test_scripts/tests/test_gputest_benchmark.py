#
# This file is part of Checkbox.
#
# Copyright 2013 Canonical Ltd.
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
import imp
import os
import unittest

from tempfile import mkstemp

imp.load_source('gputest_benchmark', os.path.join(os.path.dirname(__file__),
                '..', '..', 'scripts', 'gputest_benchmark'))
from gputest_benchmark import check_log


class LogParserTest(unittest.TestCase):

    def test_logfile_not_found(self):
        file_not_found = '/a_file_with_results'
        with self.assertRaises(SystemExit) as cm:
            check_log(file_not_found)
        self.assertEqual(
            "[Errno 2] No such file or directory: "
            "'{}'".format(file_not_found),
            str(cm.exception))

    def test_logfile_with_score(self):
        fd, filename = mkstemp(text=True)
        os.close(fd)
        with open(filename, 'wt') as f:
            f.write('FurMark : init OK.\n')
            f.write('[Benchmark_Score] - module: FurMark - Score: 8 points'
                    '(800x600 windowed, duration:2000 ms).')
        self.assertFalse(check_log(filename))
        os.unlink(filename)

    def test_logfile_without_score(self):
        fd, filename = mkstemp(text=True)
        os.close(fd)
        with open(filename, 'wt') as f:
            f.write('FurMark : init OK.\n')
            f.write('[No_Score] - module: FurMark - Score: _ points'
                    '(800x600 windowed, duration:2000 ms).')
        with self.assertRaises(SystemExit) as cm:
            check_log(filename)
        self.assertEqual(
            'Benchmark score not found, check the log for errors',
            str(cm.exception))
        os.unlink(filename)

    def test_logfile_with_encoding_error(self):
        fd, filename = mkstemp()
        os.close(fd)
        with open(filename, 'wb') as f:
            f.write(b'\x80abc\n')
            f.write(b'FurMark : init OK.\n')
            f.write(b'[Benchmark_Score] - module: FurMark - Score: 116 points'
                    b'(800x600 windowed, duration:2000 ms).')
        self.assertFalse(check_log(filename))
        os.unlink(filename)
