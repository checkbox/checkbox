from hwtest.registries.tests.helpers import TestHelper

from registries.lsb import LsbRegistry


class LsbRegistryTest(TestHelper):

    def test_keys(self):
        registry = LsbRegistry(self.config)
        self.assertTrue(registry.distributor_id)
        self.assertTrue(registry.description)
        self.assertTrue(registry.release)
        self.assertTrue(registry.codename)
