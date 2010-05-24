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

import re, string
from gettext import gettext as _

from checkbox.user_interface import (UserInterface, NEXT, PREV,
                                     YES_ANSWER, NO_ANSWER, SKIP_ANSWER,
                                     ALL_ANSWERS, ANSWER_TO_STATUS)


class Dialog(object):
    """
    Basic dialog class that displays some text
    """
    PALETTE = (('header', 'white', 'dark red'),
               ('body', 'black', 'light gray'),
               ('footer', 'white', 'dark red'),
               ('button', 'black', 'dark cyan'),
               ('button focused', 'white', 'dark blue'),
               ('highlight', 'black', 'dark cyan'),
               ('highlight focused', 'white', 'dark blue'),
               )
    header = None
    footer = None

    def __init__(self, text):
        self.text = text

        # Response selected by the user (if any)
        self.response = None
        self.direction = NEXT


    def show(self):
        """
        Show dialog
        """
        walker = urwid.SimpleListWalker([])

        text = urwid.Text(self.text)
        walker.append(text)

        if self.header:
            header = self.header
        else:
            header = urwid.AttrMap(urwid.Text(_('Checkbox System Testing')),
                                   'header')

        if self.footer:
            footer = self.footer
        else:
            footer = urwid.AttrMap(urwid.Text('Arrow keys/Page Up/Page Down: Move'),
                                   'footer')
        body = urwid.ListBox(walker)
        frame = urwid.AttrMap(urwid.Frame(body, header, footer), 'body')

        self.walker = walker
        self.frame = frame


    def run(self):
        """
        Display dialog and run mainloop to get response
        """
        self.show()
        loop = urwid.MainLoop(self.frame, self.PALETTE)
        loop.run()
        return self


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


    def create_buttons(self, buttons_data):
        """
        Create dialog buttons
        """
        # Set a default callback in case button data
        # doesn't contain that information
        def set_default_cb(button_data):
            if not isinstance(button_data, (list, tuple)):
                button_data = (button_data, self.button_clicked_cb)
            return button_data

        buttons_data = [set_default_cb(button_data)
                        for button_data in buttons_data]

        # Buttons width is calculated based on text lenght
        # and the characters used to mark the text
        # as a selectable button
        buttons_width = (max([len(label) for label, _ in buttons_data])
                         + len('<  >'))
        button_widgets = [urwid.AttrMap(urwid.Button(*button_data),
                                        'button', 'button focused')
                          for button_data in buttons_data]
        buttons_box = urwid.GridFlow(button_widgets,
                                     buttons_width, 1, 1, 'left')
        return buttons_box


    def show(self):
        """
        Display dialog text and option buttons
        """
        # Show text
        super(ChoiceDialog, self).show()

        # Show option buttons
        buttons_box = self.create_buttons(self.options)
        self.walker.append(urwid.Divider())
        self.walker.append(buttons_box)


class InputDialog(ChoiceDialog):
    """
    Dialog the gets some input from user
    """
    def next_button_clicked_cb(self, button):
        """
        Set direction, response and exit
        """
        self.direction = NEXT
        self.response = self.input
        raise urwid.ExitMainLoop


    def previous_button_clicked_cb(self, button):
        """
        Set direction, response and exit
        """
        self.direction = PREV
        self.response = self.input
        raise urwid.ExitMainLoop


    def show(self):
        """
        Display text and input field
        """
        # Show text
        Dialog.show(self)

        # Show input
        self.walker.append(urwid.Divider())
        self.input_widget = urwid.Edit(multiline=True)
        self.walker.append(urwid.AttrMap(self.input_widget,
                                         'highlight', 'highlight focused'))

        # Show buttons
        self.walker.append(urwid.Divider())
        buttons = ((_('Previous'), self.previous_button_clicked_cb),
                   (_('Next'), self.next_button_clicked_cb))
        buttons_box = self.create_buttons(buttons)
        self.walker.append(buttons_box)


    @property
    def input(self):
        """
        Return text written by the user as feedback
        """
        return self.input_widget.get_edit_text()


