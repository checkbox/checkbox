import os

from hwtest.registry import Registry


class CommandRegistry(Registry):

    default_command = ""

    def __init__(self, config, command=None):
        super(CommandRegistry, self).__init__(config)
        self.command = command or self.default_command

    def __str__(self):
        return os.popen(self.command).read()


factory = CommandRegistry
