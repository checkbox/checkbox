#
# This file is part of Checkbox.
#
# Copyright 2008 Canonical Ltd.
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
from gi.repository import Gtk, GObject, Pango, Gdk


class HyperTextView(Gtk.TextView):
    __gtype_name__ = "HyperTextView"
    __gsignals__ = {"anchor-clicked": (GObject.SignalFlags.RUN_LAST, GObject.TYPE_NONE, (str, str, int))}
    __gproperties__ = {
        "link":  (GObject.TYPE_PYOBJECT, "link color", "link color of TextView", GObject.PARAM_READWRITE),
        "active":(GObject.TYPE_PYOBJECT, "active color", "active color of TextView", GObject.PARAM_READWRITE),
        "hover": (GObject.TYPE_PYOBJECT, "link:hover color", "link:hover color of TextView", GObject.PARAM_READWRITE),
        }

    def do_get_property(self, prop):
        try:
            return getattr(self, prop.name)
        except AttributeError:
            raise AttributeError("unknown property %s" % prop.name)

    def do_set_property(self, prop, val):
        if prop.name in list(self.__gproperties__.keys()):
            setattr(self, prop.name, val)
        else:
            raise AttributeError("unknown property %s" % prop.name)

    def __init__(self, buffer=None):
        super(HyperTextView, self).__init__(buffer=buffer)
        self.link   = {"foreground": "blue", "underline": Pango.Underline.SINGLE}
        self.active = {"foreground": "red", "underline": Pango.Underline.SINGLE}
        self.hover  = {"foreground": "dark blue", "underline": Pango.Underline.SINGLE}

        self.set_editable(False)
        self.set_cursor_visible(False)

        self.__tags = []

        self.connect("motion-notify-event", self._motion)
        self.connect("focus-out-event", lambda w, e: self.get_buffer().get_tag_table().foreach(self.__tag_reset, e.window))

    def insert(self, text, _iter=None):
        b = self.get_buffer()
        if _iter is None:
            _iter = b.get_end_iter()
        b.insert(_iter, text)

    def insert_with_anchor(self, text, anchor=None, _iter=None):
        b = self.get_buffer()
        if _iter is None:
            _iter = b.get_end_iter()
        if anchor is None:
            anchor = text

        tag = b.create_tag(None, **self.get_property("link"))
        tag.set_data("is_anchor", True)
        tag.connect("event", self._tag_event, text, anchor)
        self.__tags.append(tag)
        b.insert_with_tags(_iter, text, tag)

    def _motion(self, view, ev):
        window = ev.window
        _, x, y, _ = window.get_pointer()
        x, y = view.window_to_buffer_coords(Gtk.TextWindowType.TEXT, x, y)
        tags = view.get_iter_at_location(x, y).get_tags()
        for tag in tags:
            if tag.get_data("is_anchor"):
                for t in set(self.__tags) - set([tag]):
                    self.__tag_reset(t, window)
                self.__set_anchor(window, tag, Gdk.Cursor.new(Gdk.CursorType.HAND2), self.get_property("hover"))
                break
        else:
            tag_table = self.get_buffer().get_tag_table()
            tag_table.foreach(self.__tag_reset, window)

    def _tag_event(self, tag, view, ev, _iter, text, anchor):
        _type = ev.type
        if _type == Gdk.EventType.MOTION_NOTIFY:
            return
        elif _type in [Gdk.EventType.BUTTON_PRESS, Gdk.EventType.BUTTON_RELEASE]:
            button = ev.button
            cursor = Gdk.Cursor.new(Gdk.CursorType.HAND2)
            if _type == Gdk.EventType.BUTTON_RELEASE:
                self.emit("anchor-clicked", text, anchor, button.button)
                self.__set_anchor(ev.window, tag, cursor, self.get_property("hover"))
            elif button in [1, 2]:
                self.__set_anchor(ev.window, tag, cursor, self.get_property("active"))

    def __tag_reset(self, tag, window):
        if tag.get_data("is_anchor"):
            self.__set_anchor(window, tag, None, self.get_property("link"))

    def __set_anchor(self, window, tag, cursor, prop):
        window.set_cursor(cursor)
        for key, val in prop.items():
            if val is not None:
                tag.set_property(key, val)

GObject.type_register(HyperTextView)
