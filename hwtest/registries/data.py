from hwtest.registry import Registry


class DataRegistry(Registry):
    """Base registry for storing data.

    The default behavior is to simply return the data passed as argument
    to the constructor.
    """

    def __init__(self, config, data=None):
        super(DataRegistry, self).__init__(config)
        self.data = data

    def __str__(self):
        return self.data

    def items(self):
        return []
