import os
import gtk
import gtk.glade
import gnomecanvas

from hwtest.constants import SHARE_DIR
from hwtest.excluder import Excluder
from hwtest.result import (ALL_STATUS)
from hwtest.test import (ALL_CATEGORIES)
from hwtest.ui import Ui

GUI_DIR = os.path.join(SHARE_DIR, 'gui')

class Gui(Ui):

    def __init__(self, application):
        super(Gui, self).__init__(application)
        self.tests = []
        self.start_color = 3638089728
        self.end_color = 4294967040
        self.wTree = gtk.glade.XML(os.path.join(GUI_DIR, 'hwtest.glade'),
            'window', 'hwtest')

        # Canvas
        canvas = self.wTree.get_widget("canvas")
        self.root = canvas.root().add(gnomecanvas.CanvasGroup)

        # Canvas pic
        canvas_bg = gtk.gdk.pixbuf_new_from_file(os.path.join(GUI_DIR,
            'canvas_bg.png'))
        self.root.add(gnomecanvas.CanvasPixbuf, pixbuf=canvas_bg, x=0,
            y=0, anchor="nw")

        # Window
        window = self.wTree.get_widget("window")
        window.set_resizable(False)
        window.set_size_request(450, 410)
        window.set_icon_from_file(os.path.join(GUI_DIR, 'ubuntu_logo.png'))
        window.connect("destroy", lambda w: gtk.main_quit())

        # Vertical and horizontal boxes
        self.vbox1 = gtk.VBox(False, 0)
        self.hbox1 = gtk.HBox(False, 0)

    def show_intro(self):
        # Fade intro
        text = "<big><b>%s</b></big>\n%s" % (
            self.application.title, self.application.intro)
        self.intro = self.root.add(gnomecanvas.CanvasText,
            markup=text, size=9000, fill_color_rgba=self.start_color,
            x=220, y=80)
        self._fade_in(self.intro)

        # Vertical and horizontal boxes
        self.vbox2 = gtk.VBox(False, 0)
        self.hbox2 = gtk.HBox(False, 0)
        for category in ALL_CATEGORIES:
            button_name = '%s_button' % category
            type_button = self.wTree.get_widget(button_name)
            type_button.connect("clicked", lambda w,
                category=category: self.do_intro(category))
            type_button.show()
            self.vbox2.pack_start(type_button, False, False, 2)

        self.hbox2.pack_start(self.vbox2, False, False, 0)
        self.hbox2.show_all()
        self.category = self.root.add(gnomecanvas.CanvasWidget, x=180, y=160,
            widget=self.hbox2, width=140, height=80)

    def hide_intro(self):
        self.intro.destroy()
        self.category.destroy()

    def do_intro(self, category):
        def exclude_func(test, category=category):
            return category not in test.categories

        # Cleanup intro
        self.hide_intro()
        self.show_test_common()

        # Setup tests
        manager_tests = self.application.test_manager.get_iterator()
        self.tests = Excluder(manager_tests, exclude_func, exclude_func)
        self.test = self.tests.next()
        self.show_test()

    def show_test_common(self):
        # Direction buttons
        self.direction_buttons = {}
        for direction in ['previous', 'next']:
            button = self.wTree.get_widget("%s_button" % direction)
            func = getattr(self, "do_%s" % direction)
            button.connect("clicked", lambda w, func=func: func())
            button.show()
            self.direction_buttons[direction] = button

    def hide_test_common(self):
        for direction_button in self.direction_buttons.values():
            direction_button.destroy()

    def show_test(self):
        result = self.test.result

        # Content
        gtk.rc_parse_string('gtk_font_name = "Sans 8"')
        self.content_txt = self.root.add(gnomecanvas.CanvasRichText, x=30,
            y=10, width=300, height=180, text=self.test.description, cursor_visible=False)
        self.content_line = self.root.add(gnomecanvas.CanvasLine,
            points=[30, 120, 430, 120], width_pixels=1,
            fill_color_rgba=288581136)
        gtk.rc_reset_styles(gtk.settings_get_default())

        # Radio buttons
        previous = None
        self.radio_buttons = {}
        for status in ALL_STATUS:
            button = gtk.RadioButton(previous, status.capitalize())
            previous = button
            self.radio_buttons[status] = button
            if result and result.status is status:
                button.set_active(True)

        radio_vbox = gtk.VBox(False, 0)
        radio_hbox = gtk.HBox(False, 0)
        for status in ALL_STATUS:
            radio_vbox.pack_start(self.radio_buttons[status], False, False, 2)
        radio_hbox.pack_start(radio_vbox, False, False, 0)
        radio_hbox.show_all()
        self.radio_win = self.root.add(gnomecanvas.CanvasWidget,
            x=40, y=160, widget=radio_hbox, width=140, height=100)
 
        # Direction buttons
        self.direction_buttons["previous"].set_sensitive(self.tests.has_prev())

        # Comment
        self.comment_txt = self.root.add(gnomecanvas.CanvasText,
            markup="<span size='10000'><b>%s</b></span>" % "Comments:",
            fill_color_rgba=288581375, x=225, y=135)

        comment_bg = gtk.gdk.pixbuf_new_from_file(os.path.join(GUI_DIR, 'comment_bg.png'))
        self.comment_bg = self.root.add(gnomecanvas.CanvasPixbuf, pixbuf=comment_bg,
            x=175, y=140, anchor="nw")

        comment_win = gtk.ScrolledWindow(None, None)
        comment_win.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.comment_buf = gtk.TextView()
        self.comment_buf.set_editable(True)
        self.comment_buf.set_cursor_visible(True)
        self.comment_buf.set_wrap_mode(gtk.WRAP_WORD)
        if result and result.data:
            buffer = gtk.TextBuffer()
            buffer.set_text(result.data)
            self.comment_buf.set_buffer(buffer)
        comment_win.add(self.comment_buf)
        comment_win.show_all()
        self.comment_win = self.root.add(gnomecanvas.CanvasWidget,
            x=185, y=150, widget=comment_win, width=220, height=120)

    def hide_test(self):
        self.content_txt.destroy()
        self.content_line.destroy()
        for radio_button in self.radio_buttons.values():
            radio_button.destroy()
        self.radio_win.destroy()
        self.comment_txt.destroy()
        self.comment_bg.destroy()
        self.comment_buf.destroy()
        self.comment_win.destroy()

    def do_previous(self):
        if self.tests.has_prev():
            self.test = self.tests.prev()
            self.hide_test()
            self.show_test()

    def do_next(self):
        # Get status
        status = None
        for radio, button in self.radio_buttons.items():
            if button.get_active():
                status = radio

        # Get comment
        buffer = self.comment_buf.get_buffer()
        data = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())

        self.test.create_result(status, data)

        if self.tests.has_next():
            self.test = self.tests.next()
            self.hide_test()
            self.show_test()
        else:
            self.hide_test()
            self.hide_test_common()
            self.show_send_common()
            self.show_send()

    def show_send_common(self):
        txt = """
Please enter the secure ID corresponding
to the machine being tested."""
        self.send_txt = self.root.add(gnomecanvas.CanvasText, markup=txt,
            size=9000, fill_color_rgba=288581136, x=220, y=80)
        self._fade_in(self.send_txt)

        # Login entries
        table = gtk.Table(rows=1, columns=2, homogeneous=False)
        self.vbox1.pack_start(table, True, True, 0)

        secure_id_label = gtk.Label('Secure ID')
        table.attach(secure_id_label, 0, 1, 0, 1, gtk.EXPAND, gtk.EXPAND, 2, 2)
        secure_id_entry = gtk.Entry()
        table.attach(secure_id_entry, 1, 2, 0, 1, gtk.EXPAND, gtk.EXPAND, 2, 2)

        # Send button
        send_button = self.wTree.get_widget('send_button')
        send_button.connect("clicked",
            lambda w: self.do_send(secure_id_entry.get_text()))
        self.vbox1.pack_start(send_button, False, False, 2)

        self.hbox1.pack_start(self.vbox1, False, False, 0)
        self.hbox1.show_all()

        self.login = self.root.add(gnomecanvas.CanvasWidget, x=100, y=120,
            widget=self.hbox1, width=140, height=160)

    def hide_send_common(self):
        self.send_txt.destroy()
        self.login.destroy()

    def show_send(self, error=None):
        if error:
            self.error_txt = self.root.add(gnomecanvas.CanvasText, markup=error,
                size=9000, fill_color_rgba=0xFF000000, x=190, y=20)
            self._fade_in(self.error_txt)
        else:
            self.error_txt = None

    def hide_send(self):
        if self.error_txt:
            self.error_txt.destroy()

    def do_send(self, secure_id):
        self.hide_send()
        if not secure_id:
            error = '''Must provide a secure ID.'''
        else:
            application = self.application
            application.report.info['secure_id'] = secure_id
            application.run()
            error = self.application.plugin_manager.get_error()

        if error:
            self.show_send(error)
        else:
            self.hide_send_common()
            gtk.main_quit()

    def main(self):
        self.show_intro()
        gtk.main()

    def _fade_in(self, text):
            i = self.start_color - 538976288
            while i > 0:
                while gtk.events_pending():
                        gtk.main_iteration(1)
                if i <= 0:
                    i = 0
                text.set(fill_color_rgba = i)
                i = i - 353703189
            return 1

    def _fade_out(self, text):
            i = 1
            while i <= 4294967040:
                while gtk.events_pending():
                        gtk.main_iteration(1)
                text.set(fill_color_rgba = i)
                i = i + 623191333
            text.hide()
            return 1
