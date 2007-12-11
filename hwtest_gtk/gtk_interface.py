import os.path, sys
import gtk, gtk.glade

from hwtest.lib.environ import add_variable, remove_variable
from hwtest.user_interface import UserInterface


class GTKInterface(UserInterface):

    def __init__(self, config):
        super(GTKInterface, self).__init__()

        # load UI
        gtk.window_set_default_icon_name("hwtest")
        gtk.glade.textdomain(self.gettext_domain)
        self.widgets = gtk.glade.XML(os.path.join(config.gtk_path,
            "hwtest-gtk.glade"))
        self.widgets.signal_autoconnect(self)

        self._dialog = self._get_widget("dialog_hwtest")
        self._dialog.set_title(self.title)

        self._notebook = self._get_widget("notebook_hwtest")

    def _get_widget(self, widget):
        return self.widgets.get_widget(widget)

    def _get_radiobutton(self, map):
        for radiobutton, value in map.items():
            if self._get_widget(radiobutton).get_active():
                return value
        raise Exception, "failed to map radiobutton"

    def _set_label(self, name, text):
        label = self._get_widget(name)
        label.set_text(text)

    def _get_textview(self, name):
        textview = self._get_widget(name)
        buffer = textview.get_buffer()
        data = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())
        return data

    def _set_textview(self, name, data):
        buffer = gtk.TextBuffer()
        buffer.set_text(data)
        textview = self._get_widget(name)
        textview.set_buffer(buffer)

    def _set_sensitive(self, name, boolean):
        widget = self._get_widget(name)
        widget.set_sensitive(boolean)

    def show_category(self):
        self._get_widget("button_previous").hide()
        self._notebook.set_current_page(0)

        response = self._dialog.run()
        while gtk.events_pending():
            gtk.main_iteration(True)

        return self._get_radiobutton({
            "radiobutton_desktop": "desktop",
            "radiobutton_laptop": "laptop",
            "radiobutton_server": "server"})

    def run_question(self, question):
        # Run test
        if question.command != None:
            output = question.run_command()[0].strip()
            self._set_sensitive("button_test_again", True)
        else:
            output = ''
            self._set_sensitive("button_test_again", False)

        add_variable("output", output)
        self._set_label("label_question", question.description)
        remove_variable("output")

    def show_question(self, question, has_prev=False, has_next=False):
        # Set buttons
        self._set_sensitive("button_test_again", False)
        self._set_sensitive("button_previous", has_prev)
        self._get_widget("button_previous").show()
        self._notebook.set_current_page(1)

        # Set test again button
        button_test_again = self._get_widget("button_test_again")
        if hasattr(self, "handler_id"):
            button_test_again.disconnect(self.handler_id)
        self.handler_id = button_test_again.connect("clicked",
            lambda w, question=question: self.run_question(question))

        # Default answers
        if question.answer:
            answer = question.answer
            self._set_textview("textview_comment", answer.data)
            self._get_widget("radiobutton_%s" % answer.status).set_active(True)
        else:
            self._set_textview("textview_comment", "")
            self._get_widget("radiobutton_yes").set_active(True)

        self._dialog.show()
        self.run_question(question)

        response = self._dialog.run()
        while gtk.events_pending():
            gtk.main_iteration(False)

        # Get answer if next button is pressed
        if response:
            status = self._get_radiobutton({
                "radiobutton_yes": "yes",
                "radiobutton_no": "no",
                "radiobutton_skip": "skip"})
            data = self._get_textview("textview_comment")
            question.set_answer(status, data)

        return response

    def show_gather(self, error=None):
        self._set_sensitive("button_previous", False)
        self._set_sensitive("button_next", False)
        self._get_widget("progressbar_gather").set_fraction(0)
        self._notebook.set_current_page(2)

        response = self._dialog.show()
        while gtk.events_pending():
            gtk.main_iteration(False)

    def pulse_gather(self, error=None):
        self._get_widget("progressbar_gather").pulse()
        while gtk.events_pending():
            gtk.main_iteration(False)

    def show_exchange(self, error=None):
        self._set_sensitive("button_previous", False)
        self._set_sensitive("button_next", True)
        self._notebook.set_current_page(3)

        if error is not None:
            markup= "<span color='#FF0000'><b>%s</b></span>" % error
            self._get_widget("label_exchange_error").set_markup(markup)

        response = self._dialog.run()
        while gtk.events_pending():
            gtk.main_iteration(False)

        authentication = self._get_widget("entry_authentication").get_text()

        return authentication

    def show_error_message(self, title, text):
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
