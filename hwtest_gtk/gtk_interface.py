import os.path, sys
import gtk, gtk.glade

from hwtest.lib.environ import add_variable, remove_variable

from hwtest.answer import Answer
from hwtest.user_interface import UserInterface


class GTKInterface(UserInterface):

    def __init__(self, config):
        super(GTKInterface, self).__init__(config)

        # load UI
        gtk.window_set_default_icon_name("hwtest")
        gtk.glade.textdomain(self.gettext_domain)
        self.widgets = gtk.glade.XML(os.path.join(config.gtk_path,
            "hwtest-gtk.glade"))
        self.widgets.signal_autoconnect(self)

        self._dialog = self._get_widget("dialog_hwtest")
        self._dialog.set_title(config.title)

        self._notebook = self._get_widget("notebook_hwtest")

    def _get_widget(self, widget):
        return self.widgets.get_widget(widget)

    def _get_radiobutton(self, map):
        for radiobutton, value in map.items():
            if self._get_widget(radiobutton).get_active():
                return value
        raise Exception, "failed to map radiobutton"

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

    def show_wait_begin(self, message):
        self._set_sensitive("button_previous", False)
        self._set_sensitive("button_next", False)

        self._set_text("label_wait", message)
        self._notebook.set_current_page(3)

        self._dialog.show()

    def show_wait_end(self):
        self._set_sensitive("button_previous", True)
        self._set_sensitive("button_next", True)

    def show_pulse(self):
        self._get_widget("progressbar_wait").pulse()
        self._get_widget("progressbar_question").pulse()
        while gtk.events_pending():
            gtk.main_iteration(False)

    def show_intro(self, title, text):
        # Set buttons
        self._set_sensitive("button_previous", False)
        self._notebook.set_current_page(0)

        markup = "<b>%s</b>" % title
        self._set_markup("label_intro_title", markup)
        self._set_text("label_intro_text", text)

        self._run_dialog()

        self._set_sensitive("button_previous", True)

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

    def show_question_begin(self, message=None):
        # Set buttons
        self._set_sensitive("button_previous", False)
        self._set_sensitive("button_next", False)
        self._set_show("button_test_again", False)

        # Set interface
        self._set_text("label_question", message)
        self._set_show("progressbar_question")
        self._notebook.set_current_page(2)

        self._dialog.show()

    def show_question_end(self, question):
        # Set buttons
        self._set_sensitive("button_previous", True)
        self._set_sensitive("button_next", True)
        self._set_show("button_test_again", str(question.command))

        # Set interface
        self._set_text("label_question", str(question.description))
        self._set_show("progressbar_question", False)
        self._notebook.set_current_page(2)

        # Set test again button
        button_test_again = self._get_widget("button_test_again")
        if hasattr(self, "handler_id"):
            button_test_again.disconnect(self.handler_id)
        self.handler_id = button_test_again.connect("clicked",
            lambda w, question=question: self.do_question(
                 "Running question %s..." % question.name,
                 question))

        # Default answers
        if question.answer:
            answer = question.answer
            self._set_textview("textview_comment", answer.data)
            self._set_active("radiobutton_%s" % answer.status)
        else:
            self._set_textview("textview_comment", "")
            self._set_active("radiobutton_skip")

        self._run_dialog()

        status = self._get_radiobutton({
            "radiobutton_yes": "yes",
            "radiobutton_no": "no",
            "radiobutton_skip": "skip"})
        data = self._get_textview("textview_comment")
        question.answer = Answer(status, data)

    def show_exchange(self, authentication, message=None, error=None):
        self._notebook.set_current_page(4)

        if authentication is not None:
            self._set_text("entry_authentication", authentication)

        if message is not None:
            self._set_markup("label_exchange", message)

        if error is not None:
            markup= "<span color='#FF0000'><b>%s</b></span>" % error
            self._set_markup("label_exchange_error", markup)
        else:
            self._set_markup("label_exchange_error")

        self._run_dialog()
        authentication = self._get_text("entry_authentication")

        return authentication

    def show_final(self, message=None):
        self._set_label("button_next", "_Finish")
        self._notebook.set_current_page(5)

        if message is not None:
            self._set_markup("label_final", message)

        self._run_dialog()

        self._set_label("button_next", "Ne_xt")

    def show_error(self, title, text):
        md = gtk.MessageDialog(type=gtk.MESSAGE_ERROR,
            buttons=gtk.BUTTONS_CLOSE, message_format=text)
        md.set_title(title)
        md.run()
        md.hide()
        while gtk.events_pending():
            gtk.main_iteration(False)

    def on_dialog_hwtest_delete(self, widget, event=None):
        sys.exit(0)
        return True