class TestDialog(ChoiceDialog):
    """
    Choice dialog with an extra input field for feedback
    """
    def __init__(self, text, options=None, buttons=None, default=None):
        Dialog.__init__(self, text)
        self.options = options
        self.buttons = buttons
        self.default = default


    def next_button_clicked_cb(self, button):
        """
        Set direction, response and exit
        """
        self.direction = NEXT
        self.response = self.selected
        raise urwid.ExitMainLoop


    def previous_button_clicked_cb(self, button):
        """
        Set direction, response and exit
        """
        self.direction = PREV
        self.response = self.selected
        raise urwid.ExitMainLoop


    def create_radio_buttons(self, labels):
        """
        Create dialog radio buttons
        """
        self.radio_button_group = []

        for label in labels:
            urwid.RadioButton(self.radio_button_group, label)
        return self.radio_button_group


    def show(self):
        """
        Display dialog text, radio buttons,
        input field and option buttons
        """
        # Show text
        Dialog.show(self)

        # Show radio buttons
        self.walker.append(urwid.Divider())
        radio_button_group = self.create_radio_buttons(self.options)
        self.walker.append(urwid.Pile(radio_button_group))

        # Show input
        self.walker.append(urwid.Divider())
        self.walker.append(urwid.Text(_('Further information:')))
        self.input_widget = urwid.Edit(multiline=True)
        self.walker.append(urwid.AttrMap(self.input_widget,
                                         'highlight', 'highlight focused'))

        # Show buttons
        self.walker.append(urwid.Divider())
        default_buttons = [(_('Previous'), self.previous_button_clicked_cb),
                           (_('Next'), self.next_button_clicked_cb)]
        buttons_box = self.create_buttons(self.buttons + default_buttons)
        self.walker.append(buttons_box)


    @property
    def input(self):
        """
        Return text written by the user as feedback
        """
        return self.input_widget.get_edit_text()


    @property
    def selected(self):
        """
        Return the label of the selected radio button
        """
        label = (radio_button.get_label()
                 for radio_button in self.radio_button_group
                 if radio_button.get_state()).next()
        return label


class TreeChoiceDialog(ChoiceDialog):
    """
    Choice dialog that shows a tree of options
    """
    footer = urwid.AttrMap(urwid.Columns((urwid.Text('Arrow keys/Page Up/Page Down: Move'),
                                          urwid.Text('Space: Select/Unselect'),
                                          urwid.Text('+/-/Enter: Expand/Collapse'))),
                           'footer')

    def __init__(self, text, options=None, default=None):
        Dialog.__init__(self, text)
        self.options = options
        self.default = default


    def select_all_clicked_cb(self, button):
        """
        Select all test suites
        """
        self.set_all_options(True)


    def deselect_all_clicked_cb(self, button):
        """
        Deselect all test suites
        """
        self.set_all_options(False)


    def set_all_options(self, new_value):
        """
        Set state for all options in the tree
        """
        for widget in self.option_widgets:
            widget.state = new_value
            widget.set_children_state(new_value)


    def next_button_clicked_cb(self, button):
        """
        Set direction, response and exit
        """
        self.direction = NEXT
        self.button_clicked_cb(button)


    def previous_button_clicked_cb(self, button):
        """
        Set direction, response and exit
        """
        self.direction = PREV
        self.button_clicked_cb(button)


    def button_clicked_cb(self, button):
        """
        Set response and exit
        """
        self.response = {}

        def traverse_widget_state(widget, parent_response):
            if widget.state:
                response = {}
                for child in widget:
                    traverse_widget_state(child, response)
                parent_response[widget.name] = response

        # Add to response all widgets that have been set
        for widget in self.option_widgets:
            traverse_widget_state(widget, self.response)

        raise urwid.ExitMainLoop


    def create_tree(self, name, data, parent=None):
        """
        Create a tree node and all its children
        """
        widget = TreeNodeWidget(name, parent)
        urwid.signals.connect_signal(widget, 'change',
                                     widget.changed_cb, self.walker)

        items = sorted(data.iteritems(), key=lambda item: item[0])
        for children_name, children_data in items:
            child_widget = self.create_tree(children_name, children_data, widget)
            widget.append(child_widget)

        return widget


    def _set_default(self, widgets, default):
        """
        Set selected nodes by default recursively
        """
        for name, default_children in default.iteritems():
            for widget in widgets:
                if widget.name == name:
                    widget.state = True
                    self._set_default(widget.children,
                                      default_children)

    def show(self):
        """
        Display dialog text, options tree and buttons
        """
        # Show text
        Dialog.show(self)

        # Show tree
        self.option_widgets = []
        items = sorted(self.options.iteritems(), key=lambda item: item[0])
        for name, data in items:
            widget = self.create_tree(name, data)
            self.option_widgets.append(widget)
            self.walker.append(widget)

        self._set_default([node for node in self.walker
                           if isinstance(node, TreeNodeWidget)],
                          self.default)

        # Show buttons
        labels = ((_('Select All'), self.select_all_clicked_cb),
                  (_('Deselect All'), self.deselect_all_clicked_cb),
                  (_('Previous'), self.previous_button_clicked_cb),
                  (_('Next'), self.next_button_clicked_cb))
        buttons_box = self.create_buttons(labels)
        self.walker.append(urwid.Divider())
        self.walker.append(buttons_box)


