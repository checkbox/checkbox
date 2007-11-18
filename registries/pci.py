from command import CommandRegistry


class PciRegistry(CommandRegistry):

    default_command = "lspci -vvnn"


factory = PciRegistry
