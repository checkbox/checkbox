import os

from hwtest.registry import Registry
from hwtest.lib.cache import cache

from file import FileRegistry


class DirectoryRegistry(Registry):

    default_directory = "/"

    def __init__(self, config, directory=None):
        super(DirectoryRegistry, self).__init__(config)
        self.directory = directory or self.default_directory

    def __str__(self):
        strings = []
        for name in os.listdir(self.directory):
            strings.append(name)

        return "\n".join(strings)

    @cache
    def items(self):
        items = []
        for key in self.split("\n"):
            path = os.path.join(self.directory, key)
            if os.path.isfile(path):
                value = FileRegistry(self.config, path)
            elif os.path.isdir(path):
                value = DirectoryRegistry(self.config, path)

            items.append((key, value))

        return items


factory = DirectoryRegistry
