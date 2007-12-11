import re

from registries.system import SystemRegistry
from registries.tests.helpers import TestHelper


class SystemRegistryTest(TestHelper):

    def test_key(self):
        registry = SystemRegistry(self.config)
        self.assertTrue(registry.key)
        self.assertTrue(re.search(r"^[\w]+$", registry.key))
