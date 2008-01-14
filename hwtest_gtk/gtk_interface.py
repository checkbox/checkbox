import os.path, sys
import gtk, gtk.glade

from hwtest.lib.environ import add_variable, remove_variable
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

    def _set_label(self, name, text):
        widget = self._get_widget(name)
        widget.set_text(text)

    def _set_text(self, name, text):
        widget = self._get_widget(name)
        widget.set_text(text)

    def _set_textview(self, name, text):
        buffer = gtk.TextBuffer()
        buffer.set_text(text)
        widget = self._get_widget(name)
        widget.set_buffer(buffer)

    def _set_active(self, name, boolean):
        widget = self._get_widget(name)
        widget.set_active(bool(boolean))

    def _set_sensitive(self, name, boolean):
        widget = self._get_widget(name)
        widget.set_sensitive(bool(boolean))

    def _run_dialog(self):
        self.direction = self._dialog.run()
        while gtk.events_pending():
            gtk.main_iteration(False)

    def _run_question(self, question):
        question.run()
        self._set_label("label_question", question.description)

    def show_wait(self, message=None):
        self._set_sensitive("button_previous", False)
        self._set_sensitive("button_next", False)

        self._set_label("label_wait", message)
        self._get_widget("progressbar_wait").set_fraction(0)
        self._notebook.set_current_page(3)

        self._dialog.show()

    def show_wait_end(self):
        self._set_sensitive("button_previous", True)
        self._set_sensitive("button_next", True)

    def show_pulse(self):
        self._get_widget("progressbar_wait").pulse()
        while gtk.events_pending():
            gtk.main_iteration(False)

    def show_intro(self):
        # Set buttons
        self._set_sensitive("button_previous", False)
        self._notebook.set_current_page(0)

        self._run_dialog()

        self._set_sensitive("button_previous", True)

    def show_category(self, category=None):
        # Set buttons
        self._notebook.set_current_page(1)

        if category:
            self._set_active("radiobutton_%s" % category, True)

        self._run_dialog()

        return self._get_radiobutton({
            "radiobutton_desktop": "desktop",
            "radiobutton_laptop": "laptop",
            "radiobutton_server": "server"})

    def show_question(self, question, has_prev=True, has_next=True):
        # Set buttons
        self._set_sensitive("button_test_again", question.command)
        self._notebook.set_current_page(2)

        # Set test again button
        button_test_again = self._get_widget("button_test_again")
        if hasattr(self, "handler_id"):
            button_test_again.disconnect(self.handler_id)
        self.handler_id = button_test_again.connect("clicked",
            lambda w, question=question: self._run_question(question))

        # Default answers
        if question.answer:
            answer = question.answer
            self._set_textview("textview_comment", answer.data)
            self._set_active("radiobutton_%s" % answer.status, True)
        else:
            self._set_textview("textview_comment", "")
            self._set_active("radiobutton_skip", True)

        self._run_question(question)
        self._run_dialog()

        status = self._get_radiobutton({
            "radiobutton_yes": "yes",
            "radiobutton_no": "no",
            "radiobutton_skip": "skip"})
        data = self._get_textview("textview_comment")
        question.set_answer(status, data)

    def show_exchange(self, authentication, message=None, error=None):
        self._notebook.set_current_page(4)
        self._set_text("entry_authentication", authentication)

        if message is not None:
            self._get_widget("label_exchange").set_markup(message)

        if error is not None:
            markup= "<span color='#FF0000'><b>%s</b></span>" % error
            self._get_widget("label_exchange_error").set_markup(markup)

        self._run_dialog()
        authentication = self._get_text("entry_authentication")

        return authentication

    def show_final(self, message=None):
        self._notebook.set_current_page(5)

        if message is not None:
            self._get_widget("label_final").set_markup(message)

        self._run_dialog()

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
