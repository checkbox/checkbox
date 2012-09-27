# Copyright 2012 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
checkbox.dbus.udisks2
=====================

Module for working with UDisks2 from python.

There are two main classes that are interesting here.

The first class is UDisksObserver, which is easy to setup and has pythonic API
to all of the stuff that happens in UDisks2. It offers simple signal handlers
for any changes that occur in UDisks2 that were advertised by DBus.

The second class is UDisksModel, that builds on the observer class to offer
persistent collection of objects managed by UDisks2.

To work with this model you will likely want to look at:
    http://udisks.freedesktop.org/docs/latest/ref-dbus.html
"""

import logging

from dbus import Interface

from checkbox.dbus import drop_dbus_type

__all__ = ['UDisks2Observer', 'UDisks2Model', 'Signal']


# The well-known name for the ObjectManager interface, sadly it is not a part
# of the python binding along with the rest of well-known names.
OBJECT_MANAGER_INTERFACE = "org.freedesktop.DBus.ObjectManager"


class Signal:
    """
    Basic signal that supports arbitrary listeners.

    While this class can be used directly it is best used with the helper
    decorator Signal.define on a member function. The function body is ignored,
    apart from the documentation.

    The function name then becomes a unique (per encapsulating class instance)
    object (an instance of this Signal class) that is created on demand.

    In practice you just have a documentation and use
    object.signal_name.connect() and object.signal_name(*args, **kwargs) to
    fire it.
    """

    def __init__(self, signal_name):
        """
        Construct a signal with the given name
        """
        self._listeners = []
        self._signal_name = signal_name

    def connect(self, listener):
        """
        Connect a new listener to this signal

        That listener will be called whenever fire() is invoked on the signal
        """
        self._listeners.append(listener)

    def disconnect(self, listener):
        """
        Disconnect an existing listener from this signal
        """
        self._listeners.remove(listener)

    def fire(self, args, kwargs):
        """
        Fire this signal with the specified arguments and keyword arguments.

        Typically this is used by using __call__() on this object which is more
        natural as it does all the argument packing/unpacking transparently.
        """
        for listener in self._listeners:
            listener(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        """
        Call fire() with all arguments forwarded transparently
        """
        self.fire(args, kwargs)

    @classmethod
    def define(cls, dummy_func):
        """
        Helper decorator to define a signal descriptor in a class

        The decorated function is never called but is used to get
        documentation.
        """
        return _SignalDescriptor(dummy_func)


class _SignalDescriptor:
    """
    Descriptor for convenient signal access.

    Typically this class is used indirectly, when accessed from Signal.define
    method decorator. It is used to do all the magic required when accessing
    signal name on a class or instance.
    """

    def __init__(self, dummy_func):
        self.signal_name = dummy_func.__name__
        self.__doc__ = dummy_func.__doc__

    def __repr__(self):
        return "<SignalDecorator for signal: %r>" % self.signal_name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        # Ensure that the instance has __signals__ property
        if not hasattr(instance, "__signals__"):
            instance.__signals__ = {}
        if self.signal_name not in instance.__signals__:
            instance.__signals__[self.signal_name] = Signal(self.signal_name)
        return instance.__signals__[self.signal_name]

    def __set__(self, instance, value):
        raise AttributeError("You cannot overwrite signals")

    def __delete__(self, instance):
        raise AttributeError("You cannot delete signals")


class UDisks2Observer:
    """
    Class for observing ongoing changes in UDisks2
    """

    def __init__(self):
        """
        Create a UDisks2 model.

        The model must be connected to a bus before it is first used, see
        connect()
        """
        # Proxy to the UDisks2 object
        self._udisks2_obj = None
        # Proxy to the ObjectManager interface exposed by UDisks2 object
        self._udisks2_obj_manager = None

    @Signal.define
    def on_initial_objects(self, managed_objects):
        """
        Signal fired when the initial list of objects becomes available
        """

    @Signal.define
    def on_interfaces_added(self, object_path, interfaces_and_properties):
        """
        Signal fired when one or more interfaces gets added to a specific
        object.
        """

    @Signal.define
    def on_interfaces_removed(self, object_path, interfaces):
        """
        Signal fired when one or more interface gets removed from a specific
        object
        """

    def connect_to_bus(self, bus):
        """
        Establish initial connection to UDisks2 on the specified DBus bus.

        This will also load the initial set of objects from UDisks2 and thus
        fire the on_initial_objects() signal from the model. Please call this
        method only after connecting that signal if you want to observe that
        event.
        """
        # Once everything is ready connect to udisks2
        self._connect_to_udisks2(bus)
        # And read all the initial objects and setup
        # change event handlers
        self._get_initial_objects()

    def _connect_to_udisks2(self, bus):
        """
        Setup the initial connection to UDisks2

        This step can fail if UDisks2 is not available and cannot be
        service-activated.
        """
        # Access the /org/freedesktop/UDisks2 object sitting on the
        # org.freedesktop.UDisks2 bus name. This will trigger the necessary
        # activation if udisksd is not running for any reason
        logging.debug("Accessing main UDisks2 object")
        self._udisks2_obj = bus.get_object(
            "org.freedesktop.UDisks2", "/org/freedesktop/UDisks2")
        # Now extract the standard ObjectManager interface so that we can
        # observe and iterate the collection of objects that UDisks2 provides.
        logging.debug("Accessing ObjectManager interface on UDisks2 object")
        self._udisks2_obj_manager = Interface(
            self._udisks2_obj, OBJECT_MANAGER_INTERFACE)

    def _get_initial_objects(self):
        """
        Get the initial collection of objects.

        Needs to be called before the first signals from DBus are observed.
        Requires a working connection to UDisks2.
        """
        # Having this interface we can now peek at the existing objects.
        # We can use the standard method GetManagedObjects() to do that
        logging.debug("Accessing GetManagedObjects() on UDisks2 object")
        managed_objects = self._udisks2_obj_manager.GetManagedObjects()
        managed_objects = drop_dbus_type(managed_objects)
        # Fire the public signal for getting initial objects
        self.on_initial_objects(managed_objects)
        # Connect our internal handles to the DBus signal handlers
        logging.debug("Setting up DBus signal handler for InterfacesAdded")
        self._udisks2_obj_manager.connect_to_signal(
            "InterfacesAdded", self._on_interfaces_added)
        logging.debug("Setting up DBus signal handler for InterfacesRemoved")
        self._udisks2_obj_manager.connect_to_signal(
            "InterfacesRemoved", self._on_interfaces_removed)

    def _on_interfaces_added(self, object_path, interfaces_and_properties):
        """
        Internal callback that is called by DBus

        This function is responsible for firing the public signal
        """
        # Convert from dbus types
        object_path = drop_dbus_type(object_path)
        interfaces_and_properties = drop_dbus_type(interfaces_and_properties)
        # Log what's going on
        logging.debug("The object %r has gained the following interfaces and "
                      "properties: %r", object_path, interfaces_and_properties)
        # Call the signal handler
        self.on_interfaces_added(object_path, interfaces_and_properties)

    def _on_interfaces_removed(self, object_path, interfaces):
        """
        Internal callback that is called by DBus

        This function is responsible for firing the public signal
        """
        # Convert from dbus types
        object_path = drop_dbus_type(object_path)
        interfaces = drop_dbus_type(interfaces)
        # Log what's going on
        logging.debug("The object %r has lost the following interfaces: %r",
                      object_path, interfaces)
        # Call the signal handler
        self.on_interfaces_removed(object_path, interfaces)


class UDisks2Model:
    """
    Model for working with UDisks2

    This class maintains a persistent model of what UDisks2 knows about, based
    on the UDisks2Observer class and the signals it offers.
    """

    def __init__(self, observer):
        """
        Create a UDisks2 model.

        The model will track changes using the specified observer (which is
        expected to be a UDisks2Observer instance)

        You should only connect the observer to the bus after creating the
        model otherwise the initial objects will not be detected.
        """
        # Local state, everything that UDisks2 tells us
        self._managed_objects = {}
        self._observer = observer
        # Connect all the signals to the observer
        self._observer.on_initial_objects.connect(self._on_initial_objects)
        self._observer.on_interfaces_added.connect(self._on_interfaces_added)
        self._observer.on_interfaces_removed.connect(
            self._on_interfaces_removed)

    @property
    def managed_objects(self):
        """
        A collection of objects that is managed by this model. All changes as
        well as the initial state, are reflected here.
        """
        return self._managed_objects

    def _on_initial_objects(self, managed_objects):
        """
        Internal callback called when we get the initial collection of objects
        """
        self._managed_objects = drop_dbus_type(managed_objects)

    def _on_interfaces_added(self, object_path, interfaces_and_properties):
        """
        Internal callback called when an interface is added to certain object
        """
        if object_path not in self._managed_objects:
            self._managed_objects[object_path] = {}
        obj = self._managed_objects[object_path]
        obj.update(interfaces_and_properties)

    def _on_interfaces_removed(self, object_path, interfaces):
        """
        Internal callback called when an interface is removed from a certain
        object
        """
        if object_path in self._managed_objects:
            obj = self._managed_objects[object_path]
            for interface in interfaces:
                if interface in obj:
                    del obj[interface]
