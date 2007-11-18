import sys
import unittest

sys.path.insert(0, "registries")
from map import MapRegistry


class MapRegistryTest(unittest.TestCase):

    def test_map(self):
        map = {'a': 1}
        registry = MapRegistry(None, map)
        self.assertTrue(registry.a)
        self.assertTrue(registry.a == 1)
        self.assertFalse(registry.b)
