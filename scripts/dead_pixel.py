#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

class Application:
    def __init__(self):
    self.colors = iter(["red", "green", "blue", "white", "black"])
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.set_decorated(False)
    self.window.fullscreen()
    self.window.modify_bg(gtk.STATE_NORMAL,
                              gtk.gdk.color_parse(self.colors.next()))

    self.window.connect("key-press-event", self.rotate_bg_color)
        self.window.add_events(gtk.gdk.BUTTON_PRESS_MASK)
    self.window.connect("button-press-event", self.rotate_bg_color)

        self.window.show()

    def rotate_bg_color(self, window, event):
        try:
            self.window.modify_bg(gtk.STATE_NORMAL,
                                  gtk.gdk.color_parse(self.colors.next()))
        except StopIteration:
            gtk.main_quit()

    def main(self):
        gtk.main()

if __name__ == "__main__":
    app = Application()
    app.main()
