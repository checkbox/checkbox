from hwtest.plugin import Plugin


class UserInterface(Plugin):

    attributes = ["interface_module", "interface_class"]

    def __init__(self, *args, **kwargs):
        super(UserInterface, self).__init__(*args, **kwargs)
        interface_module = __import__(self.config.interface_module,
            None, None, [''])
        interface_class = getattr(interface_module, self.config.interface_class)
        self.interface = interface_class(self.config)

    def run(self):
        for event_type in [
             ("interface", "show-permission"),
             ("interface", "show-intro"),
             ("interface", "show-gather"),
             ("interface", "show-category"),
             ("interface", "show-question"),
             ("interface", "show-report"),
             ("interface", "show-exchange"),
             ("interface", "show-final")]:
            self._manager.reactor.fire(event_type, self.interface)


factory = UserInterface
