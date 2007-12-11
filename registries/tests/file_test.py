from registries.file import FileRegistry
from registries.tests.helpers import TestHelper


class FileRegistryTest(TestHelper):

    def test_file(self):
        registry = FileRegistry(self.config, "test")
        self.assertTrue(str(registry) is not None)
        self.assertTrue(len(str(registry)) > 0)
