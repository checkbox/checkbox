import unittest

from registries.meminfo import MeminfoRegistry


class MeminfoRegistryTest(unittest.TestCase):

    def test_mem_total(self):
        registry = MeminfoRegistry()
        self.assertTrue(registry["total"] is not None)
        self.assertTrue(registry["total"] > 0)
