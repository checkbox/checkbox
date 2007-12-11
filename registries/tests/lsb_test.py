from registries.lsb import LsbRegistry
from registries.tests.helpers import TestHelper


class LsbRegistryTest(TestHelper):

    def test_keys(self):
        registry = LsbRegistry(self.config)
        self.assertTrue(registry.distributor_id)
        self.assertTrue(registry.description)
        self.assertTrue(registry.release)
        self.assertTrue(registry.codename)
