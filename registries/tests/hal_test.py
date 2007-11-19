import re
import sys
import unittest

sys.path.insert(0, "registries")
from hal import HalRegistry


class HalRegistryTest(unittest.TestCase):

    def test_system_vendor(self):
        registry = HalRegistry(None)
        self.assertTrue(registry.computer.system.vendor is not None)
