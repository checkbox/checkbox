import sys
import unittest

sys.path.insert(0, "registries")
from data import DataRegistry


class DataRegistryTest(unittest.TestCase):

    def test_data(self):
        registry = DataRegistry(None, "foo")
        self.assertTrue(str(registry) is not None)
        self.assertTrue(str(registry) == "foo")
