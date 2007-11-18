# The apt API not stable yet, so this filters warnings
import warnings
warnings.filterwarnings(action='ignore', category=FutureWarning)

# Importing from the cache module is expensive, so this delays the call
# until absolutely necessary
from apt.cache import Cache

from hwtest.registry import Registry
from hwtest.lib.cache import cache


class PackageRegistry(Registry):

    default_attributes = ["name", "priority", "section", "source",
        "version", "installed_size", "size", "summary"]

    def __init__(self, config, package, attributes=None):
        super(PackageRegistry, self).__init__(config)
        self.package = package
        self.attributes = attributes or self.default_attributes

    def __str__(self):
        strings = []
        for attr in self.attributes:
            key = attr.capitalize()
            value = getattr(self.package, attr)
            strings.append("%s: %s" % (key, value))

        return "\n".join(strings)

    @cache
    def items(self):
        items = []
        for key in self.attributes:
            value = getattr(self.package, key)
            items.append((key, value))

        return items


class PackageManagerRegistry(Registry):

    default_cache_factory = Cache

    def __init__(self, config, cache_factory=None):
        super(PackageManagerRegistry, self).__init__(config)
        self.cache_factory = cache_factory or self.default_cache_factory

    def __str__(self):
        strings = []
        for package in self:
            strings.append("%s - %s" % (self["name"], self["summary"]))
        return "\n".join(strings)

    @cache
    def items(self):
        items = []
        for package in self.cache_factory():
            if package.isInstalled:
                key = package.name
                value = PackageRegistry(self.config, package)
                items.append((key, value))

        return items


factory = PackageManagerRegistry
