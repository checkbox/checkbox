from hwtest.registry import Registry


class FileRegistry(Registry):

    default_filename = ""

    def __init__(self, config, filename=None):
        super(FileRegistry, self).__init__(config)
        self.filename = filename or self.default_filename

    def __str__(self):
        return file(self.filename, "r").read()


factory = FileRegistry
