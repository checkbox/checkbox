# -*- coding: utf-8 -*-
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
from io import StringIO

from unittest import TestCase

from checkbox.parsers.description import (
    DescriptionParser,
    PURPOSE_RE,
    STEPS_RE,
    )


class DescriptionResult:

    purpose = None
    steps = None
    verification = None
    info = None

    def setDescription(self, purpose, steps, verification, info):
        self.purpose = purpose
        self.steps = steps
        self.verification = verification
        self.info = info


class TestPurposeRe(TestCase):

    def test_one_line(self):
        line = PURPOSE_RE.sub(r"", "1. foo\n")
        self.assertEqual(line, "foo\n")

    def test_two_lines(self):
        line = PURPOSE_RE.sub(r"", "1. foo\n2. bar\n")
        self.assertEqual(line, "foo\nbar\n")


class TestStepsRe(TestCase):

    def test_one_line(self):
        line = STEPS_RE.sub(r"\1.\2", "1: foo\n")
        self.assertEqual(line, "1. foo\n")

    def test_two_lines(self):
        line = STEPS_RE.sub(r"\1.\2", "1: foo\n2: bar\n")
        self.assertEqual(line, "1. foo\n2. bar\n")


class TestDescriptionParser(TestCase):

    def getParser(self, string):
        stream = StringIO(string)
        return DescriptionParser(stream)

    def getResult(self, string):
        parser = self.getParser(string)
        result = DescriptionResult()
        parser.run(result)
        return result

    def assertResult(
        self, result, purpose=None, steps=None, verification=None, info=None):
        self.assertEqual(result.purpose, purpose)
        self.assertEqual(result.steps, steps)
        self.assertEqual(result.verification, verification)
        self.assertEqual(result.info, info)

    def test_empty(self):
        result = self.getResult("")
        self.assertEqual(result.purpose, None)

    def test_purpose(self):
        result = self.getResult("""
PURPOSE:
    foo
""")
        self.assertResult(result)

    def test_purpose_steps(self):
        result = self.getResult("""
PURPOSE:
    foo
STEPS:
    bar
""")
        self.assertResult(result)

    def test_purpose_steps_verification(self):
        result = self.getResult("""
PURPOSE:
    foo
STEPS:
    bar
VERIFICATION:
    baz
""")
        self.assertResult(result, "foo\n", "bar\n", "baz\n")

    def test_purpose_steps_info_verification(self):
        result = self.getResult("""
PURPOSE:
    foo
STEPS:
    bar
INFO:
    $output
VERIFICATION:
    baz
""")
        self.assertResult(result, "foo\n", "bar\n", "baz\n", "$output\n")

    def test_purpose_steps_verification_other(self):
        result = self.getResult("""
PURPOSE:
    foo
STEPS:
    bar
VERIFICATION:
    baz
OTHER:
    blah
""")
        self.assertResult(result)

    def test_es(self):
        result = self.getResult("""
PROPÓSITO:
     Esta prueba verifica los diferentes modos de vídeo detectados
PASOS:
     1. Se han detectado las siguientes pantallas y modos de vídeo
INFORMACIÓN:
     $ salida
VERIFICACIÓN:
     ¿Son las pantallas y los modos de vídeo correctos?
""")
        self.assertNotEqual(result.purpose, None)
        self.assertNotEqual(result.steps, None)
        self.assertNotEqual(result.verification, None)
        self.assertEqual(result.info, "$output\n")

    def test_ru(self):
        result = self.getResult("""
ЦЕЛЬ:
    Эта проверка позволит убедиться в работоспособности штекера наушников
ДЕЙСТВИЯ:
    1. Подсоедините наушники к вашему звуковому устройству
    2. Щёлкните кнопку Проверить для воспроизведения звукового сигнала через звуковое устройство
ПРОВЕРКА:
    Был ли слышен звук в наушниках и был ли он воспроизведён в ваших наушниках без искажений, щелчков или других искажённых звуков?"
""")
        self.assertNotEqual(result.purpose, None)
        self.assertNotEqual(result.steps, None)
        self.assertNotEqual(result.verification, None)
        self.assertEqual(result.info, None)

    def test_substitute_purpose(self):
        result = self.getResult("""
PURPOSE:
    1. foo
STEPS:
    bar
VERIFICATION:
    baz
""")
        self.assertResult(result, "foo\n", "bar\n", "baz\n")

    def test_substitute_steps(self):
        result = self.getResult("""
PURPOSE:
    foo
STEPS:
    1: bar
VERIFICATION:
    baz
""")
        self.assertResult(result, "foo\n", "1. bar\n", "baz\n")
