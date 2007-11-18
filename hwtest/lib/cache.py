class Cache(object):
    def __init__(self, function):
        self._cache = {}
        self._function = function

    def __get__(self, instance, cls=None):
        self._instance = instance
        return self
    
    def __call__(self, *args):
        if not self._cache.has_key((self._instance,) + args):
            self._cache[(self._instance,) + args] = self._function(self._instance, *args)

        return self._cache[(self._instance,) + args]


def cache(function):
    return Cache(function)
