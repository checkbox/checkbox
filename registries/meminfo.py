import re

from hwtest.lib.cache import cache
from hwtest.lib.conversion import string_to_type

from file import FileRegistry


class MeminfoRegistry(FileRegistry):
    """Registry for memory information.

    Each item contained in this registry consists of the information
    in the /proc/meminfo file.
    """

    @cache
    def items(self):
        items = []
        for line in self.split("\n"):
            match = re.match(r"(.*):\s+(.*)", line)
            if match:
                key = match.group(1)
                value = string_to_type(match.group(2))
                items.append((key, value))

        return items


factory = MeminfoRegistry
