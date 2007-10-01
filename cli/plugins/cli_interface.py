from hwtest.user_interface import UserInterfacePlugin
from hwtest_cli.cli_interface import CLIInterface


class CLIInterfacePlugin(UserInterfacePlugin):
    def __init__(self):
        super(CLIInterfacePlugin, self).__init__(CLIInterface())


factory = CLIInterfacePlugin
