#
# This file is part of Checkbox.
#
# Copyright 2010 Canonical Ltd.
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
import urwid

from gettext import gettext as _

from checkbox.user_interface import (UserInterface, ANSWER_TO_STATUS,
    ALL_ANSWERS, YES_ANSWER, NO_ANSWER, SKIP_ANSWER)


class Dialog(object):
    PALETTE = (('header', 'white', 'dark red'),
               ('button', 'black', 'dark cyan'),
               ('button focused', 'white', 'dark blue'),
               ('body', 'black', 'light gray'),
               )

    def __init__(self, text):
        self.text = text

        # Response selected by the user (if any)
        self.response = None


    def show(self):
        """
        Show dialog
        """
        walker = urwid.SimpleListWalker([])

        text = urwid.Text(self.text)
        walker.append(text)

        header = urwid.AttrMap(urwid.Text(_('Checkbox System Testing')),
                               'header')
        body = urwid.ListBox(walker)
        frame = urwid.AttrMap(urwid.Frame(body, header), 'body')

        self.walker = walker
        self.frame = frame


class ChoiceDialog(Dialog):
    """
    Dialog that shows some general text and few options
    and let's the user choose between them
    """
    def __init__(self, text, options=None, default=None):
        super(ChoiceDialog, self).__init__(text)
        self.options = options or [_('Continue')]
        self.default = default


    def button_clicked_cb(self, button):
        """
        Store selected options and exit from dialog
        """
        self.response = button.label
        raise urwid.ExitMainLoop


    def run(self):
        """
        Display dialog and run mainloop to get response
        """
        # Show text
        super(ChoiceDialog, self).show()

        # When options is a list, it's assumed that it's a short list of options
        # and that it can be displayed as a set of buttons to the user
        if isinstance(self.options, list):
            # Buttons width is calculated based on text lenght
            # and the characters used to mark the text
            # as a selectable button
            buttons_width = (max([len(option) for option in self.options])
                             + len('<  >'))
            buttons_box = urwid.GridFlow([urwid.AttrMap(urwid.Button(option,
                                                                     self.button_clicked_cb),
                                                         'button', 'button focused')
                                          for option in self.options],
                                         buttons_width, 1, 1, 'left')
            self.walker.append(buttons_box)
        # When options is a dictionary, it's assumed that it's a long list of options
        # and that it must be displayed as a tree of checkbox elements
        elif isinstance(self.options, dict):
            for name, subjobs in self.options.iteritems():
                widget = TreeNodeWidget(name, subjobs)
                urwid.signals.connect_signal(widget, 'change',
                                             widget.changed_cb, self.walker)
                self.walker.append(widget)

        loop = urwid.MainLoop(self.frame, self.PALETTE)
        loop.run()
        return self.response


class TreeNodeWidget(urwid.WidgetWrap):
    signals = ['change']

    def __init__(self, name, children, parent=None):
        self.name = name
        self.children = children
        self.depth = (parent.depth + 1) if parent else 0

        self.expandable = bool(children)
        self.expanded = False

        w = self._get_widget()
        super(TreeNodeWidget, self).__init__(w)


    def selectable(self):
        return True


    def keypress(self, size, key):
        """
        Use key events to select checkbox and expand tree hierarchy
        """
        if key == ' ':
            self.checkbox.set_state(not self.checkbox.get_state())
            return None
        elif self.expandable:
            if key in ('+', 'enter') and self.expanded == False:
                urwid.signals.emit_signal(self, 'change')
                return None
            elif key in ('+', 'enter') and self.expanded == True:
                urwid.signals.emit_signal(self, 'change')
                return None

        return key


    def mouse_event(self, size, event, button, col, row, focus):
        """
        Use mouse events to select checkbox and expand tree hierarchy
        """
        # Left click event
        if button == 1:
            self.checkbox.set_state(not self.checkbox.get_state())
        # Ignore button release event
        elif button == 0:
            pass
        else:
            urwid.signals.emit_signal(self, 'change')

        return True


    def _get_label(self):
        """
        Update text label
        """
        prefix = ' '*(self.depth*2)
        if self.expandable:
            if self.expanded == False:
                mark = '+'
            else:
                mark = '-'

            label = prefix + '{0} {1}'.format(mark, self.name)
        else:
            label = prefix + self.name
        return label


    def _update_label(self):
        self.checkbox.set_label(self._get_label())


    def _get_widget(self):
        self.checkbox = urwid.CheckBox(self._get_label())
        return urwid.AttrMap(self.checkbox, 'button', 'button focused')


    def changed_cb(self, walker):
        """
        Handle job expansion in the tree
        """
        position = walker.index(self)

        if self.expanded:
            del_start_position = walker.index(self) + 1
            del_end_position = (del_start_position +
                                len(self.children.items()))
            del walker[del_start_position:del_end_position]
            self.expanded = False
        else:
            widgets = []
            for name, children in self.children.iteritems():
                widget = TreeNodeWidget(name, children, self)
                urwid.signals.connect_signal(widget, 'change',
                                             widget.changed_cb, walker)
                widgets.append(widget)
            insert_position = position + 1

            # Append widgets to the list
            walker[insert_position:insert_position] = widgets
            self.expanded = True

        self._update_label()


class ProgressDialog(Dialog):
    """
    Show progress through a bar
    and pulse it when needed
    """
    def __init__(self, text):
        super(ProgressDialog, self).__init__(text)
        self.progress_count = 0


    def show(self):
        super(ProgressDialog, self).show()

        self.progress_bar = urwid.ProgressBar('pg normal', 'pg_complete')
        self.walker.append(self.progress_bar)

        self.loop = urwid.MainLoop(self.frame, self.PALETTE)
        self.loop.screen.start()
        self.loop.draw_screen()


    def set(self, progress=None):
        self.progress_count = (self.progress_count + 1) % 5
        self.progress_bar.set_completion(self.progress_count * 25)
        self.loop.draw_screen()


class UrwidInterface(UserInterface):
    """
    User-friendly CLI interface
    """
    def show_progress_start(self, text):
        """
        Show a progress bar
        """
        return
        self.progress = ProgressDialog(text)
        self.progress.show()


    def show_progress_pulse(self):
        """
        Pulse progress bar
        Bar should have been created before
        with show_progress_start method
        """
        return
        self.progress.set()


    def show_text(self, text, previous=None, next=None):
        """
        Show just some text
        and wait for the user to select 'Continue'
        """
        dialog = ChoiceDialog(text)
        return dialog.run()


    def show_radio(self, text, options=[], default=None):
        """
        Show some options and let the user choose between them
        """
        dialog = ChoiceDialog(text, options, default)
        return dialog.run()


    def show_tree(self, text, options={}, default={}):
        """
        Show some options in a tree hierarchy
        and let the user choose between them
        """
        dialog = ChoiceDialog(text, options, default)
        return dialog.run()


    def show_info(self, text, options=[], default=None):
        """
        Show some options and let the user choose between them
        """
        return self.show_radio(text, options, default)
