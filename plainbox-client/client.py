#!/usr/bin/env python3
"""
client for DBus services using ObjectManager
============================================

This module defines :class:`ObjectManagerClient` - a general purpose client for
services that rely on the standard ObjectManager and Properties interfaces to
notify clients about state changes.

Using this library an application can easily observe changes to state of any
number of objects and acess the locally-held state without any additonal
round-trips.

The ObjectManagerClient class exposes a dictionary of :class:`MirroredObject`
which itself exposes a dictionary of interfaces and properties defined by each
such object. Invalidated properties are represented as an unique
:attr:`Invalidated` object.
"""

__all__ = ['Invalidated', 'MirroredObject', 'ObjectManagerClient']

from collections import defaultdict


class InvalidatedType:
    """
    Class representing the special property value `Invalidated`
    """


Invalidated = InvalidatedType


class MirroredObject:
    """
    Class representing a mirror of state exposed by an object on DBus.

    Instances of this class are creted and destroyed automatically by
    :class:`ObjectManagerClient`. Applications can look at the
    :attr:`interfaces_and_properties` without incurring any additional costs
    (expressed as the latency of DBus calls)

    Managed objects have a number of properties (anhored at particular
    interfaces) that are automatically updated whenever the particular object
    is changed remotely. Some properties may be expensive to compute or
    transfer and are invalidated instead. Such properties are repesented as the
    special Invalidated value. Applications are free to perform explicit DBus
    Get() calls for any such property at the time that value is desired.

    :ivar _interfaces_and_properties:
        Dictionary mapping interface names to a collection of properties
    """

    def __init__(self):
        """
        Initialize a new MirroredObject
        """
        self._interfaces_and_properties = defaultdict(dict)

    @property
    def interfaces_and_properties(self):
        """
        dictionary mapping interface name to a dictionary mapping property name
        to property value.
        """
        return self._interfaces_and_properties

    def _add_properties(self, interfaces_and_properties):
        """
        Add interfaces (and optionally, properties)

        :param interfaces_and_properties:
            Mapping from interface name to a map of properties
        """
        self._interfaces_and_properties.update(interfaces_and_properties)

    def _remove_interfaces(self, interfaces):
        """
        Remove interfaces (and properties that they carry).

        :param interfaces:
            List of interface names to remove
        :returns:
            True if the object is empty and should be removed
        """
        for iface_name in interfaces:
            try:
                del self._interfaces_and_properties[iface_name]
            except KeyError:
                pass
        return len(self._interfaces_and_properties) == 0

    def _change_properties(self, iface_name, props_changed, props_invalidated):
        """
        Change properties for a particular interface

        :param iface_name:
            Name of the interface
        :param props_changed:
            A map of properties and their new values
        :param props_invaidated:
            A list of properties that were invalidated
        """
        self._interfaces_and_properties[iface_name].update(props_changed)
        for prop_name in props_invalidated:
            self._interfaes_and_properties[iface_name][prop_name] = Invalidated


