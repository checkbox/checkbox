import types

from hwtest.lib.cache import cache
from hwtest.registry import Registry


class MapRegistry(Registry):

    def __init__(self, config, map={}):
        super(MapRegistry, self).__init__(config)
        self.map = map

    @cache
    def items(self):
        items = []
        for key, value in self.map.items():
            if type(value) is types.DictType:
                value = MapRegistry(self.config, value)

            items.append((key, value))

        return items


factory = MapRegistry
