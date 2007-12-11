from registries.cpuinfo import CpuinfoRegistry
from registries.tests.helpers import TestHelper


class CpuinfoRegistryTest(TestHelper):

    def test_processors(self):
        registry = CpuinfoRegistry(self.config)
        self.assertTrue(registry.keys() > 0)
        self.assertTrue(registry[0])

    def test_vendor_id(self):
        registry = CpuinfoRegistry(self.config)
        processor = registry[0]
        self.assertTrue(processor.vendor_id)