class ObjectManagerClient:
    """
    A client that observes and mirrors locally all of the objects managed by
    one or more manager objects on a given bus name.

    Using this class an application can reliably maintain a mirror of all the
    state that some service exposes over DBus and be notified whenever changes
    occur with a single callback.

    The callback has at least two arguments: the object manager client instance
    itself and event name. The following events are supported:

        "service-lost":
            This event is provided whenever the owner of the observed bus name
            goes away. Typically this would happen when the process
            implementing the DBus service exits or disconnects from the bus.
        "service-back":
            This event is provided whenever the owner of the observed bus name
            is established. If the bus name was already taken at the time the
            client is initialized then the on_change callback is invoked
            immediately.
        "object-added":
            This event is provided whenever an object is added to the observed
            bus name. Note that only objects that would have been returned by
            GetManagedObjects() are reported this way. This also differentiates
            between objects merely being added to the bus (which is ignored)
            and objects being added to the managed collection (which is
            reported here).
        "object-removed":
            This event is provided whenever an object is removed from the
            observed bus name. Same restrictions as to "object-added" above
            apply.
        "object-changed":
            This event is provided whenever one or more properties on an object
            are changed or invalidated (changed without providing the updated
            value)

    The state is mirrored based on the three DBus signals:

     - org.freedesktop.DBus.ObjectManager.InterfacesAdded
     - org.freedesktop.DBus.ObjectManager.InterfacesRemoved
     - org.freedesktop.DBus.Properties.PropertiesChanged

    The first two signals deliver information about managed objects being
    added or removed from the bus. The first signal also carries all of the
    properties exported by such objects. The last signal carires information
    about updates to properties of already-existing objects.

    In addition the client listens to the following DBus signal:

    - org.freedesktop.DBus.NameOwnerChanged

    This signal is used to discover when the owner of the bus name changes.
    When the owner goes away the list of objects mirrored locally is reset.

    This class has the following instance variables:

    :ivar _connection:
        A dbus.Connection object
    :ivar _bus_name:
        Well-known name of the bus that this client is observing
    :ivar _event_cb:
        The callback function invoked whenever an event is produced
    :ivar _objects:
        Dictionary mapping from DBus object path to a :class:`MirroredObject`
    :ivar _watch:
        A dbus.bus.NameOwnerWatch that corresponds to the NameOwnerChanged
        signal observed by this object.
    :ivar _matches:
        A list of dbus.connection.SignalMatch that correspond to the three
        data-related signals (InterfacesAdded, InterfacesRemoved,
        PropertiesChanged) observed by this object.
    """

    def __init__(self, connection, bus_name, event_cb):
        """
        Initialize a new ObjectManagerClient

        :param connection:
            A dbus.Connection to work with
        :param bus_name:
            The DBus bus name of where the ObjectManager objects reside.
        :param event_cb:
            A callback invoked whenever an event is produced. The function is
            called at least two arguments, the instance of the client it was
            registered on and the string with the name of the event.
            Additional arguments (and keyword arguments) are provided, specific
            to each event.
        """
        self._connection = connection
        self._bus_name = bus_name
        self._event_cb = event_cb
        self._objects = defaultdict(MirroredObject)
        # Setup a watch for the owner of the bus name. This will allow us to
        # reset internal state when the service goes away and comes back. It
        # also allows us to start before the service itself becomes available.
        self._watch = self._connection.watch_name_owner(
            self._bus_name, self._on_name_owner_changed)
        # Tell DBus that we want to see the three essential signals:
        # - org.freedesktop.DBus.ObjectManager.InterfacesAdded
        # - org.freedesktop.DBus.ObjectManager.InterfacesRemoved
        # - org.freedesktop.DBus.Properties.PropertiesChanged
        # XXX: I suspect that this racy, we perhaps should add many matches at
        # once, not sure if this is possible in python though.
        # NOTE: we want to observe all objects on this bus name, so we have a
        # complete view of all of the objects. This is why we don't filter by
        # object_path.
        match_added = self._connection.add_signal_receiver(
            handler_function=self._on_interfaces_added,
            signal_name='InterfacesAdded',
            dbus_interface='org.freedesktop.DBus.ObjectManager',
            bus_name=self._bus_name)
        match_removed = self._connection.add_signal_receiver(
            handler_function=self._on_interfaces_removed,
            signal_name='InterfacesRemoved',
            dbus_interface='org.freedesktop.DBus.ObjectManager',
            bus_name=self._bus_name)
        match_changed = self._connection.add_signal_receiver(
            handler_function=self._on_properties_changed,
            signal_name='PropertiesChanged',
            dbus_interface='org.freedesktop.DBus.Properties',
            bus_name=self._bus_name,
            path_keyword='object_path')
        self._matches = (match_added, match_removed, match_changed)

    @property
    def objects(self):
        """
        A mapping from object path to :class:`MirroredObject`

        Initially this may be empty but it will react to changes in the
        observed service. It can be pre-seeded by calling GetManagedObjects on
        the appropriate object manager.

        ..see::
            :meth:`pre_seed()`
        """
        return self._objects

    def close(self):
        """
        Stop observing changes and dispose of this client.

        Can be safely called multiple times.
        """
        if self._watch is not None:
            self._watch.cancel()
            for match in self._matches:
                match.remove()
            self._matches = []
            self._watch = None

    def pre_seed(self, object_path):
        """
        Pre-seed known objects with objects managed the specified manager.

        :param object_path:
            Path of the object to interrogate.

        The specified object is interrogated and all of the objects that it
        knows about are mirrored locally. This method should be called right
        _after_ invoking :meth:`observe()` in a way that would cover this
        object. Calling those in the other order introduces a race condition.

        .. warning::
            This function does a synchronous (blocking) DBus method call.
        """
        proxy = self._connection.get_object(self._bus_name, object_path)
        managed_objects = proxy.GetManagedObjects(
            dbus_interface_name='org.freedesktop.DBus.ObjectManager')
        for object_path, interfaces_and_properties in managed_objects.items():
            self._objects[object_path]._add_properties(
                interfaces_and_properties)

    def _on_name_owner_changed(self, name):
        """
        Callback invoked when owner of the observed bus name changes
        """
        if name == '':
            self._objects.clear()
            self._event_cb(self, 'service-lost')
        else:
            self._event_cb(self, 'service-back')

    def _on_interfaces_added(self, object_path, interfaces_and_properties):
        """
        Callback invoked when an object gains one or more interfaces

        The DBus signature of this signal is: oa{sa{sv}}
        """
        # Apply changes
        self._objects[object_path]._add_properties(interfaces_and_properties)
        # Notify users
        self._event_cb(
            self, 'object-added',
            object_path, interfaces_and_properties)

    def _on_interfaces_removed(self, object_path, interfaces):
        """
        Callback invoked when an object looses one or more interfaces.

        The DBus signature of this signal is: oas
        """
        # Apply changes
        if self._objects[object_path]._remove_interfaces(interfaces):
            del self._objects[object_path]
        # Notify users
        self._event_cb(self, 'object-removed', object_path, interfaces)

    def _on_properties_changed(self, iface_name, props_changed,
                               props_invalidated, *, object_path):
        """
        Callback invoked when an object is modified.

        The DBus signature of this signal is: as{sv}as

        .. note::
            The signal itself does not carry information about which object was
            modified but the low-level DBus message does. To be able to
            reliably update our local mirror of the object this callback has to
            be registered with the `path_keyword` argument to
            `add_signal_receiver()` equal to 'object_path'.
        """
        # Apply changes
        self._objects[object_path]._change_properties(
            iface_name, props_changed, props_invalidated)
        # Notify users
        self._event_cb(
            self, 'object-changed',
            object_path, iface_name, props_changed, props_invalidated)