class TreeNodeWidget(urwid.WidgetWrap):
    """
    Implementation of a node in a tree that can be selected/deselected
    """
    signals = ['change']

    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.depth = (parent.depth + 1) if parent else 0
        self.children = []

        self.expanded = False

        # Use a checkbox as internal representation of the widget
        self.checkbox = urwid.CheckBox(self._get_label())
        w = urwid.AttrMap(self.checkbox, 'highlight', 'highlight focused')
        super(TreeNodeWidget, self).__init__(w)


    def __iter__(self):
        """
        Iterate over children nodes
        """
        return iter(self.children)


    def append(self, child):
        """
        Append a child
        """
        self.children.append(child)

        # If there wasn't any children
        # label has to be udpated
        if len(self.children) == 1:
            self._update_label()


    def selectable(self):
        return True


    @property
    def state(self):
        """
        Get state from checkbox widget
        """
        return self.checkbox.get_state()


    @state.setter
    def state(self, value):
        """
        Set state to checkbox widget
        """
        self.checkbox.set_state(value)


    def set_ancestors_state(self, new_state):
        """
        Set the state of all ancestors consistently
        """
        # If child is set, then all ancestors must be set
        if new_state:
            parent = self.parent
            while parent:
                parent.state = new_state
                parent = parent.parent
        # If child is not set, then all ancestors mustn't be set
        # unless another child of the ancestor is set
        else:
            parent = self.parent
            while parent:
                if any((child.state
                        for child in parent)):
                    break
                parent.state = new_state
                parent = parent.parent


    def set_children_state(self, new_state):
        """
        Set the state of all children recursively
        """
        self.state = new_state
        for child in self:
            child.set_children_state(new_state)


    def keypress(self, size, key):
        """
        Use key events to select checkbox and expand tree hierarchy
        """

        if key == ' ':
            new_state = not self.state
            self.state = new_state
            self.set_children_state(new_state)
            self.set_ancestors_state(new_state)
            return None
        elif self.children:
            if key in ('+', 'enter') and self.expanded == False:
                urwid.signals.emit_signal(self, 'change')
                return None
            elif key in ('-', 'enter') and self.expanded == True:
                urwid.signals.emit_signal(self, 'change')
                return None

        return key


    def mouse_event(self, size, event, button, col, row, focus):
        """
        Use mouse events to select checkbox and expand tree hierarchy
        """
        # Left click event
        if button == 1:
            new_state = not self.state
            self.state = new_state
            self.set_children_state(new_state)
            self.set_ancestors_state(new_state)
        # Ignore button release event
        elif button == 0:
            pass
        else:
            urwid.signals.emit_signal(self, 'change')

        return True


    def _get_label(self):
        """
        Generate text label
        """
        prefix = ' '*(self.depth*2)
        if self.children:
            if self.expanded == False:
                mark = '+'
            else:
                mark = '-'

            label = prefix + '{0} {1}'.format(mark, self.name)
        else:
            label = prefix + self.name
        return label


    def _update_label(self):
        """
        Update text label
        """
        self.checkbox.set_label(self._get_label())


    def _get_widget(self):
        """
        Create widget used internally as node representation
        """


    def changed_cb(self, walker):
        """
        Handle node expansion in the tree
        """
        position = walker.index(self)

        if self.expanded:
            del_start_position = walker.index(self) + 1
            del_end_position = (del_start_position +
                                len(self.children))
            del walker[del_start_position:del_end_position]
            self.expanded = False
        else:
            insert_position = position + 1

            # Append widgets to the list
            walker[insert_position:insert_position] = self.children
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

        self.progress_bar = urwid.ProgressBar('button', 'button focused')
        self.walker.append(self.progress_bar)

        self.loop = urwid.MainLoop(self.frame, self.PALETTE)
        self.loop.screen.start()
        self.loop.draw_screen()


    def set(self, progress=None):
        self.progress_count = (self.progress_count + 1) % 11
        self.progress_bar.set_completion(self.progress_count * 10)
        self.loop.draw_screen()


    def close(self):
        self.loop.screen.stop()


