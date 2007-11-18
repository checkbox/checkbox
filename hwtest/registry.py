import re

from hwtest.repository import Repository, RepositoryManager
from hwtest.lib.cache import cache


class Registry(Repository):

    def __init__(self, config):
        super(Registry, self).__init__(config)

    def __str__(self):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def __getattr__(self, name):
        return self.get(name)

    def split(self, *args, **kwargs):
        return str(self).split(*args, **kwargs)

    def items(self):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def iteritems(self):
        for k, v in self.items():
            yield k, v

    def iterkeys(self):
        for k, v in self.items():
            yield k

    def keys(self):
        return list(self.iterkeys())

    def itervalues(self):
        for k, v in self.items():
            yield v

    def values(self):
        return list(self.itervalues())

    def clear(self):
        raise Exception, "Cannot call clear on registry."

    def setdefault(self, key, default=None):
        raise Exception, "Cannot call setdefault on registry."

    def __cmp__(self, foreign):
        local = set(self.items())
        foreign = set(foreign.items())
        if local == foreign:
            return 0
        elif local < foreign:
            return -1
        return 1

    def __contains__(self, key):
        return key in self.keys()

    def __len__(self):
        return len(self.keys())

    def __getitem__(self, key):
        for k, v in self.items():
            if k == key:
                return v

    def __setitem__(self, key, value):
        raise Exception, "Cannot set setitem on registry."

    def __delitem__(self, key):
        raise Exception, "Cannot call delitem on registry."

    def update(self, foreign):
        raise Exception, "Cannot call update on registry."


class RegistryManager(RepositoryManager, Registry):

    @cache
    def items(self):
        items = []
        sections = self._config.get_defaults().registries
        for section_name in re.split(r"\s+", sections):
            section = self.load_section(section_name)
            for name in section.get_names():
                entry = section.load_entry(name)
                items.append((name, entry))
        return items
