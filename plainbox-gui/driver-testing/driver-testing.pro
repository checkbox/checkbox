# This file is part of plainbox-gui
#
# Copyright 2013 Canonical Ltd.
#
# Authors:
# - Andrew Haigh <andrew.haigh@cellsoftware.co.uk>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# Add more folders to ship with the application, here
folder_01.source = qml
folder_01.target = .
DEPLOYMENTFOLDERS = folder_01

QT += dbus widgets
TARGET = driver-testing
TEMPLATE = app

isEmpty(PREFIX) {
      PREFIX = /usr/local
}

LIBS += -L../lib/$$TARGET/plugins/ -lgui-engine

# Additional import path used to resolve QML modules in Creator's code model
QML_IMPORT_PATH =

QMAKE_LFLAGS += '-Wl,-rpath,\'$$PREFIX/lib/$$TARGET/plugins\''

SOURCES += main.cpp \
    whitelistitem.cpp \
    testitem.cpp \
    listmodel.cpp \
    commandtool.cpp \
    testitemmodel.cpp

# Please do not modify the following two lines. Required for deployment.
include(qtquick2applicationviewer/qtquick2applicationviewer.pri)
qtcAddDeployment()

desktop.path = $$PREFIX/share/applications
desktop.files += driver-testing.desktop

INSTALLS += desktop

HEADERS += whitelistitem.h \
    testitem.h \
    listmodel.h \
    commandtool.h \
    testitemmodel.h

target.path = $$PREFIX/bin
INSTALLS += target

qml_files.path = $$PREFIX/share/$$TARGET
qml_files.files = qml

INSTALLS += qml_files

OTHER_FILES += \
    qml/DummyListModel.qml \
    qml/TestSelectionButtons.qml \
    qml/TestSelectionView.qml \
    qml/TestSelectionListView.qml \
    qml/TestSelectionSuiteDelegate.qml \
    qml/TestSelectionTestDelegate.qml \
    qml/SuiteSelectionDelegate.qml \
    qml/SuiteSelectionView.qml \
    qml/RunManagerView.qml \
    qml/RunManagerSuiteDelegate.qml \
    qml/SubmissionDialog.qml \
    qml/driver-testing.qml
