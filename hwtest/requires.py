from hwtest.lib.cache import cache

from hwtest.registry import registry_eval_recursive


class Requires(object):

    def __init__(self, source, registry):
        self._source = source
        self._registry = registry
        self._mask = [False]

    def __str__(self):
        return self.get_source() or ""

    @cache
    def get_values(self):
        if self._source is None:
            self._mask = [True]
            return []

        return registry_eval_recursive(self._registry,
            self._source, self._mask)

    def get_packages(self):
        packages = []
        values = self.get_values()
        for value in values:
            if value.__class__.__name__ == "PackageRegistry":
                packages.append(value)

        return packages

    def get_devices(self):
        devices = []
        values = self.get_values()
        for value in values:
            if value.__class__.__name__ == "DeviceRegistry":
                devices.append(value)

        return devices

    def get_source(self):
        return self._source

    def get_mask(self):
        self.get_values()
        return self._mask
