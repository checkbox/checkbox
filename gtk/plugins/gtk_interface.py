from hwtest.user_interface import UserInterfacePlugin
from hwtest_gtk.gtk_interface import GTKInterface


class GTKInterfacePlugin(UserInterfacePlugin):
    def __init__(self):
        super(GTKInterfacePlugin, self).__init__(GTKInterface())


factory = GTKInterfacePlugin
