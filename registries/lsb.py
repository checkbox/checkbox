import re

from hwtest.lib.cache import cache

from command import CommandRegistry


class LsbRegistry(CommandRegistry):
    """Registry for LSB information.

    Each item contained in this registry consists of the information
    returned by the lsb_release command.
    """

    default_command = "lsb_release -a"
    default_map = {
        "Distributor ID": "distributor_id",
        "Description": "description",
        "Release": "release",
        "Codename": "codename"}

    def __init__(self, config, filename=None, map=None):
        super(LsbRegistry, self).__init__(config, filename)
        self.map = map or self.default_map

    @cache
    def items(self):
        items = []
        for line in [l for l in self.split("\n") if l]:
            (key, value) = line.split(":\t", 1)
            if key in self.map:
                key = self.map[key]
                items.append((key, value))

        return items


factory = LsbRegistry
