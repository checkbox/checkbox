from registries.map import MapRegistry
from registries.tests.helpers import TestHelper


class MapRegistryTest(TestHelper):

    def test_map(self):
        map = {'a': 1}
        registry = MapRegistry(self.config, map)
        self.assertTrue(registry.a)
        self.assertTrue(registry.a == 1)
        self.assertFalse(registry.b)
