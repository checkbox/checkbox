from command import CommandRegistry


class HaldRegistry(CommandRegistry):

    default_command = "hald --version 2>&1"

    def __str__(self):
        str = super(HaldRegistry, self).__str__()
        return str.strip().rsplit(": ")[1]

    def items(self):
        return [("version", str(self))]


factory = HaldRegistry
