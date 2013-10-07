#!/usr/bin/env python3
"""
Example application using the `client` module
=============================================
"""

__all__ = ['ExampleApp']

from gi.repository import GObject

from colorama import Fore, Style
from colorama import deinit as deinit_colorama
from colorama import init as init_colorama
from dbus import SessionBus
from dbus.mainloop.glib import DBusGMainLoop

from client import PlainBoxClient


class ExampleApp:
    """
    Simple application that demonstrates how to use ObjectManagerClient
    """

    def __init__(self):
        self.loop = GObject.MainLoop()
        self.bus = SessionBus(mainloop=DBusGMainLoop())
        self.client = PlainBoxClient(self.bus, self._on_event)

    def start(self):
        # Here the application can pretty much do anything it wants,
        # including caching more objects, etc.
        try:
            self.loop.run()
        except KeyboardInterrupt:
            pass
        finally:
            self.client.close()

    def _on_event(self, client, event, *args):
        print("event: {}".format(event).center(80, '-'))
        if event == 'service-back':
            print(Fore.MAGENTA + 'Service Connected' + Style.RESET_ALL)
            # Pre-seed ObjectManagerClient with data from all providers
            for object_path, object in self.client.objects.items():
                if ("org.freedesktop.DBus.ObjectManager"
                        in object.interfaes_and_properties):
                    self.client.pre_seed(object_path)
        elif event == 'service-lost':
            print(Fore.MAGENTA + 'Service Disconnected' + Style.RESET_ALL)
        elif event == 'object-added':
            object_path, interfaces_and_properties = args
            print(Fore.GREEN, end='')
            print(object_path)
            for interface, props in interfaces_and_properties.items():
                print('\t[{}]'.format(interface))
                for prop_name, prop_value in props.items():
                    print('\t\t{} = {}'.format(prop_name, prop_value))
            print(Style.RESET_ALL, end='')
        elif event == 'object-removed':
            object_path, interfaces = args
            print(Fore.RED, end='')
            print(object_path)
            for interface in interfaces:
                print('\t[{}]'.format(interface))
            print(Style.RESET_ALL, end='')
        elif event == 'object-changed':
            object_path, interface, props_changed, props_invalidated = args
            print(Fore.YELLOW, end='')
            print(object_path)
            print('\t[{}]'.format(interface))
            for prop_name, prop_value in props_changed.items():
                print('\t\t{} = {}'.format(prop_name, prop_value))
            for prop_name in props_invalidated:
                print('\t\t{} = invalidated'.format(prop_name, prop_value))
            print(Style.RESET_ALL, end='')
        elif event == 'job-result-available':
            job, result = args
            print(Fore.CYAN, end='')
            print("Job result available:")
            print("\tjob: {}".format(job))
            print("\tresult:  {}".format(result))
            print(Style.RESET_ALL, end='')
        elif event == 'ask-for-outcome':
            runner, = args
            print(Fore.CYAN, end='')
            print("Job result available:")
            print("\trunner: {}".format(runner))
            print(Style.RESET_ALL, end='')
        else:
            print("Unknown event: {}".format(event))

    def _dump_state(self):
        # Print a dump of all the known objects
        for path, obj in sorted(self.client.objects.items()):
            print("{}".format(str(path)))
            for iface, props in sorted(obj.interfaces_and_properties.items()):
                print("\t[{}]".format(str(iface)))
                for name, value in sorted(props.items()):
                    print("\t\t{} = {!r}".format(name, value))


def main():
    init_colorama()
    try:
        ExampleApp().start()
    finally:
        deinit_colorama()


if __name__ == "__main__":
    main()
