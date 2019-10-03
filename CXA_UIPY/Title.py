# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Title.ui'
#
# Created: Wed Dec 05 23:20:10 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_title_Form(object):
    def setupUi(self, title_Form):
        title_Form.setObjectName("title_Form")
        title_Form.resize(792, 77)
        title_Form.setMinimumSize(QtCore.QSize(550, 0))
        self.verticalLayout = QtGui.QVBoxLayout(title_Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.title_frame = QtGui.QFrame(title_Form)
        self.title_frame.setMinimumSize(QtCore.QSize(500, 50))
        self.title_frame.setMaximumSize(QtCore.QSize(16777215, 50))
        self.title_frame.setStyleSheet("QFrame{\n"
"    background-color: rgb(71, 145, 235);\n"
"}\n"
"\n"
"QPushButton {\n"
"    color:rgb(180,180,180);\n"
"    border: 0px solid rgba(255, 255, 255, 0);\n"
"    font-size: 14px;\n"
"    font-weight: 500;\n"
"\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    color: rgb(220, 220,220);\n"
"\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    \n"
"    color: rgb(255, 255, 255);\n"
"\n"
"}\n"
"\n"
"QLabel{\n"
"    \n"
"    color: rgb(227, 227, 227);\n"
"    font-size: 15px;\n"
"    font-weight: 1000;\n"
"}\n"
"\n"
"QLineEdit{\n"
"    background-color: rgb(60, 123, 200);\n"
"    border:5px;\n"
"    border-radius:8px\n"
"}\n"
"\n"
"QPushButton[class=\'close\'] {\n"
"    color:rgb(180,180,180);\n"
"    border: 0px solid rgba(255, 255, 255, 0);\n"
"    font-size: 14px;\n"
"    font-weight: 500;\n"
"    image: url(\'../CXA_Icon/button/close.png\')\n"
"}\n"
"\n"
"QPushButton:hover[class=\'close\'] {\n"
"    color: rgb(220, 220,220);\n"
"    image: url(\'../CXA_Icon/button/close_hover.png\');\n"
"}\n"
"\n"
"QPushButton:pressed[class=\'close\'] {\n"
"    \n"
"    color: rgb(255, 255, 255);\n"
"    image: url(\'../CXA_Icon/button/close_pressed.png\');\n"
"}\n"
"\n"
"QPushButton[class=\'max\'] {\n"
"    color:rgb(180,180,180);\n"
"    border: 0px solid rgba(255, 255, 255, 0);\n"
"    font-size: 14px;\n"
"    font-weight: 500;\n"
"    image: url(\'../CXA_Icon/button/max.png\')\n"
"}\n"
"\n"
"QPushButton:hover[class=\'max\'] {\n"
"    color: rgb(220, 220,220);\n"
"    image: url(\'../CXA_Icon/button/max_hover.png\');\n"
"}\n"
"\n"
"QPushButton:pressed[class=\'max\'] {\n"
"    \n"
"    color: rgb(255, 255, 255);\n"
"    image: url(\'../CXA_Icon/button/max_pressed.png\');\n"
"}\n"
"\n"
"QPushButton[class=\'min\'] {\n"
"    color:rgb(180,180,180);\n"
"    border: 0px solid rgba(255, 255, 255, 0);\n"
"    font-size: 14px;\n"
"    font-weight: 500;\n"
"    image: url(\'../CXA_Icon/button/min.png\')\n"
"}\n"
"\n"
"QPushButton:hover[class=\'min\'] {\n"
"    color: rgb(220, 220,220);\n"
"    image: url(\'../CXA_Icon/button/min_hover.png\');\n"
"}\n"
"\n"
"QPushButton:pressed[class=\'min\'] {\n"
"    \n"
"    color: rgb(255, 255, 255);\n"
"    image: url(\'../CXA_Icon/button/min_pressed.png\');\n"
"}\n"
"\n"
"QPushButton[class=\'zhiding\'] {\n"
"    color:rgb(180,180,180);\n"
"    border: 0px solid rgba(255, 255, 255, 0);\n"
"    font-size: 14px;\n"
"    font-weight: 500;\n"
"    image: url(\'../CXA_Icon/button/zhiding.png\')\n"
"}\n"
"\n"
"QPushButton:hover[class=\'zhiding\'] {\n"
"    color: rgb(220, 220,220);\n"
"    image: url(\'../CXA_Icon/button/zhiding.png\');\n"
"}\n"
"\n"
"QPushButton:pressed[class=\'zhiding\'] {\n"
"    \n"
"    color: rgb(255, 255, 255);\n"
"    image: url(\'../CXA_Icon/button/zhiding_pressed.png\');\n"
"}\n"
"")
        self.title_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.title_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.title_frame.setObjectName("title_frame")
        self.gridLayout = QtGui.QGridLayout(self.title_frame)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.title_label = QtGui.QLabel(self.title_frame)
        self.title_label.setObjectName("title_label")
        self.gridLayout.addWidget(self.title_label, 1, 1, 1, 1)
        self.icon_label = QtGui.QLabel(self.title_frame)
        self.icon_label.setMinimumSize(QtCore.QSize(35, 35))
        self.icon_label.setMaximumSize(QtCore.QSize(35, 35))
        self.icon_label.setText("")
        self.icon_label.setScaledContents(True)
        self.icon_label.setObjectName("icon_label")
        self.gridLayout.addWidget(self.icon_label, 0, 0, 3, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 2, 1, 1)
        self.lineEdit = QtGui.QLineEdit(self.title_frame)
        self.lineEdit.setEnabled(True)
        self.lineEdit.setMinimumSize(QtCore.QSize(160, 0))
        self.lineEdit.setMaximumSize(QtCore.QSize(160, 16777215))
        self.lineEdit.setStyleSheet("")
        self.lineEdit.setText("")
        self.lineEdit.setEchoMode(QtGui.QLineEdit.Normal)
        self.lineEdit.setDragEnabled(False)
        self.lineEdit.setReadOnly(False)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 1, 3, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(30, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 4, 1, 1)
        self.features_layout = QtGui.QHBoxLayout()
        self.features_layout.setSpacing(0)
        self.features_layout.setObjectName("features_layout")
        self.color_pd_btn = QtGui.QPushButton(self.title_frame)
        self.color_pd_btn.setEnabled(True)
        self.color_pd_btn.setMinimumSize(QtCore.QSize(30, 30))
        self.color_pd_btn.setMaximumSize(QtCore.QSize(30, 30))
        self.color_pd_btn.setObjectName("color_pd_btn")
        self.features_layout.addWidget(self.color_pd_btn)
        self.top_set_btn = QtGui.QPushButton(self.title_frame)
        self.top_set_btn.setMinimumSize(QtCore.QSize(30, 30))
        self.top_set_btn.setMaximumSize(QtCore.QSize(30, 30))
        self.top_set_btn.setText("")
        self.top_set_btn.setObjectName("top_set_btn")
        self.features_layout.addWidget(self.top_set_btn)
        self.gridLayout.addLayout(self.features_layout, 1, 6, 1, 1)
        self.close_win_layout = QtGui.QHBoxLayout()
        self.close_win_layout.setSpacing(0)
        self.close_win_layout.setObjectName("close_win_layout")
        self._min_btn = QtGui.QPushButton(self.title_frame)
        self._min_btn.setMinimumSize(QtCore.QSize(30, 30))
        self._min_btn.setMaximumSize(QtCore.QSize(30, 30))
        self._min_btn.setText("")
        self._min_btn.setObjectName("_min_btn")
        self.close_win_layout.addWidget(self._min_btn)
        self._max_btn = QtGui.QPushButton(self.title_frame)
        self._max_btn.setMinimumSize(QtCore.QSize(30, 30))
        self._max_btn.setMaximumSize(QtCore.QSize(30, 30))
        self._max_btn.setText("")
        self._max_btn.setObjectName("_max_btn")
        self.close_win_layout.addWidget(self._max_btn)
        self._close_btn = QtGui.QPushButton(self.title_frame)
        self._close_btn.setMinimumSize(QtCore.QSize(30, 30))
        self._close_btn.setMaximumSize(QtCore.QSize(30, 30))
        self._close_btn.setText("")
        self._close_btn.setObjectName("_close_btn")
        self.close_win_layout.addWidget(self._close_btn)
        self.gridLayout.addLayout(self.close_win_layout, 1, 8, 1, 1)
        self.line_2 = QtGui.QFrame(self.title_frame)
        self.line_2.setMinimumSize(QtCore.QSize(2, 20))
        self.line_2.setMaximumSize(QtCore.QSize(2, 20))
        self.line_2.setStyleSheet("background-color: rgb(60, 123, 200);")
        self.line_2.setFrameShadow(QtGui.QFrame.Raised)
        self.line_2.setLineWidth(0)
        self.line_2.setMidLineWidth(0)
        self.line_2.setFrameShape(QtGui.QFrame.VLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 1, 7, 1, 1)
        self.verticalLayout.addWidget(self.title_frame)

        self.retranslateUi(title_Form)
        QtCore.QMetaObject.connectSlotsByName(title_Form)
        title_Form.setTabOrder(self._max_btn, self.color_pd_btn)
        title_Form.setTabOrder(self.color_pd_btn, self._min_btn)
        title_Form.setTabOrder(self._min_btn, self._close_btn)
        title_Form.setTabOrder(self._close_btn, self.lineEdit)

    def retranslateUi(self, title_Form):
        title_Form.setWindowTitle(QtGui.QApplication.translate("title_Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.title_label.setText(QtGui.QApplication.translate("title_Form", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEdit.setPlaceholderText(QtGui.QApplication.translate("title_Form", " Please search here ...", None, QtGui.QApplication.UnicodeUTF8))
        self.color_pd_btn.setText(QtGui.QApplication.translate("title_Form", "╬", None, QtGui.QApplication.UnicodeUTF8))
        self.top_set_btn.setToolTip(QtGui.QApplication.translate("title_Form", "TopWindow", None, QtGui.QApplication.UnicodeUTF8))
        self._min_btn.setToolTip(QtGui.QApplication.translate("title_Form", "MinWindow", None, QtGui.QApplication.UnicodeUTF8))
        self._max_btn.setToolTip(QtGui.QApplication.translate("title_Form", "MaxWindow", None, QtGui.QApplication.UnicodeUTF8))
        self._close_btn.setToolTip(QtGui.QApplication.translate("title_Form", "CloseWindow", None, QtGui.QApplication.UnicodeUTF8))

