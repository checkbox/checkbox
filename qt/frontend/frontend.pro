#-------------------------------------------------
#
# Project created by QtCreator 2012-01-25T10:09:44
#
#-------------------------------------------------

QT       += core dbus service

QMAKE_UIC = /usr/bin/uic-qt4 -tr checkboxTr 

TARGET = checkbox-qt-service
TEMPLATE = app


SOURCES += main.cpp\
        qtfront.cpp \
    treemodel.cpp \
    step.cpp \
    checkboxtr.cpp

HEADERS  += qtfront.h \
    treemodel.h \
    step.h \
    checkboxtr.h

FORMS    += qtfront.ui

RESOURCES += \
    resources.qrc
