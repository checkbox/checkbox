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
import re
import gtk, gtk.glade
import posixpath

from gettext import gettext as _

from checkbox.test import ALL_STATUS, TestResult
from checkbox.user_interface import UserInterface

# Import to register HyperTextView type with gtk
from checkbox_gtk.hyper_text_view import HyperTextView


# HACK: Setting and unsetting previous and next buttons to workaround
#       for gnome bug #56070.
class GTKHack(object):
    def __init__(self, function):
        self._function = function

    def __get__(self, instance, cls=None):
        self._instance = instance
        return self

    def __call__(self, *args, **kwargs):
        self._instance._set_sensitive("button_previous", False)
        self._instance._set_sensitive("button_next", False)
        self._instance._set_sensitive("button_previous", True)
        self._instance._set_sensitive("button_next", True)
        return self._function(self._instance, *args, **kwargs)


class GTKInterface(UserInterface):

    def __init__(self, title, data_path):
        super(GTKInterface, self).__init__(title, data_path)

        # Load UI
        gtk.window_set_default_icon_name("checkbox")
        gtk.glade.textdomain(self.gettext_domain)
        self.widgets = gtk.glade.XML(posixpath.join(data_path,
            "checkbox-gtk.glade"))
        self.widgets.signal_autoconnect(self)

        # Set background color for head
        eventbox_head = self._get_widget("eventbox_head")
        eventbox_head.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))

        # Set dialog title
        self._dialog = self._get_widget("dialog_main")
        self._dialog.set_title(title)

        # Set wait transient for dialog
        self._wait = self._get_widget("window_wait")
        self._wait.set_transient_for(self._dialog)
        self._wait.realize()
        self._wait.window.set_functions(gtk.gdk.FUNC_MOVE)

        # Set shorthand for notebook
        self._notebook = self._get_widget("notebook_main")
        self._handler_id = None

    def _get_widget(self, name):
        return self.widgets.get_widget(name)

    def _get_radio_button(self, map):
        for radio_button, value in map.items():
            if self._get_widget(radio_button).get_active():
                return value
        raise Exception, "Failed to map radio_button."

    def _get_label(self, name):
        widget = self._get_widget(name)
        return widget.get_label()

    def _get_text(self, name):
        widget = self._get_widget(name)
        return widget.get_text()

    def _get_text_view(self, name):
        widget = self._get_widget(name)
        buffer = widget.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())
        return text

    def _set_label(self, name, label=""):
        widget = self._get_widget(name)
        widget.set_label(label)

    def _set_text(self, name, text=""):
        widget = self._get_widget(name)
        widget.set_text(text)

    def _set_text_view(self, name, text=""):
        buffer = gtk.TextBuffer()
        buffer.set_text(text)
        widget = self._get_widget(name)
        widget.set_buffer(buffer)

    def _set_hyper_text_view(self, name, text=""):
        def clicked(widget, text, anchor, button):
            self.show_url(anchor)

        widget = self._get_widget(name)
        widget.connect("anchor-clicked", clicked)

        buffer = gtk.TextBuffer()
        widget.set_buffer(buffer)

        url_regex = r"https?://[^\s]+"
        tag_regex = r"\[\[[^\]]+\]\]"
        in_hyper_text = False
        for part in re.split(r"(%s|%s)" % (url_regex, tag_regex), text):
            if in_hyper_text:
                in_hyper_text = False
                anchor = part
                if re.match("^%s$" % tag_regex, part):
                    part = part.lstrip("[").rstrip("]")
                    if "|" in part:
                        (anchor, part) = part.split("|", 1)
                widget.insert_with_anchor(part, anchor)
            else:
                in_hyper_text = True
                widget.insert(part)

    def _set_active(self, name, value=True):
        widget = self._get_widget(name)
        widget.set_active(bool(value))

    def _set_show(self, name, value=True):
        widget = self._get_widget(name)
        if value:
            widget.show()
        else:
            widget.hide()

    def _set_sensitive(self, name, value=True):
        # Hack to workaround Gnome bug #56070
        self._set_show(name, False)
        self._set_show(name, True)

        widget = self._get_widget(name)
        widget.set_sensitive(bool(value))

    def _set_button(self, name, value=None):
        if value is None:
            state = value
        else:
            state = self._get_label(name)
            if value == "":
                self._set_sensitive(name, False)
            else:
                self._set_sensitive(name, True)
                self._set_label(name, value)

        return state

    def _run_dialog(self, dialog=None):
        def on_dialog_response(dialog, response, self):
            self.direction = response
            gtk.main_quit()

        dialog = dialog or self._dialog
        dialog.connect("response", on_dialog_response, self)
        dialog.show()
        gtk.main()
        if self.direction == gtk.RESPONSE_DELETE_EVENT:
            raise KeyboardInterrupt

    def do_function(self, function, *args, **kwargs):
        self._set_sensitive("button_previous", False)
        self._set_sensitive("button_next", False)

        result = super(GTKInterface, self).do_function(function,
            *args, **kwargs)

        self._set_sensitive("button_previous", True)
        self._set_sensitive("button_next", True)

        return result

    def show_wait(self, message, function, *args, **kwargs):
        self._set_text("label_wait", message)
        self._wait.show()

        result = self.do_function(function, *args, **kwargs)

        self._wait.hide()
        return result

    def show_pulse(self):
        self._get_widget("progressbar_wait").pulse()
        while gtk.events_pending():
            gtk.main_iteration()

    @GTKHack
    def show_text(self, text, previous=None, next=None):
        # Set buttons
        previous_state = self._set_button("button_previous", previous)
        next_state = self._set_button("button_next", next)

        self._notebook.set_current_page(0)

        self._set_hyper_text_view("hyper_text_view_text", text)

        self._run_dialog()

        # Unset buttons
        self._set_button("button_previous", previous_state)
        self._set_button("button_next", next_state)

    @GTKHack
    def show_entry(self, text, value, previous=None, next=None):
        # Set buttons
        previous_state = self._set_button("button_previous", previous)
        next_state = self._set_button("button_next", next)

        self._notebook.set_current_page(3)

        if value is not None:
            self._set_text("entry", value)

        self._set_hyper_text_view("hyper_text_view_entry", text)

        self._run_dialog()

        # Unset buttons
        self._set_button("button_previous", previous_state)
        self._set_button("button_next", next_state)

        return self._get_text("entry")

    @GTKHack
    def show_options(self, text, options=[], default=None):
        # Set buttons
        self._notebook.set_current_page(1)

        # Set options
        option_group = None
        option_table = {}
        vbox = self._get_widget("vbox_options")
        for option in options:
            label = "_%s" % option.capitalize()
            radio_button = gtk.RadioButton(option_group, label)
            radio_button.show()
            option_table[option] = radio_button
            vbox.pack_start(radio_button, False, False, 0)
            if option_group is None:
                option_group = radio_button
            if option == default:
                radio_button.set_active(True)

        self._set_hyper_text_view("hyper_text_view_options", text)

        self._run_dialog()

        # Get option
        for option, radio_button in option_table.items():
            if radio_button.get_active():
                return option

    def _run_test(self, test):
        self._set_sensitive("button_test", False)

        message = _("Running test %s...") % test.name
        result = self.show_wait(message, test.command)

        description = self.do_function(test.description, result)
        self._set_hyper_text_view("hyper_text_view_test", description)

        self._set_active("radio_button_%s" % result.status)
        self._set_sensitive("button_test", True)
        self._set_label("button_test", _("_Test Again"))

    @GTKHack
    def show_test(self, test, result=None):
        self._set_sensitive("button_test", False)
        self._notebook.set_current_page(2)

        # Set test description
        description = self.do_function(test.description, result)
        self._set_hyper_text_view("hyper_text_view_test", description)

        # Set buttons
        if str(test.command):
            self._set_sensitive("button_test", True)

            button_test = self._get_widget("button_test")
            if self._handler_id:
                button_test.disconnect(self._handler_id)
            self._handler_id = button_test.connect("clicked",
                lambda w, t=test: self._run_test(t))

        # Default results
        if result:
            self._set_text_view("text_view_comment", result.data)
            self._set_active("radio_button_%s" % result.status)
        else:
            self._set_text_view("text_view_comment")
            self._set_active("radio_button_skip")

        self._run_dialog()

        # Reset labels
        self._set_hyper_text_view("hyper_text_view_test")
        self._set_label("button_test", _("_Test"))

        radio_buttons = ["radio_button_%s" % s for s in ALL_STATUS]
        status = self._get_radio_button(dict(zip(radio_buttons, ALL_STATUS)))
        data = self._get_text_view("text_view_comment")
        return TestResult(test, status, data)

    def show_error(self, text):
        message_dialog = gtk.MessageDialog(parent=self._dialog,
            type=gtk.MESSAGE_ERROR,
            buttons=gtk.BUTTONS_CLOSE,
            message_format=text)
        message_dialog.set_modal(True)
        message_dialog.set_title(_("Error"))
        self._run_dialog(message_dialog)
        message_dialog.hide()
