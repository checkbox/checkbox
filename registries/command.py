import os

from hwtest.registry import Registry


class CommandRegistry(Registry):
    """Base registry for running commands.

    The default behavior is to return the output of the command.

    Subclasses should provide a default_command class attribute.
    """

    default_command = ""

    def __init__(self, config, command=None):
        super(CommandRegistry, self).__init__(config)
        self.command = command or self.default_command

    def __str__(self):
        return os.popen(self.command).read()

    def items(self):
        return []


factory = CommandRegistry
