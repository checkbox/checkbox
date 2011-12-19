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
import re, sys, time
import posixpath
import inspect

from gettext import gettext as _

from checkbox.job import UNINITIATED
from checkbox.user_interface import (UserInterface,
    NEXT, YES_ANSWER, NO_ANSWER, SKIP_ANSWER,
    ANSWER_TO_STATUS, STATUS_TO_ANSWER)
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QObject, QVariant
from PyQt4.QtGui import QApplication, QProgressDialog, QLabel, QStandardItemModel, QStandardItem
from PyQt4.QtGui import QMessageBox
from gui import Ui_Form

# Import to register HyperTextView type with gtk
#from checkbox_gtk.hyper_text_view import HyperTextView

ANSWER_TO_BUTTON = {
    YES_ANSWER: "radio_button_yes",
    NO_ANSWER: "radio_button_no",
    SKIP_ANSWER: "radio_button_skip"}

BUTTON_TO_STATUS = dict((b, ANSWER_TO_STATUS[a])
    for a, b in ANSWER_TO_BUTTON.items())

STATUS_TO_BUTTON = dict((s, ANSWER_TO_BUTTON[a])
    for s, a in STATUS_TO_ANSWER.items())

buttonMap = {QMessageBox.Yes: "yes", QMessageBox.No: "no"}

def funcname():
    return inspect.stack()[1][3]

