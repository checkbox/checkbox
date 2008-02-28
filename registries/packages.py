from hwtest.lib.cache import cache

from hwtest.registry import Registry
from hwtest.registries.command import CommandRegistry


COLUMNS = ["name", "version", "description"]


class PackageRegistry(Registry):

    def __init__(self, config, package):
        super(PackageRegistry, self).__init__(config)
        self.package = package

    def __str__(self):
        strings = ["%s: %s" % (k, v) for k, v in self.package.items()]

        return "\n".join(strings)

    @cache
    def items(self):
        return [(k, v) for k, v in self.package.items()]


class PackagesRegistry(CommandRegistry):
    """Registry for packages."""

    @cache
    def items(self):
        items = []
        for line in [l for l in self.split("\n") if l]:
            # Determine the lengths of dpkg columns and
            # strip status column.
            if line.startswith("+++"):
                lengths = [len(i) for i in line.split("-")]
                lengths[0] += 1
                for i in range(1, len(lengths)):
                    lengths[i] += lengths[i - 1] + 1

            # Parse information from installed packages.
            if line.startswith("ii"):
                package = {}
                for i in range(len(COLUMNS)):
                    key = COLUMNS[i]
                    value = line[lengths[i]:lengths[i+1]-1].strip()
                    package[key] = value

                value = PackageRegistry(None, package)
                items.append((key, value))

        return items


factory = PackagesRegistry
