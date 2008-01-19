import re

from hwtest.registries.command import CommandRegistry


class DpkgRegistry(CommandRegistry):
    """Registry for dpkg information.

    For the moment, this registry only contains items for the version
    and architecture as returned by the dpkg command.
    """

    def items(self):
        items = []
        match = re.search(r"([\d\.]+) \((.*)\)", str(self))
        items.append(("version", match.group(1)))
        items.append(("architecture", match.group(2)))

        return items


factory = DpkgRegistry
