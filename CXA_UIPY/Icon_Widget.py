# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Icon_Widget.ui'
#
# Created: Fri Dec 07 22:38:38 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_UI_IconWidget(object):
    def setupUi(self, UI_IconWidget):
        UI_IconWidget.setObjectName("UI_IconWidget")
        UI_IconWidget.resize(628, 599)
        self.Asseat_listWidget = QtGui.QListWidget(UI_IconWidget)
        self.Asseat_listWidget.setGeometry(QtCore.QRect(20, -10, 577, 642))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Asseat_listWidget.sizePolicy().hasHeightForWidth())
        self.Asseat_listWidget.setSizePolicy(sizePolicy)
        self.Asseat_listWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.Asseat_listWidget.setMaximumSize(QtCore.QSize(16777214, 16777215))
        self.Asseat_listWidget.setMovement(QtGui.QListView.Static)
        self.Asseat_listWidget.setResizeMode(QtGui.QListView.Adjust)
        self.Asseat_listWidget.setLayoutMode(QtGui.QListView.SinglePass)
        self.Asseat_listWidget.setViewMode(QtGui.QListView.IconMode)
        self.Asseat_listWidget.setObjectName("Asseat_listWidget")

        self.retranslateUi(UI_IconWidget)
        QtCore.QMetaObject.connectSlotsByName(UI_IconWidget)

    def retranslateUi(self, UI_IconWidget):
        UI_IconWidget.setWindowTitle(QtGui.QApplication.translate("UI_IconWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))

