import re

from registries.hald import HaldRegistry
from registries.tests.helpers import TestHelper


class HaldRegistryTest(TestHelper):

    def test_version(self):
        registry = HaldRegistry(self.config)
        self.assertTrue(registry.version)
        self.assertTrue(re.search(r"^[\d\.]+$", registry.version))
