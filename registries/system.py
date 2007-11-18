import md5

from hwtest.registry import Registry
from hwtest.lib.cache import cache

from hal import HalRegistry


class SystemRegistry(Registry):

    @cache
    def __str__(self):
        hal_registry = HalRegistry(None)

        fingerprint = md5.new()
        fingerprint.update(hal_registry.computer.system.vendor)
        fingerprint.update(hal_registry.computer.system.product)
        return fingerprint.hexdigest()

    def items(self):
        return [("id", str(self))]


factory = SystemRegistry
