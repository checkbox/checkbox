import os

from hwtest.plugin import Plugin
from hwtest.iterator import Iterator


class UserInterface(Plugin):

    attributes = ["interface_module", "interface_class"]

    def run(self):
        interface_module = __import__(self.config.interface_module,
            None, None, [''])
        interface_class = getattr(interface_module, self.config.interface_class)
        interface = interface_class(self.config)

        if os.getuid() != 0:
            self._manager.reactor.fire(("prompt", "error"), interface,
                "Invalid permission", "Application must be run as root")
            self._manager.reactor.stop()

        iterator = Iterator([
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
