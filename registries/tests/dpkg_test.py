import re

from hwtest.registries.tests.helpers import TestHelper

from registries.dpkg import DpkgRegistry


class DpkgRegistryTest(TestHelper):

    def test_version(self):
        registry = DpkgRegistry(self.config)
        self.assertTrue(registry.version)
        self.assertTrue(re.search(r"^[\d\.]+$", registry.version))

    def test_architecture(self):
        registry = DpkgRegistry(self.config)
        self.assertTrue(registry.architecture)
