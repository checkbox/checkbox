import re

from command import CommandRegistry


class DpkgRegistry(CommandRegistry):

    default_command = "dpkg --version"

    def items(self):
        items = []
        match = re.search(r"([\d\.]+) \((.*)\)", str(self))
        items.append(("version", match.group(1)))
        items.append(("architecture", match.group(2)))

        return items


factory = DpkgRegistry
