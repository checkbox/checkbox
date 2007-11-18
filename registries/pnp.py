from command import CommandRegistry


class PnpRegistry(CommandRegistry):

    default_command = "lspnp -v"


factory = PnpRegistry
