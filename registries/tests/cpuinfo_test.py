import re
import sys
import unittest

sys.path.insert(0, "registries")
from cpuinfo import CpuinfoRegistry


class CpuinfoRegistryTest(unittest.TestCase):

    def test_processors(self):
        registry = CpuinfoRegistry(None)
        self.assertTrue(registry.keys() > 0)
        self.assertTrue(registry[0])

    def test_vendor_id(self):
        registry = CpuinfoRegistry(None)
        processor = registry[0]
        self.assertTrue(processor.vendor_id)
