#
# This file is part of Checkbox.
#
# Copyright 2010-12 Canonical Ltd.
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.
#
__metaclass__ = type

__all__ = [
    "Dispatcher",
    "DispatcherList",
    "DispatcherQueue",
    ]

import logging

from itertools import product


class Event:
    """Event payload containing the positional and keywoard arguments
    passed to the handler in the event listener."""

    def __init__(self, type, *args, **kwargs):
        self.type = type
        self.args = args
        self.kwargs = kwargs


class Listener:
    """Event listener notified when events are published by the dispatcher."""

    def __init__(self, event_type, handler, count):
        self.event_type = event_type
        self.handler = handler
        self.count = count

    def notify(self, event):
        """Notify the handler with the payload of the event.

        :param event: The event containint the payload for the handler.
        """
        if self.count is None or self.count:
            self.handler(*event.args, **event.kwargs)
            if self.count:
                self.count -= 1


class ListenerList(Listener):
    """Event listener notified for lists of events."""

    def __init__(self, *args, **kwargs):
        super(ListenerList, self).__init__(*args, **kwargs)
        self.event_types = set(self.event_type)
        self.kwargs = {}

    def notify(self, event):
        """Only notify the handler when all the events for this listener
        have been published by the dispatcher. When duplicate events
        occur, the latest event is preserved and the previous one are
        overwritten until all events have been published.
        """
        if self.count is None or self.count:
            self.kwargs[event.type] = event.args[0]
            if self.event_types.issubset(self.kwargs):
                self.handler(**self.kwargs)
                if self.count:
                    self.count -= 1


class ListenerQueue(ListenerList):

    def notify(self, event):
        """Only notify the handler when all the events for this listener
        have been published by the dispatcher. Duplicate events are enqueued
        and dequeued only when all events have been published.
        """
        arg = event.args[0]
        queue = self.kwargs.setdefault(event.type, [])

        # Strip duplicates from the queue.
        if arg not in queue:
            queue.append(arg)

        # Once the queue has handler has been called, the queue
        # then behaves like a list using the latest events.
        if self.event_types.issubset(self.kwargs):
            self.notify = notify = super(ListenerQueue, self).notify
            keys = list(self.kwargs.keys())
            for values in product(*list(self.kwargs.values())):
                self.kwargs = dict(list(zip(keys, values)))
                notify(event)


class Dispatcher:
    """Register handlers and publish events for them identified by strings."""

    listener_factory = Listener

    def __init__(self, listener_factory=None):
        self._event_listeners = {}

        if listener_factory is not None:
            self.listener_factory = listener_factory

    def registerHandler(self, event_type, handler, count=None):
        """Register an event handler and return its listener.

        :param event_type: The name of the event type to handle.
        :param handler: The function handling the given event type.
        :param count: Optionally, the number times to call the handler.
        """
        listener = self.listener_factory(event_type, handler, count)

        listeners = self._event_listeners.setdefault(event_type, [])
        listeners.append(listener)

        return listener

    def unregisterHandler(self, handler):
        """Unregister a handler.

        :param handler: The handler to unregister.
        """
        for event_type, listeners in self._event_listeners.items():
            listeners = [
                listener for listener in listeners
                if listener.handler == handler]
            if listeners:
                self._event_listeners[event_type] = listeners
            else:
                del self._event_listeners[event_type]

    def unregisterListener(self, listener, event_type=None):
        """Unregister a listener.

        :param listener: The listener of the handler to unregister.
        :param event_type: Optionally, the event_type to unregister.
        """
        if event_type is None:
            event_type = listener.event_type

        self._event_listeners[event_type].remove(listener)
        if not self._event_listeners[event_type]:
            del self._event_listeners[event_type]

    def publishEvent(self, event_type, *args, **kwargs):
        """Publish an event of a given type and notify all listeners.

        :param event_type: The name of the event type to publish.
        :param args: Positional arguments to pass to the registered handlers.
        :param kwargs: Keyword arguments to pass to the registered handlers.
        """
        if event_type in self._event_listeners:
            event = Event(event_type, *args, **kwargs)
            for listener in list(self._event_listeners[event_type]):
                try:
                    listener.notify(event)
                    if listener.count is not None and not listener.count:
                        self.unregisterListener(listener)
                except:
                    logging.exception(
                        "Error running event handler for %r with args %r %r",
                        event_type, args, kwargs)


class DispatcherList(Dispatcher):
    """
    Register handlers and publish events for them identified by lists
    of strings.
    """

    listener_factory = ListenerList

    def registerHandler(self, event_types, handler, count=None):
        """See Dispatcher."""
        if not isinstance(event_types, (list, tuple)):
            event_types = (event_types,)

        listener = self.listener_factory(event_types, handler, count)
        for event_type in event_types:
            listeners = self._event_listeners.setdefault(event_type, [])
            listeners.append(listener)

        return listener

    def unregisterListener(self, listener):
        """See Dispatcher."""
        for event_type in listener.event_types:
            super(DispatcherList, self).unregisterListener(
                listener, event_type)

    def publishEvent(self, event_type, arg):
        """See Dispatcher."""
        super(DispatcherList, self).publishEvent(event_type, arg)


class DispatcherQueue(DispatcherList):
    """
    Register handlers and publish events for them identified by lists
    of strings in queue order.
    """

    listener_factory = ListenerQueue
