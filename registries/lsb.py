import re

from hwtest.lib.cache import cache

from file import FileRegistry


class LsbRegistry(FileRegistry):

    default_filename = "/etc/lsb-release"
    default_map = {
        "DISTRIB_ID": "distributor_id",
        "DISTRIB_DESCRIPTION": "description",
        "DISTRIB_RELEASE": "release",
        "DISTRIB_CODENAME": "codename"}

    def __init__(self, config, filename=None, map=None):
        super(LsbRegistry, self).__init__(config, filename)
        self.map = map or self.default_map

    @cache
    def items(self):
        items = []
        for line in self.split("\n"):
            match = re.match(r"(.*)=(.*)", line)
            if match:
                key = match.group(1)
                if key in self.map:
                    key = self.map[key]
                    value = match.group(2).strip('"')
                    items.append((key, value))

        return items


factory = LsbRegistry
