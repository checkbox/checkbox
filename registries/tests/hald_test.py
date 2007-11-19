import re
import sys
import unittest

sys.path.insert(0, "registries")
from hald import HaldRegistry


class HaldRegistryTest(unittest.TestCase):

    def test_version(self):
        registry = HaldRegistry(None)
        self.assertTrue(registry.version)
        self.assertTrue(re.search(r"^[\d\.]+$", registry.version))
