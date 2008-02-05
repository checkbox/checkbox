# The apt API not stable yet, so this filters warnings
import warnings
warnings.filterwarnings(action='ignore', category=FutureWarning)

# Importing from the cache module is expensive, so this delays the call
# until absolutely necessary
from apt.cache import Cache

from hwtest.lib.cache import cache

from hwtest.registry import Registry


class PackageRegistry(Registry):

    attribute_map = {
        "name": "name",
        "priority": "priority",
        "section": "section",
        "summary": "summary",
        "installedSize": "size",
        "installedVersion": "version"}

    def __init__(self, config, package):
        super(PackageRegistry, self).__init__(config)
        self.package = package

    def _attribute_to_string(self, attribute):
        key = attribute.capitalize()
        value = getattr(self.package, attribute)
        return "%s: %s" % (key, value)

    def __str__(self):
        strings = []
        for attribute, name in self.attribute_map.items():
            value = getattr(self.package, attribute)
            strings.append("%s: %s" % (name, value))

        return "\n".join(strings)

    @cache
    def items(self):
        items = []
        for attribute, name in self.attribute_map.items():
            value = getattr(self.package, attribute)
            items.append((name, value))

        return items


class PackagesRegistry(Registry):

    def __str__(self):
        strings = []
        for package in self:
            strings.append("%s - %s" % (self["name"], self["summary"]))

        return "\n".join(strings)

    @cache
    def items(self):
        items = []
        for package in Cache():
            if package.isInstalled:
                key = package.name
                value = PackageRegistry(None, package)
                items.append((key, value))

        return items


factory = PackagesRegistry
