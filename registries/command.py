import os
import logging

from hwtest.lib.cache import cache

from hwtest.registry import Registry


class CommandRegistry(Registry):
    """Base registry for running commands.

    The default behavior is to return the output of the command.

    Subclasses should define a command configuration parameter.
    """

    def __init__(self, config, command=None):
        super(CommandRegistry, self).__init__(config)
        self.command = command or self.config.command

    @cache
    def __str__(self):
        logging.info("Running command: %s", self.command)
        return os.popen(self.command).read()

    def items(self):
        return []


factory = CommandRegistry
