import re
import sys
import unittest

sys.path.insert(0, "registries")
from lsb import LsbRegistry


class LsbRegistryTest(unittest.TestCase):

    def test_keys(self):
        registry = LsbRegistry(None)
        self.assertTrue(registry.distributor_id)
        self.assertTrue(registry.description)
        self.assertTrue(registry.release)
        self.assertTrue(registry.codename)
