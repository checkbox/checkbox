from hwtest.registries.command import CommandRegistry
from hwtest.registries.tests.helpers import TestHelper


class CommandRegistryTest(TestHelper):

    def test_command(self):
        registry = CommandRegistry(self.config, "echo -n foo")
        self.assertTrue(str(registry) is not None)
        self.assertTrue(str(registry) == "foo")
