from hwtest.registry import Registry


class NoneRegistry(Registry):
    """Base registry for an empty registry.

    The default behavior is to always return None.
    """

    def __str__(self):
        return ""

    def items(self):
        return []
