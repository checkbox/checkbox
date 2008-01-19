from hwtest.lib.cache import cache
from hwtest.lib.conversion import string_to_type

from hwtest.registries.data import DataRegistry
from hwtest.registries.file import FileRegistry


class ProcessorRegistry(DataRegistry):
    """Registry for processor information.

    Each item contained in this registry consists of the information
    for a single processor in the /proc/cpuinfo file.
    """

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
    """Registry for cpuinfo information.

    Each item contained in this registry consists of the processor number
    as key and the corresponding processor registry as value.
    """

    @cache
    def items(self):
        items = []
        for data in [d.strip() for d in self.split("\n\n") if d]:
            key = len(items)
            value = ProcessorRegistry(self.config, data)
            items.append((key, value))

        return items


factory = CpuinfoRegistry
