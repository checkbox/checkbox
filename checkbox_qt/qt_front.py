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
import dbus, dbus.service
# import python dbus GLib mainloop support
import dbus.mainloop.glib
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QObject, QVariant, QRect
from PyQt4.QtGui import QApplication, QProgressDialog, QLabel, QStandardItemModel, QStandardItem, QSizePolicy, QErrorMessage
from PyQt4.QtGui import QMessageBox, QWidget, QHBoxLayout, QGraphicsScene, QGraphicsEllipseItem, QGraphicsView, QGraphicsTextItem
from gui import Ui_main
from gettext import gettext as _

buttonMap = {QMessageBox.Yes: "yes", QMessageBox.No: "no"}
titleTestTypes = { 
    "__audio__": "Audio Test",
    "__bluetooth__": "Bluetooth Test",
    "__camera__": "Camera Test",
    "__cpu__": "CPU Test",
    "__disk__": "Disk Test",
    "__firewire__": "Firewire Test",
    "__graphics__": "Graphics Test",
    "__info__": "Info Test",
    "__input__": "Input Test",
    "__keys__": "Keys Test",
    "__mediacard__": "Mediacard Test",
    "__memory__": "Memory Test",
    "__miscellanea__": "Miscellanea Test",
    "__monitor__": "Monitor Test",
    "__networking__": "Networking Test",
    "__wireless__": "Wireless Test",
    "__optical__": "Optical Test",
    "__pcmcia-pcix__": "PCMCIA/PCIX Test",
    "__power-management__": "Power Management Test",
    "__suspend__": "Suspend Test",
    "__usb__": "USB Test"
}

class Step(QWidget):
    def __init__(self, parent, index, text=""):
        QWidget.__init__(self, parent)
        self.setFixedWidth(470)
        self.layout = QHBoxLayout(self)

        if index:
            self.scene = QGraphicsScene(0, 0, 20, 20);
            self.item = QGraphicsEllipseItem(0, 0, 20, 20);
            self.item.setBrush( QtCore.Qt.yellow )
            self.item.setPos(0,0)
            self.scene.addItem(self.item);
            self.item.setPos(0,0)
            self.view = QGraphicsView(self.scene)
            self.view.setFrameShape(0)
            self.view.setBackgroundRole(17)
            self.view.setFixedSize(20, 20)
            self.text = QGraphicsTextItem(" "+ index, self.item)
            self.text.setTextWidth(20)
            self.layout.addWidget(self.view)
        else:
            widget = QWidget(self)
            widget.setFixedWidth(50)
            self.layout.addWidget(widget)

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.layout.addWidget(self.label)
        self.show()

    def __del__(self):
        self.hide()

class TreeModel(QStandardItemModel):
    message = None
    def warn(self):
        if not self.message:
            self.message = QErrorMessage()
        self.message.showMessage("Changeme: If you deselect this, bad things will happen, check it again!")

    def setData(self, index, value, role = QtCore.Qt.EditRole):
        item = QStandardItemModel.itemFromIndex(self, index)
        self.warn()
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

    def setInteraction(self, value=False):
        for i in range(self.rowCount()):
            item = QStandardItemModel.item(self, i, 0)
            item.setEnabled(value)
            for j in range(item.rowCount()):
                childItem = item.child(j)
                childItem.setEnabled(value)

