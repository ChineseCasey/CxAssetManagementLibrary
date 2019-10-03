# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Main_Win.ui'
#
# Created: Sat Dec 08 19:59:12 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Main_Function_area_Form(object):
    def setupUi(self, Main_Function_area_Form):
        Main_Function_area_Form.setObjectName("Main_Function_area_Form")
        Main_Function_area_Form.resize(1200, 697)
        self.verticalLayout_3 = QtGui.QVBoxLayout(Main_Function_area_Form)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.Main_frame = QtGui.QFrame(Main_Function_area_Form)
        self.Main_frame.setMinimumSize(QtCore.QSize(0, 0))
        self.Main_frame.setStyleSheet("QFrame{\n"
"    \n"
"    background-color: rgb(255, 255, 255);\n"
"}\n"
"QLineEdit{\n"
"    background-color: rgb(150, 150, 157);\n"
"    border:5px;\n"
"    border-radius:8px\n"
"}\n"
"QLabel{\n"
"    background-color: rgb(150, 150, 157);\n"
"    color: rgb(255, 225, 147);\n"
"    font-size: 15px;\n"
"    font-weight: 1000;\n"
"}\n"
"\n"
"QTreeWidget,TreeView {\n"
"    outline: none;\n"
"    border: 1px solid #d9d9d9;\n"
"    border-radius: 1px;\n"
"}\n"
"\n"
"QTreeWidget::item {\n"
"    margin-top: 2px;\n"
"    margin-bottom: 2px;\n"
"    margin-right: 2px;\n"
"    border: 1px solid #d9d9d9;\n"
"    height: 30px;\n"
"    border-radius: 1px;\n"
"    padding-left: 2px;\n"
"    font-size: 12px;\n"
"    border-left: 0 solid transparent;\n"
"    selection-color:#fff;\n"
"}\n"
"\n"
"QTreeWidget::item:selected {\n"
"    \n"
"    background-color: rgb(150, 150, 157);\n"
"    border: 1px solid #3bafda;\n"
"    border-radius: 1px;\n"
"}\n"
"\n"
"QTreeWidget::branch {\n"
"    background: palette(base);\n"
"}\n"
"\n"
"QTreeWidget::branch:has-siblings:!adjoins-item {\n"
"    background: transparent;\n"
"}\n"
"\n"
"QTreeWidget::branch:has-siblings:adjoins-item {\n"
"    margin-top: 2px;\n"
"    margin-left: 2px;\n"
"    border: 1px solid #d9d9d9;\n"
"    border-right: 0 solid transparent;\n"
"    margin-bottom: 2px;\n"
"    image: url(\'../CXA_Icon/tree_widget/minus.png\');\n"
"}\n"
"\n"
"QTreeWidget::branch:!has-children:!has-siblings:adjoins-item {\n"
"    margin-top: 2px;\n"
"    margin-left: 2px;\n"
"    border: 1px solid #d9d9d9;\n"
"    border-right: 0 solid transparent;\n"
"    margin-bottom: 2px;\n"
"    image: url(\'../CXA_Icon/tree_widget/minus.png\');\n"
"}\n"
"\n"
"QTreeWidget::branch:closed:has-children:has-siblings {\n"
"    margin-top: 2px;\n"
"    margin-left: 2px;\n"
"    image: url(\'../CXA_Icon/tree_widget/plus.png\');\n"
"\n"
"}\n"
"\n"
"QTreeWidget::branch:has-children:!has-siblings:closed {\n"
"    margin-top: 2px;\n"
"    margin-left: 2px;\n"
"    border: 1px solid #d9d9d9;\n"
"    border-right: 0 solid transparent;\n"
"    margin-bottom: 2px;\n"
"    image: url(\'../CXA_Icon/tree_widget/plus.png\');\n"
"}\n"
"\n"
"QTreeWidget::branch:open:has-children:has-siblings {\n"
"    margin-top: 2px;\n"
"    margin-left: 2px;\n"
"    image: url(\'../CXA_Icon/tree_widget/minus.png\');\n"
"}\n"
"\n"
"QTreeWidget::branch:open:has-children:!has-siblings {\n"
"    margin-top: 2px;\n"
"    margin-left: 2px;\n"
"    border: 1px solid #d9d9d9;\n"
"    border-right: 0 solid transparent;\n"
"    margin-bottom: 2px;\n"
"    image: url(\'../CXA_Icon/tree_widget/minus.png\');\n"
"}\n"
"/*QComboBox*/\n"
"QComboBox {\n"
"    border: 1px solid #aab2bd;\n"
"    border-radius: 4px;\n"
"    font-size: 14px;\n"
"    font-weight: 1000;\n"
"    padding: 5px 10px;\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"    background-color: transparent;\n"
"}\n"
"\n"
"QComboBox::down-arrow {\n"
"    image: url(\"../CXA_Icon/combox/more.png\");\n"
"    padding-right: 10px;\n"
"    padding-top: 2px;\n"
"\n"
"}\n"
"\n"
"QComboBox::!editable:on {\n"
"    border: 1px solid #3bafda;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView{\n"
"    border: 2px solid #e6e9ed;\n"
"    outline: none;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView::item{\n"
"    height: 35px;\n"
"    border-bottom: 1px solid #e6e9ed;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView::item:hover{\n"
"    background-color: #3bafda;\n"
"    color: #FFFFFF;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView::item:selected{\n"
"    background-color: #3bafda;\n"
"    color: #FFFFFF;\n"
"}\n"
"\n"
"/*QSlider*/\n"
"QSlider::groove:horizontal{\n"
"    border:0px;\n"
"    height:8px;\n"
"}\n"
"\n"
"QSlider::sub-page:horizontal{\n"
"    background:lightblue;\n"
"}\n"
"\n"
"QSlider::add-page:horizontal{\n"
"    background:lightgray;\n"
"}\n"
"\n"
"QSlider::handle:horizontal{\n"
"    background:lightblue;\n"
"    width:10px;\n"
"    border-radius:5px;\n"
"    margin:-3px 0px -3px 0px;\n"
"}\n"
"\n"
"QSlider::groove:vertical{\n"
"    border:0px;\n"
"    width:8px;\n"
"}\n"
"\n"
"QSlider::sub-page:vertical{\n"
"    background:lightblue;\n"
"}\n"
"\n"
"QSlider::add-page:vertical{\n"
"    background:lightgray;\n"
"}\n"
"\n"
"QSlider::handle:vertical{\n"
"    background:lightblue;\n"
"    height:10px;\n"
"    border-radius:5px;\n"
"    margin:0px -3px 0px -3px;\n"
"}\n"
"/*QListWidget,QListView*/\n"
"QListWidget,QListView {\n"
"    border: 1px solid #ccd1d9;\n"
"    outline: none;\n"
"    padding: 0;\n"
"}\n"
"\n"
"QListWidget::item,QListView::item {\n"
"    padding-left: 5px;\n"
"    border-bottom: 1px solid #e6e9ed;\n"
"}\n"
"\n"
"QListWidget::item:hover,QListView::item:hover{\n"
"    background-color: rgb(150, 150, 157);\n"
"    color: #FFFFFF;\n"
"}\n"
"\n"
"QListWidget::item:selected,QListView::item:selected{\n"
"    background-color: rgb(150, 150, 157);\n"
"    color: #FFFFFF;\n"
"}\n"
"\n"
"QPushButton {\n"
"    \n"
"    background-color: rgb(255, 216, 115);\n"
"    color: #fff;\n"
"    border: 0px solid rgba(255, 255, 255, 0);\n"
"    font-size: 18px;\n"
"    font-weight: 700;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #4fc1e9;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background: qradialgradient(cx:0.5,\n"
"    cy: 0.5,\n"
"    fx: 0.5,\n"
"    fy: 0.5,\n"
"    radius: 1.5,\n"
"    stop: 0.2 #4fc1e9,\n"
"    stop: 0.8 #3bafda);\n"
"}\n"
"")
        self.Main_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.Main_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.Main_frame.setObjectName("Main_frame")
        self.verticalLayout = QtGui.QVBoxLayout(self.Main_frame)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self._top_frame = QtGui.QFrame(self.Main_frame)
        self._top_frame.setMinimumSize(QtCore.QSize(0, 0))
        self._top_frame.setMaximumSize(QtCore.QSize(16777215, 40))
        self._top_frame.setStyleSheet("")
        self._top_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self._top_frame.setFrameShadow(QtGui.QFrame.Raised)
        self._top_frame.setLineWidth(1)
        self._top_frame.setMidLineWidth(0)
        self._top_frame.setObjectName("_top_frame")
        self.horizontalLayout = QtGui.QHBoxLayout(self._top_frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(10, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.module_switch_comboBox = QtGui.QComboBox(self._top_frame)
        self.module_switch_comboBox.setMinimumSize(QtCore.QSize(120, 25))
        self.module_switch_comboBox.setObjectName("module_switch_comboBox")
        self.horizontalLayout.addWidget(self.module_switch_comboBox)
        spacerItem1 = QtGui.QSpacerItem(130, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.main_title_data_label = QtGui.QLabel(self._top_frame)
        self.main_title_data_label.setMinimumSize(QtCore.QSize(400, 0))
        self.main_title_data_label.setObjectName("main_title_data_label")
        self.horizontalLayout.addWidget(self.main_title_data_label)
        spacerItem2 = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.main_serch_lineEdit = QtGui.QLineEdit(self._top_frame)
        self.main_serch_lineEdit.setMinimumSize(QtCore.QSize(160, 0))
        self.main_serch_lineEdit.setMaximumSize(QtCore.QSize(160, 16777215))
        self.main_serch_lineEdit.setStyleSheet("")
        self.main_serch_lineEdit.setText("")
        self.main_serch_lineEdit.setEchoMode(QtGui.QLineEdit.Normal)
        self.main_serch_lineEdit.setDragEnabled(False)
        self.main_serch_lineEdit.setReadOnly(False)
        self.main_serch_lineEdit.setObjectName("main_serch_lineEdit")
        self.horizontalLayout.addWidget(self.main_serch_lineEdit)
        self.icon_zoom_Slider = QtGui.QSlider(self._top_frame)
        self.icon_zoom_Slider.setMinimumSize(QtCore.QSize(50, 0))
        self.icon_zoom_Slider.setMaximumSize(QtCore.QSize(100, 16777215))
        self.icon_zoom_Slider.setMinimum(20)
        self.icon_zoom_Slider.setMaximum(100)
        self.icon_zoom_Slider.setOrientation(QtCore.Qt.Horizontal)
        self.icon_zoom_Slider.setObjectName("icon_zoom_Slider")
        self.horizontalLayout.addWidget(self.icon_zoom_Slider)
        spacerItem3 = QtGui.QSpacerItem(433, 17, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.verticalLayout.addWidget(self._top_frame)
        self.splitter = QtGui.QSplitter(self.Main_frame)
        self.splitter.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.splitter.setStyleSheet("")
        self.splitter.setFrameShape(QtGui.QFrame.NoFrame)
        self.splitter.setFrameShadow(QtGui.QFrame.Sunken)
        self.splitter.setMidLineWidth(1)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setHandleWidth(1)
        self.splitter.setObjectName("splitter")
        self._lift_frame = QtGui.QFrame(self.splitter)
        self._lift_frame.setMinimumSize(QtCore.QSize(200, 0))
        self._lift_frame.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self._lift_frame.setStyleSheet("")
        self._lift_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self._lift_frame.setFrameShadow(QtGui.QFrame.Raised)
        self._lift_frame.setObjectName("_lift_frame")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self._lift_frame)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.main_file_tree = QtGui.QTreeWidget(self._lift_frame)
        self.main_file_tree.setMinimumSize(QtCore.QSize(200, 0))
        self.main_file_tree.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.main_file_tree.setStyleSheet("background-color: rgb(245, 245, 247);")
        self.main_file_tree.setFrameShape(QtGui.QFrame.NoFrame)
        self.main_file_tree.setFrameShadow(QtGui.QFrame.Raised)
        self.main_file_tree.setAutoScroll(True)
        self.main_file_tree.setColumnCount(1)
        self.main_file_tree.setObjectName("main_file_tree")
        item_0 = QtGui.QTreeWidgetItem(self.main_file_tree)
        item_0 = QtGui.QTreeWidgetItem(self.main_file_tree)
        item_0 = QtGui.QTreeWidgetItem(self.main_file_tree)
        item_0 = QtGui.QTreeWidgetItem(self.main_file_tree)
        item_1 = QtGui.QTreeWidgetItem(item_0)
        self.main_file_tree.header().setDefaultSectionSize(100)
        self.main_file_tree.header().setMinimumSectionSize(21)
        self.verticalLayout_2.addWidget(self.main_file_tree)
        self.line = QtGui.QFrame(self._lift_frame)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_2.addWidget(self.line)
        self._center_frame = QtGui.QFrame(self.splitter)
        self._center_frame.setMinimumSize(QtCore.QSize(0, 0))
        self._center_frame.setStyleSheet("")
        self._center_frame.setFrameShape(QtGui.QFrame.Panel)
        self._center_frame.setFrameShadow(QtGui.QFrame.Raised)
        self._center_frame.setObjectName("_center_frame")
        self.verticalLayout_4 = QtGui.QVBoxLayout(self._center_frame)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.stackedWidget = QtGui.QStackedWidget(self._center_frame)
        self.stackedWidget.setObjectName("stackedWidget")
        self.serch_page = QtGui.QWidget()
        self.serch_page.setObjectName("serch_page")
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.serch_page)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.serch_listWidget = QtGui.QListWidget(self.serch_page)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.serch_listWidget.sizePolicy().hasHeightForWidth())
        self.serch_listWidget.setSizePolicy(sizePolicy)
        self.serch_listWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.serch_listWidget.setMaximumSize(QtCore.QSize(16777214, 16777215))
        self.serch_listWidget.setMovement(QtGui.QListView.Static)
        self.serch_listWidget.setResizeMode(QtGui.QListView.Adjust)
        self.serch_listWidget.setLayoutMode(QtGui.QListView.SinglePass)
        self.serch_listWidget.setViewMode(QtGui.QListView.IconMode)
        self.serch_listWidget.setObjectName("serch_listWidget")
        self.verticalLayout_6.addWidget(self.serch_listWidget)
        spacerItem4 = QtGui.QSpacerItem(1100, 1, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.verticalLayout_6.addItem(spacerItem4)
        self.stackedWidget.addWidget(self.serch_page)
        self.verticalLayout_4.addWidget(self.stackedWidget)
        self._right_frame = QtGui.QFrame(self.splitter)
        self._right_frame.setMinimumSize(QtCore.QSize(0, 0))
        self._right_frame.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self._right_frame.setStyleSheet("")
        self._right_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self._right_frame.setFrameShadow(QtGui.QFrame.Raised)
        self._right_frame.setObjectName("_right_frame")
        self.verticalLayout_5 = QtGui.QVBoxLayout(self._right_frame)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.samp_info_stacked = QtGui.QStackedWidget(self._right_frame)
        self.samp_info_stacked.setObjectName("samp_info_stacked")
        self.verticalLayout_5.addWidget(self.samp_info_stacked)
        self.verticalLayout.addWidget(self.splitter)
        self.line_2 = QtGui.QFrame(self.Main_frame)
        self.line_2.setMaximumSize(QtCore.QSize(16777215, 1))
        self.line_2.setStyleSheet("background-color: rgb(60, 123, 200);")
        self.line_2.setFrameShadow(QtGui.QFrame.Raised)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout.addWidget(self.line_2)
        self._buttom_frame = QtGui.QFrame(self.Main_frame)
        self._buttom_frame.setMinimumSize(QtCore.QSize(30, 0))
        self._buttom_frame.setMaximumSize(QtCore.QSize(16777215, 30))
        self._buttom_frame.setStyleSheet("QFrame{\n"
"    background-color: rgb(71, 145, 235);\n"
"}")
        self._buttom_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self._buttom_frame.setFrameShadow(QtGui.QFrame.Raised)
        self._buttom_frame.setObjectName("_buttom_frame")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self._buttom_frame)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem5 = QtGui.QSpacerItem(1415, 7, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem5)
        self.verticalLayout.addWidget(self._buttom_frame)
        self.verticalLayout_3.addWidget(self.Main_frame)

        self.retranslateUi(Main_Function_area_Form)
        QtCore.QMetaObject.connectSlotsByName(Main_Function_area_Form)

    def retranslateUi(self, Main_Function_area_Form):
        Main_Function_area_Form.setWindowTitle(QtGui.QApplication.translate("Main_Function_area_Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.main_title_data_label.setText(QtGui.QApplication.translate("Main_Function_area_Form", "这里将会显示选择Asseat的文件层级!!!", None, QtGui.QApplication.UnicodeUTF8))
        self.main_serch_lineEdit.setPlaceholderText(QtGui.QApplication.translate("Main_Function_area_Form", " Please search here ...", None, QtGui.QApplication.UnicodeUTF8))
        self.main_file_tree.headerItem().setText(0, QtGui.QApplication.translate("Main_Function_area_Form", "Name", None, QtGui.QApplication.UnicodeUTF8))
        __sortingEnabled = self.main_file_tree.isSortingEnabled()
        self.main_file_tree.setSortingEnabled(False)
        self.main_file_tree.topLevelItem(0).setText(0, QtGui.QApplication.translate("Main_Function_area_Form", "Vray", None, QtGui.QApplication.UnicodeUTF8))
        self.main_file_tree.topLevelItem(1).setText(0, QtGui.QApplication.translate("Main_Function_area_Form", "Arnold", None, QtGui.QApplication.UnicodeUTF8))
        self.main_file_tree.topLevelItem(2).setText(0, QtGui.QApplication.translate("Main_Function_area_Form", "Redshift", None, QtGui.QApplication.UnicodeUTF8))
        self.main_file_tree.topLevelItem(3).setText(0, QtGui.QApplication.translate("Main_Function_area_Form", "HDR", None, QtGui.QApplication.UnicodeUTF8))
        self.main_file_tree.topLevelItem(3).child(0).setText(0, QtGui.QApplication.translate("Main_Function_area_Form", "Room", None, QtGui.QApplication.UnicodeUTF8))
        self.main_file_tree.setSortingEnabled(__sortingEnabled)

