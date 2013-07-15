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

# Additional import path used to resolve QML modules in Creator's code model
QML_IMPORT_PATH =

SOURCES += main.cpp \
    testsuiteitem.cpp \
    listmodel.cpp

# Please do not modify the following two lines. Required for deployment.
include(qtquick2applicationviewer/qtquick2applicationviewer.pri)
qtcAddDeployment()

HEADERS += \
    testsuiteitem.h \
    listmodel.h

OTHER_FILES += \
    qml/outline/DummyListModel.qml \
    qml/outline/TestSelectionButtons.qml \
    qml/outline/TestSelectionView.qml \
    qml/outline/OldMainButtons.qml \
    qml/outline/TestSelectionListView.qml

