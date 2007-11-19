from hwtest.registry import Registry


class FileRegistry(Registry):
    """Base registry for containing files.

    The default behavior is to return the content of the file.

    Subclasses should provide a default_filename class attribute.
    """

    default_filename = ""

    def __init__(self, config, filename=None):
        super(FileRegistry, self).__init__(config)
        self.filename = filename or self.default_filename

    def __str__(self):
        return file(self.filename, "r").read()

    def items(self):
        return []


factory = FileRegistry
