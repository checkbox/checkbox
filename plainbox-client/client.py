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

__all__ = [
    'Invalidated',
    'MirroredObject',
    'ObjectManagerClient',
    'PlainBoxClient'
]

from collections import defaultdict
from logging import getLogger


_logger = getLogger("plainbox.client")


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

    DBUS_OBJECT_MANAGER_IFACE = 'org.freedesktop.DBus.ObjectManager'
    DBUS_PROPERTIES_IFACE = 'org.freedesktop.DBus.Properties'

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
        self._watch = self._observe_bus_name()
        self._matches = self._observe_signals()

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

    def _observe_bus_name(self):
        """
        Internal method of ObjectManagerClient.

        Sets up a watch for the owner of the bus we are interested in

        :returns:
            A NameOwnerWatch instance that describes the watch
        """
        # Setup a watch for the owner of the bus name. This will allow us to
        # reset internal state when the service goes away and comes back. It
        # also allows us to start before the service itself becomes available.
        return self._connection.watch_name_owner(
            self._bus_name, self._on_name_owner_changed)

    def _observe_signals(self):
        """
        Internal method of ObjectManagerClient

        Sets up a set of matches that allow the client to observe enough
        signals to keep internal mirror of the data correct.

        Tells DBus that we want to see the three essential signals:

        - org.freedesktop.DBus.ObjectManager.InterfacesAdded
        - org.freedesktop.DBus.ObjectManager.InterfacesRemoved
        - org.freedesktop.DBus.Properties.PropertiesChanged

        NOTE: we want to observe all objects on this bus name, so we have a
        complete view of all of the objects. This is why we don't filter by
        object_path.

        :returns:
            A tuple of SignalMatch instances that describe observed signals.
        """
        match_object_manager = self._connection.add_signal_receiver(
            handler_function=self._on_signal,
            signal_name=None,  # match all signals
            dbus_interface=self.DBUS_OBJECT_MANAGER_IFACE,
            path=None,  # match all senders
            bus_name=self._bus_name,
            # extra keywords, those allow us to get meta-data to handlers
            byte_arrays=True,
            path_keyword='object_path',
            interface_keyword='interface',
            member_keyword='member')
        match_properties = self._connection.add_signal_receiver(
            handler_function=self._on_signal,
            signal_name="PropertiesChanged",
            dbus_interface=self.DBUS_PROPERTIES_IFACE,
            path=None,  # match all senders
            bus_name=self._bus_name,
            # extra keywords, those allow us to get meta-data to handlers
            byte_arrays=True,
            path_keyword='object_path',
            interface_keyword='interface',
            member_keyword='member')
        return (match_object_manager, match_properties)

    def _on_signal(self, *args, object_path, interface, member):
        """
        Internal method of ObjectManagerClient

        Dispatches each received signal to a handler function. Doing the
        dispatch here allows us to register one listener for many signals and
        then do all the routing inside the application.

        :param args:
            Arguments of the original signal
        :param object_path:
            Path of the object that sent the signal
        :param interface:
            Name of the DBus interface that designates the signal
        :param member:
            Name of the DBus signal (without the interface part)
        """
        if interface == self.DBUS_OBJECT_MANAGER_IFACE:
            if member == 'InterfacesAdded':
                return self._on_interfaces_added(*args)
            elif member == 'InterfacesRemoved':
                return self._on_interfaces_removed(*args)
        elif interface == self.DBUS_PROPERTIES_IFACE:
            if member == 'PropertiesChanged':
                return self._on_properties_changed(
                    *args, object_path=object_path)
        _logger.warning("Unsupported signal received: %s.%s: %r",
                        interface, member, args)

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


class PlainBoxClient(ObjectManagerClient):
    """
    A subclass of ObjectManagerClient that additionally observes PlainBox
    specific DBus signals.

    There are two new events that can show up on the event callback:

        "job-result-available":
            This event is provided whenever a job result becomes available on
            Vthe bus. It is sent after the state on the bus settles and becomes
            mirrored locally.
        "ask-for-outcome":
            This event is provided whenever a job result with outcome equal to
            OUTCOME_UNDECIDED was produced by PlainBox and the application
            needs to ask the user how to proceed.

    The state is mirrored based on the same signals as in ObjectManagerClient,
    in addition though, two more signals are being monitored:

    Both signals are affected by this bug:
        https://bugs.launchpad.net/checkbox-ihv-ng/+bug/1236322

     - com.canonical.certification.PlainBox.Service1.JobResultAvailable
     - com.canonical.certification.PlainBox.Service1.AskForOutcome
    """

    BUS_NAME = 'com.canonical.certification.PlainBox1'

    def __init__(self, connection, event_cb):
        """
        Initialize a new PlainBoxClient

        :param connection:
            A dbus.Connection to work with
        :param event_cb:
            A callback invoked whenever an event is produced. The function is
            called at least two arguments, the instance of the client it was
            registered on and the string with the name of the event.
            Additional arguments are provided, specific to each event.
        """
        super(PlainBoxClient, self).__init__(
            connection, self.BUS_NAME, event_cb)

    def _observe_signals(self):
        """
        Internal method of ObjectManagerClient

        Unlike in ObjectManagerClient, in PlainBoxClient, it actually tells
        DBus that we want to look at ALL the signals sent on the particular bus
        name. This is less racy (one call) and gets us also the two other
        signals that plainbox currently uses.

        :returns:
            A tuple of SignalMatch instances that descibe observed signals.
        """
        match_everything = self._connection.add_signal_receiver(
            handler_function=self._on_signal,
            signal_name=None,  # match all signals
            dbus_interface=None,  # match all interfaces
            path=None,  # match all senders
            bus_name=self._bus_name,
            # extra keywords, those allow us to get meta-data to handlers
            byte_arrays=True,
            path_keyword='object_path',
            interface_keyword='interface',
            member_keyword='member')
        return (match_everything,)

    def _on_signal(self, *args, object_path, interface, member):
        """
        Internal method of ObjectManagerClient

        Dispatches each received signal to a handler function. Doing the
        dispatch here allows us to register one listener for many signals and
        then do all the routing inside tha application.

        The overidden version supports the two PlainBox-specific signals,
        relying the rest to the base class.

        :param args:
            Arguments of the original signal
        :param object_path:
            Path of the object that sent the signal
        :param interface:
            Name of the DBus interface that designates the signal
        :param member:
            Name of the DBus signal (without the interface part)
        """

        if member == "JobResultAvailable":
            return self._on_job_result_available(*args)
        elif member == "AskForOutcome":
            return self._on_ask_for_outcome(*args)
        else:
            return super(PlainBoxClient, self)._on_signal(
                *args,
                object_path=object_path, interface=interface, member=member)

    def _on_job_result_available(self, job, result):
        """
        Callback invoked when JobResultAvailable signal is received
        """
        # Notify users
        self._event_cb(self, 'job-result-available', job, result)

    def _on_ask_for_outcome(self, runner):
        """
        Callback invoked when JobResultAvailable signal is received
        """
        # Notify userz
        self._event_cb(self, 'ask-for-outcome', runner)