class QtFront(dbus.service.Object):
    widgetList = None
    model = None
    def __init__(self, name, session):
        dbus.service.Object.__init__(self, dbus.SessionBus(), "/com/canonical/qt_checkbox")
        self.ui = Ui_main()
        self.widget = QtGui.QWidget()
        self.ui.setupUi(self.widget)
        self.widget.show()
        self.ui.tabWidget.tabBar().setVisible(False)
        self.ui.radioTestTab.tabBar().setVisible(False)
        self.ui.radioTestTab.setVisible(False)
        self.ui.nextPrevButtons.setVisible(False)
        self.ui.friendlyTestsButton.clicked.connect(self.onFullTestsClicked)
        #self.ui.chooseTestsButton.clicked.connect(self.onCustomTestsClicked)
        self.ui.buttonStartTesting.clicked.connect(self.onStartTestsClicked)
        self.ui.testTestButton.clicked.connect(self.onStartTestClicked)
        self.ui.yesTestButton.clicked.connect(self.onYesTestClicked)
        self.ui.noTestButton.clicked.connect(self.onNoTestClicked)
        self.ui.nextTestButton.clicked.connect(self.onNextTestClicked)
        self.ui.previousTestButton.clicked.connect(self.onPreviousTestClicked)
        self.ui.stepsFrame.setFixedHeight(0)
        self.skipTestMessage = QErrorMessage()
       

    @dbus.service.method("com.canonical.QtCheckbox", in_signature='', out_signature='')
    def hide(self):
        self.widget.hide()

    @dbus.service.method("com.canonical.QtCheckbox", in_signature='sass', out_signature='s')
    def showInfo(self, text, options=[], default=None):
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

        dialog = QMessageBox(self.ui.tabWidget)
        dialog.setText(text)
        dialog.setWindowTitle(_("Info"))
        dialog.setDefaultButton(defaultButton)
        dialog.setStandardButtons(buttons)
        status = dialog.exec_()
        return buttonMap[status]

    @dbus.service.method("com.canonical.QtCheckbox", in_signature='s', out_signature='')
    def showError(self, text):
        QMessageBox.critical(self.ui.tabWidget, _("Error"), text)

    @dbus.service.method("com.canonical.QtCheckbox", in_signature='sa{sa{ss}}', out_signature='')
    def showTree(self, text, options={}):#, default={}):
        self.ui.testsTab.setCurrentIndex(1)
        self.ui.radioTestTab.setVisible(False)
        self.ui.nextPrevButtons.setVisible(False)
        # build the model only once
        if not self.model:
            self.model = TreeModel()

            for section in options:
                sectionItem = QStandardItem(section) 
                sectionItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled| QtCore.Qt.ItemIsTristate) 
                sectionItem.setData(QVariant(QtCore.Qt.Checked), QtCore.Qt.CheckStateRole) 

                for test in options[section]:
                    testItem = QStandardItem(test)
                    testItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                    testItem.setData(QVariant(QtCore.Qt.Checked), QtCore.Qt.CheckStateRole)
                    sectionItem.appendRow(testItem)

                self.model.appendRow(sectionItem) 

            self.ui.treeView.setModel(self.model)
            self.ui.treeView.show()

        self.ui.buttonStartTesting.setEnabled(True)
        self.ui.treeView.model().setInteraction(True)

    @dbus.service.method("com.canonical.QtCheckbox", in_signature='ssb', out_signature='')
    def showTest(self, text, testType, enableTestButton):
        self.ui.radioTestTab.setVisible(True)
        self.ui.nextPrevButtons.setVisible(True)
        self.ui.testTestButton.setEnabled(enableTestButton)

        for i in self.ui.stepsFrame.children():
            i.deleteLater()
        self.ui.stepsFrame.setFixedHeight(0)
        self.ui.stepsFrame.update()
        self.ui.testsTab.setCurrentIndex(2)
        purpose = text[text.find("PURPOSE") + 8: text.find("STEPS:")].strip()
        steps = text[text.find("STEPS:") + 6: text.find("VERIFICATION:")].strip().split('\n')
        verification = text[text.find("VERIFICATION:") + 13:].strip()
        r = re.compile(r"[0-9]+\. (.*)")
        index = 1
        self.ui.testTypeLabel.setText(titleTestTypes[testType])
        self.ui.purposeLabel.setText(purpose)
        for i in steps:
            isInfo = False
            if not r.match(i.strip()):
                isInfo = True
            step = r.sub(r"\1", i.strip())
            if isInfo:
                a = Step(self.ui.stepsFrame, None, step)
            else:
                a = Step(self.ui.stepsFrame, str(index), step)

            index+=1
            a.move(0, self.ui.stepsFrame.height())
            self.ui.stepsFrame.setFixedHeight(self.ui.stepsFrame.height() + a.height())
        question = Step(self.ui.stepsFrame, str("?"), verification)
        question.move(0, self.ui.stepsFrame.height())
        self.ui.stepsFrame.setFixedHeight(self.ui.stepsFrame.height() + question.height())

    @dbus.service.method("com.canonical.QtCheckbox", in_signature='', out_signature='a{sa{ss}}')
    def getTestsToRun(self):
        selectedOptions = {}

        model = self.ui.treeView.model()
        numRows = model.rowCount()
        for i in range(numRows):
            item = model.item(i, 0)
            itemDict = {}
            for j in range(item.rowCount()):
                if item.child(j).checkState() == QtCore.Qt.Checked or item.child(j).checkState() == QtCore.Qt.PartiallyChecked:
                    itemDict[str(item.child(j).text())] = str("")

            if item.checkState() == QtCore.Qt.Checked or item.checkState() == QtCore.Qt.PartiallyChecked:
                selectedOptions[str(item.text())] = itemDict

        print selectedOptions
        return selectedOptions

    @dbus.service.method("com.canonical.QtCheckbox", in_signature='', out_signature='')
    def show(self):
        self.widget.show()

    @dbus.service.method("com.canonical.QtCheckbox", in_signature='s', out_signature='')
    def setWindowTitle(self, title):
        self.widget.setWindowTitle(title)

    @dbus.service.method("com.canonical.QtCheckbox", in_signature='s', out_signature='')
    def showText(self, text):
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.welcomeTextBox.setPlainText(text)

    @dbus.service.method("com.canonical.QtCheckbox", in_signature='s', out_signature='')
    def startProgressBar(self, text):
        self.ui.progressBar.setRange(0, 0)
        self.ui.progressBar.setVisible(True)
        self.ui.progressLabel.setVisible(True)
        # pulsate if tests are not running yet
        self.ui.progressLabel.setText(text)

    @dbus.service.method("com.canonical.QtCheckbox", in_signature='', out_signature='')
    def stopProgressBar(self):
        self.ui.progressBar.setRange(0, 100)
        self.ui.progressBar.setVisible(False)
        self.ui.progressLabel.setVisible(False)
        # pulsate if tests are not running yet
        self.ui.progressLabel.setText("")

    @dbus.service.signal("com.canonical.QtCheckbox", signature='')
    def onFullTestsClicked(self, a):
        self.ui.tabWidget.setCurrentIndex(1)
        self.ui.testsTab.setTabText(self.ui.testsTab.indexOf(self.ui.testSelection), QtGui.QApplication.translate("main", " Summary ", None, QtGui.QApplication.UnicodeUTF8))
        pass

    @dbus.service.signal("com.canonical.QtCheckbox", signature='')
    def onCustomTestsClicked(self, a):
        self.ui.tabWidget.setCurrentIndex(1)
        pass

    @dbus.service.signal("com.canonical.QtCheckbox", signature='')
    def onStartTestsClicked(self, a):
        self.ui.buttonStartTesting.setEnabled(False)
        self.ui.treeView.model().setInteraction(False)
        #self.ui.tabWidget.setCurrentIndex(1)
        pass

    @dbus.service.signal("com.canonical.QtCheckbox", signature='')
    def onNextTestClicked(self, a):
        self.skipTestMessage.showMessage("Skip this test?")
        pass

    @dbus.service.signal("com.canonical.QtCheckbox", signature='')
    def onPreviousTestClicked(self, a):
        pass

    @dbus.service.signal("com.canonical.QtCheckbox", signature='')
    def onStartTestClicked(self, a):
        pass

    @dbus.service.signal("com.canonical.QtCheckbox", signature='')
    def onYesTestClicked(self, a):
        pass

    @dbus.service.signal("com.canonical.QtCheckbox", signature='')
    def onNoTestClicked(self, a):
        pass

if __name__ == "__main__":
        app = QtGui.QApplication(sys.argv)
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        session_bus = dbus.SessionBus()
        name = dbus.service.BusName("com.canonical.QtCheckbox", session_bus)
        widget = QtFront(session_bus, '/QtFront')
        app.exec_()
        

