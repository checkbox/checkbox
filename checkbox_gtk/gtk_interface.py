#
# Copyright (c) 2008 Canonical
#
# Written by Marc Tardif <marc@interunion.ca>
#
# This file is part of Checkbox.
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
import os
import sys
import gtk, gtk.glade

from gettext import gettext as _

from checkbox.result import Result, FAIL, PASS, SKIP
from checkbox.user_interface import UserInterface


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

    def __init__(self, config):
        super(GTKInterface, self).__init__(config)

        # load UI
        gtk.window_set_default_icon_name("checkbox")
        gtk.glade.textdomain(self.gettext_domain)
        self.widgets = gtk.glade.XML(os.path.join(config.gtk_path,
            "checkbox-gtk.glade"))
        self.widgets.signal_autoconnect(self)

        self._dialog = self._get_widget("dialog_checkbox")
        self._dialog.set_title(config.title)

        self._notebook = self._get_widget("notebook_checkbox")
        self._handler_id = None

    def _get_widget(self, widget):
        return self.widgets.get_widget(widget)

    def _get_radiobutton(self, map):
        for radiobutton, value in map.items():
            if self._get_widget(radiobutton).get_active():
                return value
        raise Exception, "Failed to map radiobutton."

    def _get_text(self, name):
        widget = self._get_widget(name)
        return widget.get_text()

    def _get_textview(self, name):
        widget = self._get_widget(name)
        buffer = widget.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())
        return text

    def _set_label(self, name, label=""):
        widget = self._get_widget(name)
        widget.set_label(label)

    def _set_markup(self, name, markup=""):
        widget = self._get_widget(name)
        widget.set_markup(markup)

    def _set_text(self, name, text=""):
        widget = self._get_widget(name)
        widget.set_text(text)

    def _set_textview(self, name, text=""):
        buffer = gtk.TextBuffer()
        buffer.set_text(text)
        widget = self._get_widget(name)
        widget.set_buffer(buffer)

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

    def _run_dialog(self):
        self.direction = self._dialog.run()
        while gtk.events_pending():
            gtk.main_iteration(False)

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
        self._notebook.set_current_page(3)
        self._dialog.show()

        self.do_function(function, *args, **kwargs)

    def show_pulse(self):
        self._get_widget("progressbar_wait").pulse()
        self._get_widget("progressbar_test").pulse()
        while gtk.events_pending():
            gtk.main_iteration(False)

    @GTKHack
    def show_intro(self, title, text):
        # Set buttons
        self._set_sensitive("button_previous", False)
        self._notebook.set_current_page(0)

        markup = "<b>%s</b>" % title
        self._set_markup("label_intro_title", markup)
        self._set_text("label_intro_text", text)

        self._run_dialog()

        self._set_sensitive("button_previous", True)

    @GTKHack
    def show_category(self, title, text, category=None):
        # Set buttons
        self._notebook.set_current_page(1)

        self._set_text("label_category", text)
        if category:
            self._set_active("radiobutton_%s" % category)

        self._run_dialog()

        return self._get_radiobutton({
            "radiobutton_desktop": "desktop",
            "radiobutton_laptop": "laptop",
            "radiobutton_server": "server"})

    @GTKHack
    def show_test(self, test, result=None):
        self._set_show("button_test", False)
        self._notebook.set_current_page(2)

        # Run test
        if str(test.command):
            self._set_text("label_test",
                _("Running test: %s") % test.name)
            self._set_show("progressbar_test")
            self._dialog.show()

            command_result = self.do_function(test.command)

            self._set_show("progressbar_test", False)
        else:
            command_result = None

        # Set test
        self._set_text("label_test", test.description(command_result).data)

        # Set buttons
        if str(test.command):
            self._set_show("button_test", True)

            button_test = self._get_widget("button_test")
            if self._handler_id:
                button_test.disconnect(self._handler_id)
            self._handler_id = button_test.connect("clicked",
                lambda w, t=test: self.show_test(t))

        # Default results
        if result:
            self._set_textview("textview_comment", result.data)
            answer = {PASS: "yes", FAIL: "no", SKIP: "skip"}[result.status]
            self._set_active("radiobutton_%s" % answer)
        else:
            self._set_textview("textview_comment", "")
            self._set_active("radiobutton_skip")

        self._run_dialog()

        status = self._get_radiobutton({
            "radiobutton_yes": PASS,
            "radiobutton_no": FAIL,
            "radiobutton_skip": SKIP})
        data = self._get_textview("textview_comment")
        return Result(test, status=status, data=data)

    @GTKHack
    def show_exchange(self, authentication, reports=[], message=None,
                      error=None):
        self._notebook.set_current_page(4)

        if authentication is not None:
            self._set_text("entry_authentication", authentication)

        all_reports = ["distribution", "devices", "processors",
                       "packages", "tests"]
        for report in all_reports:
            self._set_show("label_%s" % report, report in reports)

        if message is not None:
            self._set_markup("label_exchange", message)

        if error is not None:
            self.show_error(_("Exchange"), error)

        self._run_dialog()

        authentication = self._get_text("entry_authentication")

        return authentication

    @GTKHack
    def show_final(self, message=None):
        self._set_label("button_next", _("_Finish"))
        self._notebook.set_current_page(5)

        if message is not None:
            self._set_markup("label_final", message)

        self._run_dialog()

        self._set_label("button_next", _("Ne_xt"))

    def show_error(self, title, text):
        md = gtk.MessageDialog(type=gtk.MESSAGE_ERROR,
            buttons=gtk.BUTTONS_CLOSE, message_format=text)
        md.set_title(title)
        md.run()
        md.hide()
        while gtk.events_pending():
            gtk.main_iteration(False)

    def on_dialog_checkbox_delete(self, widget, event=None):
        sys.exit(0)
        return True
