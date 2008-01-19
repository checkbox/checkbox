from hwtest.registries.data import DataRegistry
from hwtest.registries.tests.helpers import TestHelper


class DataRegistryTest(TestHelper):

    def test_data(self):
        registry = DataRegistry(self.config, "foo")
        self.assertTrue(str(registry) is not None)
        self.assertTrue(str(registry) == "foo")
