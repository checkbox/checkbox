from hwtest.lib.cache import cache
from hwtest.lib.conversion import string_to_type

from data import DataRegistry
from file import FileRegistry


class ProcessorRegistry(DataRegistry):

    @cache
    def items(self):
        items = []
        for line in [l.strip() for l in self.split("\n")]:
            (key, value) = line.split(':', 1)

            # Sanitize key so that it can be expressed as
            # an attribute
            key = key.strip()
            key = key.replace(' ', '_')
            key = key.lower()

            # Srip processor entry because it is redundant
            if key == 'processor':
                continue

            # Express value as a list if it is flags
            value = value.strip()
            if key == 'flags':
                value = value.split()
            else:
                value = string_to_type(value)

            items.append((key, value))

        return items


class CpuinfoRegistry(FileRegistry):

    default_filename = "/proc/cpuinfo"

    @cache
    def items(self):
        items = []
        for data in [d.strip() for d in self.split("\n\n") if d]:
            key = len(items)
            value = ProcessorRegistry(self.config, data)
            items.append((key, value))

        return items


factory = CpuinfoRegistry
