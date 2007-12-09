from hwtest.lib.cache import cache

from data import DataRegistry
from file import FileRegistry


class ModuleRegistry(DataRegistry):
    """Registry for individual module information.

    Each item contained in this registry consists of the following
    information for each module:

    size:         Memory size of the module, in bytes.
    instances:    How many instances of the module are currently loaded.
    dependencies: If the module depends upon another module to be present
                  in order to function, and lists those modules.
    state:        The load state of the module: Live, Loading or Unloading.
    offset:       Current kernel memory offset for the loaded module.
    """

    fields = ["size", "instances", "dependencies", "state", "offset"]

    @cache
    def items(self):
        (size, instances, dependencies, state, offset) = self.split(" ")

        items = []
        items.append(("size", int(size)))
        items.append(("instances", int(instances)))
        items.append(("dependencies",
            dependencies == "-" and [] or dependencies.split(",")[:-1]))
        items.append(("state", state))
        items.append(("offset", int(offset, 16)))

        return items


class ModulesRegistry(FileRegistry):
    """Registry for modules information.

    Each item contained in this registry consists of the information
    in the /proc/modules file.
    """

    @cache
    def items(self):
        items = []
        for line in self.split("\n")[:-1]:
            (key, data) = line.split(" ", 1)
            value = ModuleRegistry(self.config, data)
            items.append((key, value))

        return items


factory = ModulesRegistry