class MyForm(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.top.setStyleSheet("background-image: url(qt/checkbox-qt-head.png)");

class TreeModel(QStandardItemModel):
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        item = QStandardItemModel.itemFromIndex(self, index)
        if item.parent() != None:
            QStandardItemModel.setData(self, item.index(), value, role)
            # we are a child, and we have to update parent's status
            selected = 0
            for i in range(item.parent().rowCount()):
                childItem = item.parent().child(i)
                if childItem.checkState() == QtCore.Qt.Checked:
                    selected += 1
            if selected == item.parent().rowCount():
                item.parent().setCheckState(QtCore.Qt.Checked)
            elif selected == 0:
                item.parent().setCheckState(QtCore.Qt.Unchecked)
            else:
                item.parent().setCheckState(QtCore.Qt.PartiallyChecked)
        else:
            # if we dont have a parent, then we are root. Deselect/select children
            for i in range(item.rowCount()):
                childItem = item.child(i)
                QStandardItemModel.setData(self, childItem.index(), value, role)

        return QStandardItemModel.setData(self, index, value, role)

class QTInterface(UserInterface):
    app = None
    formWindow = None
    progressDialog = None
    def __init__(self, title, data_path):
        super(QTInterface, self).__init__(title, data_path)
        print "My name is: %s" % funcname()
        self.app = QApplication(sys.argv)
        self.progressDialog = QProgressDialog()
        self.formWindow = MyForm()
        self.formWindow.show()
        self._app_title = title
        self.formWindow.ui.progressWidget.setVisible(False)
        self.formWindow.ui._notebook.tabBar().setVisible(False)
        self._set_show("button_select_all", False)
        self._set_show("button_deselect_all", False)

        self.app.processEvents()

    def _get_widget(self, name):
        print "My name is: %s" % funcname()
        return self.formWindow.findChild(QObject, name)

    def _get_radio_button(self, map):
        print "My name is: %s" % funcname()
        return False

    def _get_label(self, name):
        print "My name is: %s" % funcname()
        widget = self._get_widget(name)
        return widget.text()

    def _get_text(self, name):
        print "My name is: %s" % funcname()
        return False

    def _get_text_view(self, name):
        print "My name is: %s" % funcname()
        return False

    def _set_label(self, name, label=""):
        print "My name is: %s" % funcname()
        widget = self._get_widget(name)
        widget.setText(label)
        return False

    def _set_text(self, name, text=""):
        print "My name is: %s" % funcname()
        return False

    def _set_text_view(self, name, text=""):
        print "My name is: %s" % funcname()
        return False

    def _set_hyper_text_view(self, name, text=""):
        print "My name is: %s" % funcname()
        return False

    def _set_active(self, name, value=True):
        print "My name is: %s" % funcname()
        return False

    def _set_show(self, name, value=True):
        print "My name is: %s" % funcname()
        widget = self._get_widget(name)
        widget.setVisible(bool(value))

    def _set_sensitive(self, name, value=True):
        print "My name is: %s" % funcname()
        widget = self._get_widget(name)
        widget.setEnabled(bool(value))

    def _set_button(self, name, value=None):
        print "My name is: %s" % funcname()
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
        print "My name is: %s" % funcname()
        title = self._app_title
        if test_name:
            title += " - %s" % test_name
        self.formWindow.setWindowTitle(title)

    def _run_dialog(self, dialog=None):
        print "My name is: %s" % funcname()
        def on_dialog_response_next():
            self.direction = 1
            self.app.quit()

        def on_dialog_response_previous():
            self.direction = -1
            self.app.quit()

        self.formWindow.ui.button_next.clicked.connect(on_dialog_response_next)
        self.formWindow.ui.button_previous.clicked.connect(on_dialog_response_previous)
        self.app.exec_()

    def show_progress_start(self, message):
        print "My name is: %s" % funcname()
        self._set_sensitive("button_previous", False)
        self._set_sensitive("button_next", False)
        self.formWindow.ui.progressWidget.setVisible(True)
        self.formWindow.ui.progressLabel.setText(message)
        self.formWindow.ui.progressBar.setRange (0, 0); 
        self.app.processEvents()

    def show_progress_stop(self):
        print "My name is: %s" % funcname()
        self.formWindow.ui.progressWidget.setVisible(False)

        self._set_sensitive("button_previous", True)
        self._set_sensitive("button_next", True)

        self.app.processEvents()

    def show_progress_pulse(self):
        print "My name is: %s" % funcname()
        self.app.processEvents()

    def show_text(self, text, previous=None, next=None):
        print "My name is: %s" % funcname() + text

        #Reset window title
        self._set_main_title()
        # Set buttons
        previous_state = self._set_button("button_previous", previous)
        next_state = self._set_button("button_next", next)

        self.formWindow.ui._notebook.setCurrentIndex(0)
        self.formWindow.ui.infoWindow.setPlainText(text)

        self._run_dialog()

        # Unset buttons
        self._set_button("button_previous", previous_state)
        self._set_button("button_next", next_state)

    def show_entry(self, text, value, previous=None, next=None):
        print "My name is: %s" % funcname()
        return False

    def show_check(self, text, options=[], default=[]):
        print "My name is: %s" % funcname()
        return False

    def show_radio(self, text, options=[], default=None):
        print "My name is: %s" % funcname()
        return False

    def show_tree(self, text, options={}, default={}):
        print "My name is: %s" % funcname()
        def set_all_buttons_checked(check=True):
            model = self.formWindow.ui.treeView.model()
            numRows = model.rowCount()
            for i in range(numRows):
                item = model.item(i, 0)
                if check:
                    item.setCheckState(QtCore.Qt.Checked)
                else:
                    item.setCheckState(QtCore.Qt.Unchecked)
                for j in range(item.rowCount()):
                    childItem = item.child(j)
                    if check:
                        childItem.setCheckState(QtCore.Qt.Checked)
                    else:
                        childItem.setCheckState(QtCore.Qt.Unchecked)

        def on_deselect_all():
            set_all_buttons_checked(False)

        def on_select_all():
            set_all_buttons_checked(True)

        self._set_main_title()

        # Set buttons
        self.formWindow.ui._notebook.setCurrentIndex(1)

        self.formWindow.ui.treeInfo.setPlainText(text)

        model = TreeModel() 
        for section in options:
            sectionItem = QStandardItem(section) 
            sectionItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled| QtCore.Qt.ItemIsTristate) 
            sectionItem.setData(QVariant(QtCore.Qt.Checked), QtCore.Qt.CheckStateRole) 

            for test in options[section]:
                testItem = QStandardItem(test)
                testItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                testItem.setData(QVariant(QtCore.Qt.Checked), QtCore.Qt.CheckStateRole)
                sectionItem.appendRow(testItem)

            model.appendRow(sectionItem) 

        self.formWindow.ui.treeView.setModel(model)
        self.formWindow.ui.treeView.show()

        self._set_show("button_select_all", True)
        self._set_show("button_deselect_all", True)
        self.formWindow.ui.button_select_all.clicked.connect(on_select_all)
        self.formWindow.ui.button_deselect_all.clicked.connect(on_deselect_all)

        self.app.processEvents()
        self._run_dialog()

        self.formWindow.ui.button_select_all.clicked.disconnect(on_select_all)
        self.formWindow.ui.button_deselect_all.clicked.disconnect(on_deselect_all)

        selectedOptions = {}

        model = self.formWindow.ui.treeView.model()
        numRows = model.rowCount()
        for i in range(numRows):
            item = model.item(i, 0)
            itemDict = {}
            for j in range(item.rowCount()):
                if item.child(j).checkState() == QtCore.Qt.Checked or item.child(j).checkState() == QtCore.Qt.PartiallyChecked:
                    itemDict[str(item.child(j).text())] = {}

            if item.checkState() == QtCore.Qt.Checked or item.checkState() == QtCore.Qt.PartiallyChecked:
                selectedOptions[str(item.text())] = itemDict

        return selectedOptions

    def _run_test(self, test, runner):
        print "My name is: %s" % funcname()
        return False

    def show_test(self, test, runner):
        print "My name is: %s" % funcname()
        return False

    def show_info(self, text, options=[], default=None):
        print "My name is: %s" % funcname()
        buttons = QMessageBox.NoButton
        defaultButton = QMessageBox.NoButton
        for option in options:
            if option == "yes":
                if default == option:
                    defaultButton = QMessageBox.Yes
                buttons |= QMessageBox.Yes
            elif option == "no":
                if default == option:
                    defaultButton = QMessageBox.No
                buttons |= QMessageBox.No
                
        dialog = QMessageBox()
        dialog.setText(text)
        dialog.setWindowTitle(_("Info"))
        dialog.setDefaultButton(defaultButton)
        dialog.setStandardButtons(buttons)
        status = dialog.exec_()
        return buttonMap[status]

    def show_error(self, text):
        print "My name is: %s" % funcname()
        QMessageBox.critical(self.formWindow, _("Error"), text)

    def draw_image_head(self, widget, data):
        print "My name is: %s" % funcname()
        return False
