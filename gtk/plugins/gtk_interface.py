from hwtest.user_interface import UserInterfacePlugin
from hwtest_gtk.gtk_interface import GTKInterface


class GTKInterfacePlugin(UserInterfacePlugin):
    def __init__(self, config):
        super(GTKInterfacePlugin, self).__init__(config, GTKInterface())


factory = GTKInterfacePlugin
