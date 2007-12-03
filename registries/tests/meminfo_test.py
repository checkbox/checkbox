import re
import sys
import unittest

sys.path.insert(0, "registries")
from meminfo import MeminfoRegistry


class MeminfoRegistryTest(unittest.TestCase):

    def test_mem_total(self):
        registry = MeminfoRegistry(None)
        self.assertTrue(registry["MemTotal"] is not None)
        self.assertTrue(registry["MemTotal"] > 0)
