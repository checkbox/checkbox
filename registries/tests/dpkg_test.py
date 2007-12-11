import re

from registries.dpkg import DpkgRegistry
from registries.tests.helpers import TestHelper


class DpkgRegistryTest(TestHelper):

    def test_version(self):
        registry = DpkgRegistry(self.config)
        self.assertTrue(registry.version)
        self.assertTrue(re.search(r"^[\d\.]+$", registry.version))

    def test_architecture(self):
        registry = DpkgRegistry(self.config)
        self.assertTrue(registry.architecture)
