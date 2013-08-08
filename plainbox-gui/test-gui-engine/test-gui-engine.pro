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
# test-gui-engine.pro
#
# Hand-made pro file to create the test executable for gui-engine plugin

QT  += testlib dbus qml xml

LIBS += -L../plugins/ -lgui-engine

QMAKE_LFLAGS += '-Wl,-rpath,\'\$$ORIGIN/../plugins\''

HEADERS += test-gui-engine.h

SOURCES += test-gui-engine.cpp


