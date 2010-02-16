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
class Resolver:
    """
    Main class. Instantiate with the root directory of your items.
    """

    def __init__(self, compare=None, key=None):
        if compare is None:
            compare = lambda a, b: cmp(a, b)
        if key is None:
            key = lambda k: k

        self.compare = compare
        self.key = key

        # detect repeated resolution attempts - these indicate some circular dependency
        self.reentrant_resolution = set()

        # collect all items
        self.items = {}

        # for each item, keep a set of dependents and dependencies
        self.dependents = {}
        self.dependencies = {}

    def add(self, item, *dependencies):
        key = self.key(item)
        if key in self.items:
            raise Exception, "%s: key already exists" % key
        self.items[key] = item

        dependency_keys = [self.key(d) for d in dependencies]
        self.dependencies[key] = set(dependency_keys)

    def remove(self, item):
        key = self.key(item)
        del self.items[key]
        del self.dependencies[key]

    def resolve(self, item, found=None):
        """
        the center piece.
        recursively resolve dependencies of scripts
        return them as a flat list, sorted according to ancestral relationships
        """
        key = self.key(item)
        resolved = self.dependents.get(key, None)
        if resolved is not None:
            return resolved

        if key not in self.items:
            msg = "no dependencies found for %s" % key
            if found:
                msg += " while resolving %s" % found
            raise Exception, msg

        dependencies = self.dependencies.get(key, set())
        resolved = set()

        for dependency in dependencies:
            resolution_step = (key, dependency)
            if resolution_step in self.reentrant_resolution:
                if found:
                    scapegoat = found
                else:
                    scapegoat = dependency
                raise Exception, "circular dependency involving %s and %s" % (key, scapegoat)
            # add resolution
            self.reentrant_resolution.add(resolution_step)
            # and its dependencies, if any
            resolved.update(self.resolve(self.items[dependency], found=key))

        # now it's time for sorting hierarchically... Since circular dependencies are excluded,
        # ancestors will always have fewer dependencies than descendants, so sorting by the
        # number of dependencies will give the desired order.
        resolved = sorted(resolved, key=lambda x : len(self.dependents[x]))
        resolved.append(key)
        self.dependents[key] = resolved

        return resolved

    def get_dependencies(self, item):
        return [self.items[r] for r in self.resolve(item)]

    def get_dependents(self, item=None):
        dependents = []
        if item:
            # Immediate dependents
            key = self.key(item)
            all_dependents = filter(
                lambda x: key in self.resolve(x)[:-1],
                self.items.itervalues())
            dependents = filter(
                lambda x: self.key(self.get_dependencies(x)[-2]) == key,
                all_dependents)
        else:
            # First level of dependents
            dependents = filter(lambda x: len(self.resolve(x)) == 1, self.items.itervalues())

        index = 0
        dependents = sorted(dependents, self.compare)
        while index < len(dependents):
            sub_dependents = self.get_dependents(dependents[index])
            if sub_dependents:
                dependents[index+1:index+1] = sub_dependents
                index += len(sub_dependents)
            index += 1

        return dependents
