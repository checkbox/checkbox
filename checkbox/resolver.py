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
    Main class. Instantiate with the root directory of your names.
    """

    def __init__(self, cmp=None):
        self.cmp = cmp

        # detect repeated resolution attempts - these indicate some circular dependency
        self.reentrant_resolution = set()

        # for each script, keep a set of dependencies
        self.dependencies = {}

        # collect all names underneath root directory
        self.names = {}

    def add(self, name, *dependencies):
        if name in self.names:
            raise Exception, "%s: name already exists" % name
        self.names[name] = set(dependencies)

    def remove(self, name):
        del self.names[name]

    def resolve(self, name, found=None):
        """
        the center piece.
        recursively resolve dependencies of scripts
        return them as a flat list, sorted according to ancestral relationships
        """
        resolved = self.dependencies.get(name, None)
        if resolved is not None:
            return resolved

        if name not in self.names:
            msg = "no dependencies found for %s" % name
            if found:
                msg += " while resolving %s" % found
            raise Exception, msg


        dependencies = self.names.get(name)
        resolved = set()

        for dependency in dependencies:
            resolution_step = (name, dependency)
            if resolution_step in self.reentrant_resolution:
                if found:
                    scapegoat = found
                else:
                    scapegoat = dependency
                raise Exception, "circular dependency involving %s and %s" % (name, scapegoat)
            self.reentrant_resolution.add(resolution_step)
            resolved.update(self.resolve(dependency, found=name)) # and its dependencies, if any

        # now it's time for sorting hierarchically... Since circular dependencies are excluded,
        # ancestors will always have fewer dependencies than descendants, so sorting by the
        # number of dependencies will give the desired order.
        resolved = sorted(resolved, key=lambda x : len(self.dependencies[x]))
        resolved.append(name)
        self.dependencies[name] = resolved

        return resolved

    def get_dependencies(self, name):
        return self.resolve(name)

    def get_dependents(self, name=None):
        dependents = []
        if name:
            # Immediate dependents
            all_dependents = filter(lambda x : name in self.resolve(x)[:-1], self.names)
            dependents = filter(lambda x : self.get_dependencies(x)[-2] == name, all_dependents)
        else:
            # First level of dependents
            dependents = filter(lambda x : len(self.resolve(x)) == 1, self.names)

        index = 0
        dependents = sorted(dependents, self.cmp)
        while index < len(dependents):
            sub_dependents = self.get_dependents(dependents[index])
            if sub_dependents:
                dependents[index+1:index+1] = sub_dependents
                index += len(sub_dependents)
            index += 1

        return dependents
