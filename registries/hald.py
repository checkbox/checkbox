from command import CommandRegistry


class HaldRegistry(CommandRegistry):
    """Registry for HAL daemon information.

    For the moment, this registry only contains an item for the version
    as returned by the hald command.
    """
 
    def __str__(self):
        str = super(HaldRegistry, self).__str__()
        return str.strip().rsplit(": ")[1]

    def items(self):
        return [("version", str(self))]


factory = HaldRegistry
