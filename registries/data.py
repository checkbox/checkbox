from hwtest.registry import Registry


class DataRegistry(Registry):

    default_data = ""

    def __init__(self, config, data=None):
        super(DataRegistry, self).__init__(config)
        self.data = data or self.default_data

    def __str__(self):
        return self.data


factory = DataRegistry
