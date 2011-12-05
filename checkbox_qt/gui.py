# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/checkbox-qt.ui'
#
# Created: Mon Dec  5 12:58:06 2011
#      by: PyQt4 UI code generator 4.8.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(451, 402)
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.verticalLayout_2 = QtGui.QVBoxLayout(Form)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.top = QtGui.QWidget(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.top.sizePolicy().hasHeightForWidth())
        self.top.setSizePolicy(sizePolicy)
        self.top.setMinimumSize(QtCore.QSize(428, 72))
        self.top.setObjectName(_fromUtf8("top"))
        self.verticalLayout.addWidget(self.top)
        self.center = QtGui.QWidget(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.center.sizePolicy().hasHeightForWidth())
        self.center.setSizePolicy(sizePolicy)
        self.center.setObjectName(_fromUtf8("center"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.center)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.infoWindow = QtWebKit.QWebView(self.center)
        self.infoWindow.setProperty("url", QtCore.QUrl(_fromUtf8("about:blank")))
        self.infoWindow.setObjectName(_fromUtf8("infoWindow"))
        self.verticalLayout_3.addWidget(self.infoWindow)
        self.progressWidget = QtGui.QWidget(self.center)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressWidget.sizePolicy().hasHeightForWidth())
        self.progressWidget.setSizePolicy(sizePolicy)
        self.progressWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.progressWidget.setObjectName(_fromUtf8("progressWidget"))
        self.progress_bar = QtGui.QVBoxLayout(self.progressWidget)
        self.progress_bar.setSpacing(0)
        self.progress_bar.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.progress_bar.setMargin(0)
        self.progress_bar.setMargin(0)
        self.progress_bar.setObjectName(_fromUtf8("progress_bar"))
        self.progressLabel = QtGui.QLabel(self.progressWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressLabel.sizePolicy().hasHeightForWidth())
        self.progressLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setKerning(True)
        self.progressLabel.setFont(font)
        self.progressLabel.setText(QtGui.QApplication.translate("Form", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.progressLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.progressLabel.setIndent(-1)
        self.progressLabel.setObjectName(_fromUtf8("progressLabel"))
        self.progress_bar.addWidget(self.progressLabel)
        self.progressBar = QtGui.QProgressBar(self.progressWidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setFormat(QtGui.QApplication.translate("Form", "%p%", None, QtGui.QApplication.UnicodeUTF8))
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.progress_bar.addWidget(self.progressBar)
        self.verticalLayout_3.addWidget(self.progressWidget)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout.addWidget(self.center)
        self.bottom = QtGui.QWidget(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bottom.sizePolicy().hasHeightForWidth())
        self.bottom.setSizePolicy(sizePolicy)
        self.bottom.setMinimumSize(QtCore.QSize(0, 41))
        self.bottom.setObjectName(_fromUtf8("bottom"))
        self.button_next = QtGui.QPushButton(self.bottom)
        self.button_next.setGeometry(QtCore.QRect(360, 6, 81, 29))
        self.button_next.setText(QtGui.QApplication.translate("Form", "Next", None, QtGui.QApplication.UnicodeUTF8))
        self.button_next.setObjectName(_fromUtf8("button_next"))
        self.button_previous = QtGui.QPushButton(self.bottom)
        self.button_previous.setGeometry(QtCore.QRect(270, 6, 81, 29))
        self.button_previous.setText(QtGui.QApplication.translate("Form", "Previous", None, QtGui.QApplication.UnicodeUTF8))
        self.button_previous.setObjectName(_fromUtf8("button_previous"))
        self.verticalLayout.addWidget(self.bottom)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        pass

from PyQt4 import QtWebKit
