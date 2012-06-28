#
# This file is part of Checkbox.
#
# Copyright 2008 Canonical Ltd.
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.
#
from collections import defaultdict, OrderedDict


class Resolver:
    """
    Main class. Instantiate with the root directory of your items.
    """

    def __init__(self, key_func=None):
        if key_func is None:
            key_func = lambda k: k
        self.key_func = key_func

        self.items_added = OrderedDict()
        self.depends = {}  # Dependencies
        self.rdepends = defaultdict(list)  # Reverse dependencies

        # Data used in _resolve method
        self.items = None
        self.items_blocked = None
        self.resolved = False

    def add(self, item, *dependencies):
        """
        Add item as pending
        """
        key = self.key_func(item)
        if key in self.items_added:
            raise Exception("%s: key already exists" % key)

        # Dependencies bookkeeping
        self.items_added[key] = item
        self.depends[key] = list(dependencies)
        for dependency in dependencies:
            self.rdepends[dependency].append(key)

        # Circular dependencies check
        def circular_dependencies(node):
            seen = circular_dependencies.seen
            for dependency in self.depends.get(node, []):
                if key == dependency:
                    raise Exception("circular dependency involving "
                                    "%s and %s" % (key, node))
                if dependency in seen:
                    continue
                seen.add(dependency)
                circular_dependencies(dependency)
        circular_dependencies.seen = set((key,))
        circular_dependencies(key)

        # Resolve on next call to get_dependencies/get_dependents
        self.resolved = False

    def _resolve(self):
        """
        Work through the pending items and reorder them properly
        """
        if self.resolved:
            return

        # Initialize internal ordering data
        self.items = OrderedDict()
        self.items_blocked = {}

        def add_unblocked(key):
            """Add items that have been unblocked"""
            for dependent in self.rdepends[key]:
                if not dependent in self.items_blocked:
                    continue

                unblocked = all(dependency in self.items
                                for dependency in self.depends[dependent]
                                if dependency in self.items_added)
                if unblocked:
                    item = self.items_blocked[dependent]
                    self.items[dependent] = item
                    del self.items_blocked[dependent]

                    add_unblocked(dependent)

        for key, item in self.items_added.items():
            # Avoid adding an item until all dependencies have been met
            blocked = any(dependency not in self.items
                          for dependency in self.depends[key]
                          if dependency in self.items_added)

            if blocked:
                self.items_blocked[key] = item
            else:
                self.items[key] = item
                add_unblocked(key)

        if self.items_blocked:
            raise Exception('There are {} items blocked: {}'
                            .format(len(self.items_blocked),
                                    ', '.join(self.items_blocked.keys())))

        # Don't resolve again on next call to get_dependencies/get_dependents
        # unless a new item is added
        self.resolved = True

    def get_dependencies(self, item):
        """
        Return a list of the dependencies for a given item
        """
        self._resolve()
        key = self.key_func(item)
        if key not in self.depends:
            msg = "no dependencies found for %s" % key
            raise Exception(msg)

        dependencies = self.depends[key] + [key]

        return dependencies

    def get_dependents(self, item=None):
        """
        Return a list of the items that depend on the given one
        or the whole list of items topologically ordered
        """
        self._resolve()
        items = list(self.items.values())
        if item is not None:
            index = items.index(item)
            items = items[index + 1:]

        return items