class UrwidInterface(UserInterface):
    """
    User-friendly CLI interface
    """
    ANSWER_TO_OPTION = {
        YES_ANSWER: _('yes'),
        NO_ANSWER: _('no'),
        SKIP_ANSWER: _('skip')}

    OPTION_TO_ANSWER = dict((o, a)
                            for a, o in ANSWER_TO_OPTION.items())

    def show_progress_start(self, text):
        """
        Show a progress bar
        """
        self.progress = ProgressDialog(text)
        self.progress.show()


    def show_progress_pulse(self):
        """
        Pulse progress bar
        Bar should have been created before
        with show_progress_start method
        """
        self.progress.set()


    def show_progress_stop(self):
        """
        Close progress bar dialog
        """
        self.progress.close()


    def show_text(self, text, previous=None, next=None):
        """
        Show just some text
        and wait for the user to select 'Continue'
        """
        dialog = ChoiceDialog(text).run()
        self.direction = dialog.direction
        return dialog.response


    def show_entry(self, text, value, previous=None, next=None):
        dialog = InputDialog(text).run()
        self.direction = dialog.direction
        return dialog.response


    def show_check(self, text, options=[], default=None):
        raise NotImplementedError


    def show_radio(self, text, options=[], default=None):
        """
        Show some options and let the user choose between them
        """
        dialog = ChoiceDialog(text, options, default).run()
        self.direction = dialog.direction
        return dialog.response


    def show_tree(self, text, options={}, default={}):
        """
        Show some options in a tree hierarchy
        and let the user choose between them
        """
        dialog = TreeChoiceDialog(text, options, default).run()
        self.direction = dialog.direction
        return dialog.response


    def show_test(self, test, runner):
        """
        Show test description, radio buttons to set result
        and text box for the tester to add feedback if required
        """
        # Run external command if needed
        if re.search(r'\$output', test['description']):
            output = runner(test)[1]
        else:
            output = ''

        # Get options
        options = list([self.ANSWER_TO_OPTION[a]
                        for a in ALL_ANSWERS])

        # Get buttons
        buttons = []
        if 'command' in test:
            buttons.append(_('test'))

        while True:
            # Get description
            description = (string.Template(test['description'])
                           .substitute({'output': output.strip()}))

            dialog = TestDialog(description, options, buttons).run()

            if dialog.response in self.OPTION_TO_ANSWER:
                break

            # If option cannot be mapped to an answer,
            # then 'test' button has been clicked
            output = runner(test)[1]
            buttons[0] = _('test again')

        answer = self.OPTION_TO_ANSWER[dialog.response]
        test['data'] = dialog.input
        test['status'] = ANSWER_TO_STATUS[answer]
        self.direction = dialog.direction
        return self.response


    def show_info(self, text, options=[], default=None):
        """
        Show some options and let the user choose between them
        """
        return self.show_radio(text, options, default)


    def show_error(self, text):
        """
        Show an error message
        """
        return self.show_radio(text)
