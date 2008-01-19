import re

from hwtest.registries.tests.helpers import TestHelper

from registries.hald import HaldRegistry


class HaldRegistryTest(TestHelper):

    def test_version(self):
        registry = HaldRegistry(self.config)
        self.assertTrue(registry.version)
        self.assertTrue(re.search(r"^[\d\.]+$", registry.version))
