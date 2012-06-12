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
import posixpath

from gettext import gettext as _
from string import Template

from gi.repository import Gtk, Gdk, Pango, PangoCairo
import cairo

from checkbox.job import UNINITIATED
from checkbox.user_interface import (UserInterface,
    NEXT, YES_ANSWER, NO_ANSWER, SKIP_ANSWER,
    ANSWER_TO_STATUS, STATUS_TO_ANSWER)

# Import to register HyperTextView type with gtk
from checkbox_gtk.hyper_text_view import HyperTextView

ANSWER_TO_BUTTON = {
    YES_ANSWER: "radio_button_yes",
    NO_ANSWER: "radio_button_no",
    SKIP_ANSWER: "radio_button_skip"}

BUTTON_TO_STATUS = dict((b, ANSWER_TO_STATUS[a])
    for a, b in ANSWER_TO_BUTTON.items())

STATUS_TO_BUTTON = dict((s, ANSWER_TO_BUTTON[a])
    for s, a in STATUS_TO_ANSWER.items())


# HACK: Setting and unsetting previous and next buttons to workaround
#       for gnome bug #56070.
class GTKHack:
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
        Gtk.Window.set_default_icon_name("checkbox")
        self.widgets = Gtk.Builder()
        self.widgets.set_translation_domain(self.gettext_domain)
        self.widgets.add_from_file(posixpath.join(data_path,
            "checkbox-gtk.ui"))
        self.widgets.connect_signals(self)

        # Set background color for head
        eventbox_head = self._get_widget("eventbox_head")
        color = Gdk.color_parse("#F0EBE2")
        #HACK: LP #839675
        if isinstance(color, tuple): color = color[1]
        eventbox_head.modify_bg(Gtk.StateType.NORMAL, color)

        # Set and apply initial/default dialog title
        self._app_title = title
        self._dialog = self._get_widget("dialog_main")
        self._dialog.set_title(self._app_title)

        #Setup and handler to render pixmap and translatable description text.
        self.IMAGE_HEAD_BACKGROUND = posixpath.join(data_path,
            "checkbox-gtk-head.png")
        self.FONT = "Ubuntu"
        self.TEXT = title

        image_head=self._get_widget("image_head")
        try:
            image_head.connect("draw",self.draw_image_head)
        except TypeError:
            #Looks like GTK+ 2.x
            image_head.connect("expose-event",self.draw_image_head)

        # Set wait transient for dialog
        self._wait = self._get_widget("box_wait")
        self._wait.hide()

        # Set shorthand for notebook
        self._notebook = self._get_widget("notebook_main")
        self._handlers = {}

    def _get_widget(self, name):
        return self.widgets.get_object(name)

    def _get_radio_button(self, map):
        for radio_button, value in map.items():
            if self._get_widget(radio_button).get_active():
                return value
        raise Exception("Failed to map radio_button.")

    def _get_label(self, name):
        widget = self._get_widget(name)
        return widget.get_label()

    def _get_text(self, name):
        widget = self._get_widget(name)
        return widget.get_text()

    def _get_text_view(self, name):
        widget = self._get_widget(name)
        buffer = widget.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
        return text

    def _set_label(self, name, label=""):
        widget = self._get_widget(name)
        widget.set_label(label)

    def _set_text(self, name, text=""):
        widget = self._get_widget(name)
        widget.set_text(text)

    def _set_text_view(self, name, text=""):
        buffer = Gtk.TextBuffer()
        buffer.set_text(text)
        widget = self._get_widget(name)
        widget.set_buffer(buffer)

    def _set_hyper_text_view(self, name, text=""):
        def clicked(widget, text, anchor, button):
            self.show_url(anchor)

        widget = self._get_widget(name)
        if widget not in self._handlers:
            self._handlers[widget] = widget.connect("anchor-clicked", clicked)

        buffer = Gtk.TextBuffer()
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

    def _set_main_title(self, test_name=None):
        title = self._app_title
        if test_name:
            title += " - %s" % test_name
        self._get_widget("dialog_main").set_title(title)

    def _set_progress(self,progress):
        # Update progress bar
        bar = self._get_widget("progressbar_test")
        if not self.progress: 
            return
        done, total = self.progress
        bar.set_text("%(done)d/%(total)d" % {'done': done, 'total': total})
        if total:
            progress_fraction = float(done) / total
        else:
            progress_fraction=0
        bar.set_fraction(progress_fraction)

    def _run_dialog(self, dialog=None):
        def on_dialog_response(dialog, response, self):
            # Keep dialog alive when the button that has been clicked
            # isn't meant to move to a previous/next window
            # To do this, please link the RESPONSE_REJECT code to such
            # button in the glade file
            if response != Gtk.ResponseType.REJECT:
                self.direction = response
                Gtk.main_quit()

        def on_dialog_key_press(dialog, event, self):
            # Ignore ESC key presses
            key = Gdk.keyval_name(event.keyval)
            if "Escape" in key:
                return True
            return False

        dialog = dialog or self._dialog
        dialog.connect("response", on_dialog_response, self)
        dialog.connect("key-press-event", on_dialog_key_press, self)
        dialog.set_default_response(NEXT)
        dialog.show()
        Gtk.main()
        if self.direction == Gtk.ResponseType.DELETE_EVENT:
            raise KeyboardInterrupt

    def show_progress_start(self, message):
        self._set_progress(self.progress)
        self._set_sensitive("button_previous", False)
        self._set_sensitive("button_next", False)

        self._set_text("label_wait", message)
        self._wait.show()

    def show_progress_stop(self):
        self._wait.hide()

        self._set_sensitive("button_previous", True)
        self._set_sensitive("button_next", True)

    def show_progress_pulse(self):
        self._get_widget("progressbar_wait").pulse()
        while Gtk.events_pending():
            Gtk.main_iteration()

    @GTKHack
    def show_text(self, text, previous=None, next=None):
        #Reset window title
        self._set_main_title()
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
    def show_entry(self, text, value, label=None, previous=None, next=None):
        #Reset window title
        self._set_main_title()
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

        entered_value = self._get_text("entry")
        self._set_text("entry","")
        return entered_value

    @GTKHack
    def show_check(self, text, options=[], default=[]):
        # Set buttons
        self._notebook.set_current_page(1)
        self._set_show("button_select_all", True)
        self._set_show("button_deselect_all", True)

        # Set options
        option_table = {}
        vbox = self._get_widget("vbox_options_list")
        for option in options:
            label = "_%s%s" % (option[0].upper(), option[1:])
            check_button = Gtk.CheckButton(label = label,
                                           use_underline = True)
            check_button.get_child().set_line_wrap(True)
            check_button.show()
            option_table[option] = check_button
            vbox.pack_start(check_button, False, False, 0)
            if option in default:
                check_button.set_active(True)

        self._set_hyper_text_view("hyper_text_view_options", text)

        # Set callbacks
        def click_button(widget, active):
            for check_button in option_table.values():
                check_button.set_active(active)

        for button_name in "button_select_all", "button_deselect_all":
            button = self._get_widget(button_name)
            button.connect("clicked", click_button,
                "deselect" not in button_name)

        self._run_dialog()

        # Unset buttons
        self._set_show("button_select_all", False)
        self._set_show("button_deselect_all", False)

        # Get options
        results = []
        for option, check_button in option_table.items():
            if check_button.get_active():
                results.append(option)
            vbox.remove(check_button)

        return results

    @GTKHack
    def show_radio(self, text, options=[], default=None):
        # Set buttons
        self._notebook.set_current_page(1)

        # Set options
        option_group = None
        option_table = {}
        vbox = self._get_widget("vbox_options_list")
        for option in options:
            label = "_%s%s" % (option[0].upper(), option[1:])
            radio_button = Gtk.RadioButton(group = option_group,
                                           label = label,
                                           use_underline = True)
            radio_button.get_child().set_line_wrap(True)
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
        result = None
        for option, radio_button in option_table.items():
            if radio_button.get_active():
                result = option
            vbox.remove(radio_button)

        return result

    @GTKHack
    def show_tree(self, text, options={}, default={}, deselect_warning=""):
        #Reset window title
        self._set_main_title()

        (COLUMN_TEXT, COLUMN_ACTIVE) = list(range(2))

        # Set buttons
        self._notebook.set_current_page(1)
        self._set_show("button_select_all", True)
        self._set_show("button_deselect_all", True)

        # Set options
        treestore = Gtk.TreeStore(str, bool)
        treeview = Gtk.TreeView()
        treeview.set_model(treestore)
        treeview.set_headers_visible(False)
        treeview.show()

        def set_options(options, default, parent=None):
            if isinstance(options, dict):
                keys = sorted(options.keys())
                values = [options[k] for k in keys]
                for text, child in zip(keys, values):
                    active = text in default
                    iter = treestore.append(parent, [text, active])
                    set_options(child, default.get(text, {}), iter)

        set_options(options, default)

        vbox = self._get_widget("vbox_options_list")
        vbox.pack_start(treeview, False, False, 0)

        def toggle_tree(iter, active=None):
            # Set value
            if active is None:
                active = not treestore.get_value(iter, COLUMN_ACTIVE)
            treestore.set_value(iter, COLUMN_ACTIVE, active)

            # Set ancestors
            def set_ancestors(iterator):
                parent_row = treestore[iterator].parent
                if active:
                    while parent_row:
                        parent_row[COLUMN_ACTIVE] = active
                        parent_row = parent_row.parent
                else:
                    while parent_row:
                        if any(child[COLUMN_ACTIVE]
                               for child in parent_row.iterchildren()):
                            break
                        parent_row[COLUMN_ACTIVE] = active
                        parent_row = parent_row.parent

            set_ancestors(iter)

            # Set children
            def set_children(iter):
                child = treestore.iter_children(iter)
                while child:
                    treestore.set_value(child, COLUMN_ACTIVE, active)
                    set_children(child)
                    child = treestore.iter_next(child)

            set_children(iter)

        # Toggle column
        cell = Gtk.CellRendererToggle()
        cell.connect("toggled",
            lambda t, p: toggle_tree(treestore.get_iter_from_string(p)))
        col = Gtk.TreeViewColumn(None, cell, active=COLUMN_ACTIVE)
        treeview.append_column(col)

        # Text column
        cell = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn(None, cell, text=COLUMN_TEXT)
        treeview.append_column(col)

        # Select and deselect buttons
        def click_button(widget, active):
            iter = treestore.get_iter_first()
            while iter:
                toggle_tree(iter, active)
                iter = treestore.iter_next(iter)

        for button_name in "button_select_all", "button_deselect_all":
            button = self._get_widget(button_name)
            button.connect("clicked", click_button,
                "deselect" not in button_name)

        self._set_hyper_text_view("hyper_text_view_options", text)
        self._run_dialog()

        # Unset buttons
        self._set_show("button_select_all", False)
        self._set_show("button_deselect_all", False)

        # Get options
        def get_results(iter):
            results = {}
            while iter:
                active = treestore.get_value(iter, COLUMN_ACTIVE)
                if active:
                    text = treestore.get_value(iter, COLUMN_TEXT)
                    children = treestore.iter_children(iter)
                    results[text] = get_results(children)

                iter = treestore.iter_next(iter)

            return results

        results = get_results(treestore.get_iter_first())
        vbox.remove(treeview)

        return results

    def _run_test(self, test, runner):
        self._set_sensitive("button_test", False)

        (status, data, duration) = runner(test)

        description = Template(test["description"]).substitute({
            "output": data.strip()})
        self._set_hyper_text_view("hyper_text_view_test", description)

        self._set_active(STATUS_TO_BUTTON[status])
        self._set_label("button_test", _("_Test Again"))
        self._set_sensitive("button_test", True)

    @GTKHack
    def show_test(self, test, runner):
        #Set window title to reflect current test
        self._set_main_title(test["name"])

        self._set_sensitive("button_test", False)
        self._notebook.set_current_page(2)


        # Set test description
        if re.search(r"\$output", test["description"]):
            self._run_test(test, runner)
        else:
            self._set_hyper_text_view("hyper_text_view_test",
                test["description"])

        self._set_progress(self.progress) 
        # Set buttons
        if "command" in test:
            self._set_sensitive("button_test", True)
            button_test = self._get_widget("button_test")
            if button_test in self._handlers:
                button_test.disconnect(self._handlers[button_test])
            self._handlers[button_test] = button_test.connect("clicked",
                lambda w, t=test, r=runner: self._run_test(t, r))

        self._set_text_view("text_view_comment", test.get("data", ""))
        self._set_active(STATUS_TO_BUTTON[test.get("status", UNINITIATED)])

        self._run_dialog()

        # Reset labels
        self._set_hyper_text_view("hyper_text_view_test")
        self._set_label("button_test", _("_Test"))

        test["data"] = self._get_text_view("text_view_comment")
        test["status"] = self._get_radio_button(BUTTON_TO_STATUS)

        self._set_main_title()

    def show_info(self, text, options=[], default=None):
        message_dialog = Gtk.MessageDialog(parent=self._dialog,
            type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.NONE,
            message_format=text)
        message_dialog.set_modal(True)
        message_dialog.set_title(_("Info"))
        message_dialog.connect("realize", lambda x: \
            x.get_window().set_functions(Gdk.WMFunction.MOVE))

        if default:
            # We have a default, move it to the end of the button list
            options.remove(default)
            options.append(default)
        for index, option in enumerate(options):
            message_dialog.add_button(option, index)

        self._run_dialog(message_dialog)
        message_dialog.hide()

        response = self.direction
        self.direction = NEXT
        return options[response]

    def show_error(self, primary_text,
                   secondary_text=None, detailed_text=None):
        message_dialog = Gtk.MessageDialog(parent=self._dialog,
            type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.NONE,
            message_format=primary_text)
        message_dialog.set_modal(True)
        message_dialog.set_title(_("Error"))
        message_dialog.set_default_response(NEXT)
        message_dialog.add_buttons(Gtk.STOCK_CLOSE, NEXT)
        if secondary_text:
            message_dialog.format_secondary_text(secondary_text)
        if detailed_text:
            content_area = message_dialog.get_content_area()

            expander = Gtk.Expander(label=_('Detailed information...'))

            def expanded_cb(expander, *args):
                message_dialog.set_resizable(expander.get_expanded())
            expander.connect("notify::expanded", expanded_cb)
            scrolled_window = Gtk.ScrolledWindow()
            textview = Gtk.TextView()
            textview.set_editable(False)
            textview.get_buffer().set_text(detailed_text)
            scrolled_window.add(textview)
            expander.add(scrolled_window)
            content_area.pack_start(expander,
                                    expand=True, fill=True, padding=0)
        message_dialog.show_all()
        self._run_dialog(message_dialog)
        message_dialog.hide()

    def draw_image_head(self, widget, data):
        #Render the background we read from an image
        background_image = cairo.ImageSurface.create_from_png(
                self.IMAGE_HEAD_BACKGROUND)
        cairo_drawing_context = Gdk.cairo_create(widget.get_window())
        cairo_drawing_context.set_source_surface(background_image,0,0)
        cairo_drawing_context.paint()
        #Text rendering with Pango is more involved but potentially
        #better for l10n and i18n purposes
        font_description = Pango.FontDescription()
        font_description.set_family(self.FONT)
        font_description.set_weight(Pango.Weight.NORMAL)
        font_description.set_absolute_size(12 * Pango.SCALE)

        pango_drawing_context = widget.get_pango_context()
        pango_text_layout = Pango.Layout(context=pango_drawing_context)
        pango_text_layout.set_font_description(font_description)
        pango_text_layout.set_text(self.TEXT, -1)

        #Color to render text
        cairo_drawing_context.set_source_rgb(0,0,0)
        #Position to render text
        cairo_drawing_context.move_to(75,45)
        PangoCairo.show_layout(cairo_drawing_context,pango_text_layout)
