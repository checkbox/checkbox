import logging

from hwtest.registry import Registry


class FileRegistry(Registry):
    """Base registry for containing files.

    The default behavior is to return the content of the file.

    Subclasses should define a filename configuration parameter.
    """

    def __init__(self, config, filename=None):
        super(FileRegistry, self).__init__(config)
        self.filename = filename or self.config.filename

    def __str__(self):
        logging.info("Reading filename: %s", self.filename)
        return file(self.filename, "r").read()

    def items(self):
        return []


factory = FileRegistry
