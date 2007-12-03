import re
import sys
import unittest

sys.path.insert(0, "registries")
from dpkg import DpkgRegistry


class DpkgRegistryTest(unittest.TestCase):

    def test_version(self):
        registry = DpkgRegistry(None)
        self.assertTrue(registry.version)
        self.assertTrue(re.search(r"^[\d\.]+$", registry.version))

    def test_architecture(self):
        registry = DpkgRegistry(None)
        self.assertTrue(registry.architecture)
