from hwtest.plugin import Plugin
from hwtest.iterator import Iterator


class UserInterface(Plugin):

    required_attributes = ["interface_module", "interface_class"]
    optional_attributes = ["title", "gtk_path"]

    def run(self):
        interface_module = __import__(self.config.interface_module,
            None, None, [''])
        interface_class = getattr(interface_module, self.config.interface_class)
        interface = interface_class(self.config)

        iterator = Iterator([
             ("prompt", "permission"),
             ("prompt", "intro"),
             ("prompt", "gather"),
             ("prompt", "category"),
             ("prompt", "questions"),
             ("prompt", "report"),
             ("prompt", "exchange"),
             ("prompt", "final")])

        while True:
            try:
                event_type = iterator.go(interface.direction)
            except StopIteration:
                break

            self._manager.reactor.fire(event_type, interface)


factory = UserInterface
