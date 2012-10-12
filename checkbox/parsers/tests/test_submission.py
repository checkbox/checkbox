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
import os
import gzip

from unittest import TestCase

from checkbox.parsers.submission import SubmissionParser


class SubmissionRun:

    def __init__(self, result=None):
        if result is None:
            self.result = {}
        else:
            self.result = result

    def setArchitectureState(self, architecture_state):
        self.result["architecture_state"] = architecture_state

    def setDistribution(self, **distribution):
        self.result["distribution"] = distribution

    def setMemoryState(self, **memory_state):
        self.result["memory_state"] = memory_state

    def setProcessorState(self, **processor_state):
        self.result["processor_state"] = processor_state

    def addAttachment(self, **attachment):
        self.result.setdefault("attachments", [])
        self.result["attachments"].append(attachment)

    def addDeviceState(self, **device_state):
        self.result.setdefault("device_states", [])
        self.result["device_states"].append(device_state)

    def addPackageVersion(self, **package_version):
        self.result.setdefault("package_versions", [])
        self.result["package_versions"].append(package_version)

    def addTestResult(self, **test_result):
        self.result.setdefault("test_results", [])
        self.result["test_results"].append(test_result)


class TestSubmissionParser(TestCase):

    def getFixture(self, name):
        return os.path.join(os.path.dirname(__file__), "fixtures", name)

    def getParser(self, name):
        fixture = self.getFixture(name)
        if name.endswith(".gz"):
            stream = gzip.open(fixture)
        else:
            stream = open(fixture, encoding="utf-8")
        return SubmissionParser(stream)

    def getResult(self, name):
        result = {}
        parser = self.getParser(name)
        parser.run(SubmissionRun, result=result)
        return result

    def test_distribution(self):
        """The submission should contain distribution with release,
        codename, distributor_id and description.
        """
        result = self.getResult("submission.xml.gz")
        self.assertTrue("distribution" in result)
        self.assertEquals(result["distribution"]["release"], "12.10")
        self.assertEquals(result["distribution"]["codename"], "quantal")
        self.assertEquals(result["distribution"]["distributor_id"], "Ubuntu")
        self.assertEquals(
            result["distribution"]["description"],
            "Ubuntu quantal (development branch)")

    def test_memory_state(self):
        """The submission should contain memory state with total and swap."""
        result = self.getResult("submission.xml.gz")
        self.assertTrue("memory_state" in result)
        self.assertEquals(result["memory_state"]["total"], 2023460864)
        self.assertEquals(result["memory_state"]["swap"], 2067787776)

    def test_processor_state(self):
        """The submission should contain processor state with bogomips,
        cache, count, make, model, model_number, model_revision,
        model_version, other, platform_name, speed.
        """
        result = self.getResult("submission.xml.gz")
        self.assertTrue("processor_state" in result)
        self.assertEquals(result["processor_state"]["bogomips"], 4788)
        self.assertEquals(result["processor_state"]["cache"], 3145728)
        self.assertEquals(result["processor_state"]["count"], 4)
        self.assertEquals(result["processor_state"]["make"], "GenuineIntel")
        self.assertEquals(
            result["processor_state"]["model"],
            "Intel(R) Core(TM) i5 CPU       M 520  @ 2.40GHz")
        self.assertEquals(result["processor_state"]["model_number"], "6")
        self.assertEquals(result["processor_state"]["model_revision"], "2")
        self.assertEquals(
            result["processor_state"]["other"],
            """fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca """
            """cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm """
            """pbe syscall nx rdtscp lm constant_tsc arch_perfmon pebs bts """
            """rep_good nopl xtopology nonstop_tsc aperfmperf pni pclmulqdq """
            """dtes64 monitor ds_cpl vmx smx est tm2 ssse3 cx16 xtpr pdcm """
            """sse4_1 sse4_2 popcnt aes lahf_lm ida arat dtherm tpr_shadow """
            """vnmi flexpriority ept vpid""")
        self.assertEquals(result["processor_state"]["platform_name"], "x86_64")
        self.assertEquals(result["processor_state"]["speed"], 2400)

    def test_attachments(self):
        """The submission should contain 10 attachments."""
        result = self.getResult("submission.xml.gz")
        self.assertTrue("attachments" in result)
        self.assertEquals(len(result["attachments"]), 10)

    def test_device_states(self):
        """The submission should contain 82 device states."""
        result = self.getResult("submission.xml.gz")
        self.assertTrue("device_states" in result)
        self.assertEquals(len(result["device_states"]), 82)

    def test_package_versions(self):
        """The submission should contain 1460 package versions."""
        result = self.getResult("submission.xml.gz")
        self.assertTrue("package_versions" in result)
        self.assertEquals(len(result["package_versions"]), 1460)

    def test_test_results(self):
        """The submission should contain 87 test results."""
        result = self.getResult("submission.xml.gz")
        self.assertTrue("test_results" in result)
        self.assertEquals(len(result["test_results"]), 87)
