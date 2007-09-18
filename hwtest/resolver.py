class Resolver:
    '''
    Main class. Instantiate with the root directory of your names.
    '''

    def __init__(self):
        # detect repeated resolution attempts - these indicate some circular dependency
        self.reentrant_resolution = set()

        # for each script, keep a set of dependencies
        self.dependencies = {}

        # collect all names underneath root directory
        self.names = {}

    def add(self, name, *dependencies):
        if name in self.names:
            raise Exception, '%s: name already exists' % name
        self.names[name] = set(dependencies)

    def remove(self, name):
        del self.names[name]

    def resolve(self, name, found=None):
        '''
        the center piece.
        recursively resolve dependencies of scripts
        return them as a flat list, sorted according to ancestral relationships
        '''
        resolved = self.dependencies.get(name, None)
        if resolved is not None:
            return resolved

        if name not in self.names:
            msg = 'no dependencies found for %s' % name
            if found:
                msg += ' while resolving %s' % found
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
                raise Exception, 'circular dependency involving %s and %s' % (name, scapegoat)
            self.reentrant_resolution.add(resolution_step)
            resolved.update(self.resolve(dependency, found=name)) # and its dependencies, if any

        resolved = list(resolved)
        # now it's time for sorting hierarchically... Since circular dependencies are excluded,
        # ancestors will always have fewer dependencies than descendants, so sorting by the
        # number of dependencies will give the desired order.
        resolved.sort(key = lambda x : len(self.dependencies[x]))
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
        dependents.sort()
        while index < len(dependents):
            sub_dependents = self.get_dependents(dependents[index])
            if sub_dependents:
                dependents[index+1:index+1] = sub_dependents
                index += len(sub_dependents)
            index += 1

        return dependents
