from hwtest.plugin import Plugin


class UserInterface(Plugin):

    def __init__(self, config):
        super(UserInterface, self).__init__(config)
        interface_module = __import__(self.config.interface_module,
            None, None, [''])
        interface_class = getattr(interface_module, self.config.interface_class)
        self.interface = interface_class(config)

    def run(self):
        for event_type in [
             ("interface", "show-permission"),
             ("interface", "show-gather"),
             ("interface", "show-category"),
             ("interface", "show-question"),
             ("interface", "show-report"),
             ("interface", "show-exchange")]:
            self._manager.reactor.fire(event_type, self.interface)


factory = UserInterface
