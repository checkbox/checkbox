# This file is part of Checkbox.
#
# Copyright 2012 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
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

"""
plainbox.impl.test_result
=========================

Test definitions for plainbox.impl.result module
"""
from tempfile import TemporaryDirectory
from unittest import TestCase
import doctest
import io

from plainbox.abc import IJobResult
from plainbox.impl.result import DiskJobResult
from plainbox.impl.result import IOLogRecord
from plainbox.impl.result import IOLogRecordReader
from plainbox.impl.result import IOLogRecordWriter
from plainbox.impl.result import MemoryJobResult
from plainbox.impl.testing_utils import make_io_log


def load_tests(loader, tests, ignore):
    tests.addTests(
        doctest.DocTestSuite('plainbox.impl.result',
                             optionflags=doctest.REPORT_NDIFF))
    return tests


class CommonTestsMixIn:

    def test_append_comments(self):
        result = self.result_cls({})
        self.assertIsNone(result.comments)
        result.append_comments("first")
        self.assertEqual(result.comments, "first")
        result.append_comments("second")
        self.assertEqual(result.comments, "first\nsecond")


class DiskJobResultTests(TestCase, CommonTestsMixIn):

    result_cls = DiskJobResult

    def setUp(self):
        self.scratch_dir = TemporaryDirectory()

    def tearDown(self):
        self.scratch_dir.cleanup()

    def test_smoke(self):
        result = DiskJobResult({})
        self.assertEqual(str(result), "None")
        self.assertEqual(repr(result), "<DiskJobResult>")
        self.assertIsNone(result.outcome)
        self.assertIsNone(result.comments)
        self.assertEqual(result.io_log, ())
        self.assertIsNone(result.return_code)
        self.assertTrue(result.is_hollow)

    def test_everything(self):
        result = DiskJobResult({
            'outcome': IJobResult.OUTCOME_PASS,
            'comments': "it said blah",
            'io_log_filename': make_io_log([
                (0, 'stdout', b'blah\n')
            ], self.scratch_dir.name),
            'return_code': 0
        })
        self.assertEqual(str(result), "pass")
        # This result contains a random vale of io_log_filename so direct repr
        # comparison is not feasable. All we want to check here is that it
        # looks right and that it has the outcome value
        self.assertTrue(repr(result).startswith("<DiskJobResult"))
        self.assertTrue(repr(result).endswith(">"))
        self.assertIn("outcome:'pass'", repr(result))
        self.assertEqual(result.outcome, IJobResult.OUTCOME_PASS)
        self.assertEqual(result.comments, "it said blah")
        self.assertEqual(result.io_log, ((0, 'stdout', b'blah\n'),))
        self.assertEqual(result.io_log_as_flat_text, 'blah\n')
        self.assertEqual(result.return_code, 0)
        self.assertFalse(result.is_hollow)

    def test_io_log_as_text_attachment(self):
        result = MemoryJobResult({
            'outcome': IJobResult.OUTCOME_PASS,
            'comments': "it said blah",
            'io_log': [(0, 'stdout', b'\x80\x456')],
            'return_code': 0
        })
        self.assertEqual(result.io_log_as_text_attachment, '')


class MemoryJobResultTests(TestCase, CommonTestsMixIn):

    result_cls = MemoryJobResult

    def test_smoke(self):
        result = MemoryJobResult({})
        self.assertEqual(str(result), "None")
        self.assertEqual(repr(result), "<MemoryJobResult>")
        self.assertIsNone(result.outcome)
        self.assertIsNone(result.comments)
        self.assertEqual(result.io_log, ())
        self.assertIsNone(result.return_code)
        self.assertTrue(result.is_hollow)

    def test_everything(self):
        result = MemoryJobResult({
            'outcome': IJobResult.OUTCOME_PASS,
            'comments': "it said blah",
            'io_log': [(0, 'stdout', b'blah\n')],
            'return_code': 0
        })
        self.assertEqual(str(result), "pass")
        self.assertEqual(
            repr(result), (
                "<MemoryJobResult comments:'it said blah' io_log:[(0, 'stdout'"
                ", b'blah\\n')] outcome:'pass' return_code:0>"))
        self.assertEqual(result.outcome, IJobResult.OUTCOME_PASS)
        self.assertEqual(result.comments, "it said blah")
        self.assertEqual(result.io_log, ((0, 'stdout', b'blah\n'),))
        self.assertEqual(result.io_log_as_flat_text, 'blah\n')
        self.assertEqual(result.return_code, 0)
        self.assertFalse(result.is_hollow)

    def test_io_log_as_text_attachment(self):
        result = MemoryJobResult({
            'outcome': IJobResult.OUTCOME_PASS,
            'comments': "it said foo",
            'io_log': [(0, 'stdout', b'foo')],
            'return_code': 0
        })
        self.assertEqual(result.io_log_as_text_attachment, 'foo')

class IOLogRecordWriterTests(TestCase):

    _RECORD = IOLogRecord(0.123, 'stdout', b'some\ndata')
    _TEXT = '[0.123,"stdout","c29tZQpkYXRh"]\n'

    def test_smoke_write(self):
        stream = io.StringIO()
        writer = IOLogRecordWriter(stream)
        writer.write_record(self._RECORD)
        self.assertEqual(stream.getvalue(), self._TEXT)
        writer.close()
        with self.assertRaises(ValueError):
            stream.getvalue()

    def test_smoke_read(self):
        stream = io.StringIO(self._TEXT)
        reader = IOLogRecordReader(stream)
        record1 = reader.read_record()
        self.assertEqual(record1, self._RECORD)
        record2 = reader.read_record()
        self.assertEqual(record2, None)
        reader.close()
        with self.assertRaises(ValueError):
            stream.getvalue()

    def test_iter_read(self):
        stream = io.StringIO(self._TEXT)
        reader = IOLogRecordReader(stream)
        record_list = list(reader)
        self.assertEqual(record_list, [self._RECORD])
