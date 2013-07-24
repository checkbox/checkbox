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
folder_01.source = qml/outline
folder_01.target = qml
DEPLOYMENTFOLDERS = folder_01

QT += dbus

LIBS += -L../plugins/ -lgui-engine

# Additional import path used to resolve QML modules in Creator's code model
QML_IMPORT_PATH =

SOURCES += main.cpp \
    whitelistitem.cpp \
    testitem.cpp \
    listmodel.cpp \
    savefiledlg.cpp \
    commandtool.cpp

# Please do not modify the following two lines. Required for deployment.
include(qtquick2applicationviewer/qtquick2applicationviewer.pri)
qtcAddDeployment()

HEADERS += whitelistitem.h \
    testitem.h \
    listmodel.h \
    savefiledlg.h \
    commandtool.h

OTHER_FILES += \
    qml/outline/DummyListModel.qml \
    qml/outline/TestSelectionButtons.qml \
    qml/outline/TestSelectionView.qml \
    qml/outline/TestSelectionListView.qml \
    qml/outline/TestSelectionSuiteDelegate.qml \
    qml/outline/TestSelectionTestDelegate.qml \
    qml/outline/SuiteSelectionDelegate.qml \
    qml/outline/SuiteSelectionView.qml \
    qml/outline/RunManagerView.qml \
    qml/outline/RunManagerSuiteDelegate.qml \
    qml/outline/SubmissionDialog.qml

