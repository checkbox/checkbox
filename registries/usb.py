from command import CommandRegistry


class UsbRegistry(CommandRegistry):

    default_command = "lsusb -v"


factory = UsbRegistry
