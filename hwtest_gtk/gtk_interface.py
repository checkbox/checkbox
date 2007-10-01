import os.path, sys
import gtk, gtk.glade
from gettext import gettext as _

from hwtest.constants import HWTEST_DIR
from hwtest.user_interface import UserInterface


class GTKInterface(UserInterface):
 
    def __init__(self):
        super(GTKInterface, self).__init__()

        # load UI
        gtk.window_set_default_icon_name("hwtest")
        gtk.glade.textdomain(self.gettext_domain)
        self.widgets = gtk.glade.XML(os.path.join(HWTEST_DIR, 'gtk',
            'hwtest-gtk.glade'))
        self.widgets.signal_autoconnect(self)

        self._dialog = self._get_widget('dialog_hwtest')
        self._notebook = self._get_widget('notebook_hwtest')

    def _get_widget(self, widget):
        return self.widgets.get_widget(widget)

    def _get_radiobutton(self, map):
        for radiobutton, value in map.items():
            if self._get_widget(radiobutton).get_active():
                return value
        raise Exception, "failed to map radiobutton"

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

    def show_categories(self):
        self._get_widget('button_previous').hide()
        self._notebook.set_current_page(0)

        response = self._dialog.run()
        while gtk.events_pending():
            gtk.main_iteration(True)

        return self._get_radiobutton({
            'radiobutton_desktop': 'desktop',
            'radiobutton_laptop': 'laptop',
            'radiobutton_server': 'server'})

    def show_question(self, question, has_prev=False, has_next=False):
        self._set_textview('textview_question', question.description)
        self._get_widget('button_previous').set_sensitive(has_prev)
        self._get_widget('button_previous').show()
        self._notebook.set_current_page(1)

        # Default answers
        if question.answer:
            answer = question.answer
            self._set_textview('textview_answer', answer.data)
            self._get_widget('radiobutton_%s' % answer.status).set_active(True)
        else:
            self._set_textview('textview_answer', '')
            self._get_widget('radiobutton_yes').set_active(True)

        response = self._dialog.run()
        while gtk.events_pending():
            gtk.main_iteration(False)

        # Get answer if next button is pressed
        if response:
            status = self._get_radiobutton({
                'radiobutton_yes': 'yes',
                'radiobutton_no': 'no',
                'radiobutton_skip': 'skip'})
            data = self._get_textview('textview_answer')
            question.create_answer(status, data)

        return response

    def show_authentication(self, error=None):
        self._get_widget('button_previous').hide()
        self._notebook.set_current_page(2)

        if error is not None:
            markup= '<span color="#FF0000"><b>%s</b></span>' % error
            self._get_widget('label_authentication_error').set_markup(markup)

        response = self._dialog.run()
        while gtk.events_pending():
            gtk.main_iteration(False)

        email = self._get_widget('entry_email').get_text()
        
        return email

    def on_dialog_hwtest_delete(self, widget, event=None):
        sys.exit(0)
        return True
