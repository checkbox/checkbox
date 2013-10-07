#!/usr/bin/env python3
"""
Example application using the `client` module
=============================================
"""

__all__ = ['ExampleApp']

from gi.repository import GObject
from dbus import SessionBus
from dbus.mainloop.glib import DBusGMainLoop

from client import ObjectManagerClient


class ExampleApp:
    """
    Simple application that demonstrates how to use ObjectManagerClient
    """

    BUS_NAME = 'com.canonical.certification.PlainBox1'

    def __init__(self):
        self.loop = GObject.MainLoop()
        self.bus = SessionBus(mainloop=DBusGMainLoop())
        self.client = ObjectManagerClient(
            self.bus, self.BUS_NAME, self._on_change)

    def start(self):
        # Here the application can pretty much do anything it wants,
        # including caching more objects, etc.
        try:
            self.loop.run()
        except KeyboardInterrupt:
            pass
        finally:
            self.client.close()

    def _on_change(self, client, reason):
        print("state changed, reason: {}".format(reason).center(80, '-'))
        if reason == 'service-back':
            # Pre-seed ObjectManagerClient with data from well-known providers
            self.client.pre_seed('/plainbox/service1')
            # XXX: ugly hack!
            # This looks at object path, should use interfaces instead
            for object_path in list(self.client.objects):
                if object_path.startswith("/plainbox/provider"):
                    self.client.pre_seed(object_path)
        # Print a dump of all the known objects
        for path, obj in sorted(client.objects.items()):
            print("{}".format(str(path)))
            for iface, props in sorted(obj.interfaces_and_properties.items()):
                print("\t[{}]".format(str(iface)))
                for name, value in sorted(props.items()):
                    print("\t\t{} = {!r}".format(name, value))


def main():
    ExampleApp().start()


if __name__ == "__main__":
    main()
