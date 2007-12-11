from registries.meminfo import MeminfoRegistry
from registries.tests.helpers import TestHelper


class MeminfoRegistryTest(TestHelper):

    def test_mem_total(self):
        registry = MeminfoRegistry(self.config)
        self.assertTrue(registry["MemTotal"] is not None)
        self.assertTrue(registry["MemTotal"] > 0)
