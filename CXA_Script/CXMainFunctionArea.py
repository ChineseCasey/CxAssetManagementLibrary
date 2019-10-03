# coding=utf-8
import imp

try:
    imp.find_module('PySide2')
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
except:
    from PySide.QtGui import *
    from PySide.QtCore import *

import os,sys

from CXA_UIPY.Main_Win import Ui_Main_Function_area_Form
from CXA_UIPY.Icon_Widget import Ui_UI_IconWidget
import CXA_Rely.get_project_path as Cpath
from CXA_Script.CXDataFile import GetAsseatData
from CXA_Script.CXSampInfoWin import SampInfoWin

class MainFunctionArea(QWidget,Ui_Main_Function_area_Form):

    def __init__(self,parent=None):
        super(MainFunctionArea, self).__init__(parent)
        self.Icon_list_widget_list = []
        self.setupUi(self)
        self.icon_size = 100
        self.splitter.setFixedWidth(350)


        self.serch_listWidget.setIconSize(QSize(self.icon_size,self.icon_size))
        self.icon_zoom_Slider.valueChanged.connect(self.set_serch_list_size)
        self.main_file_tree.itemClicked.connect(lambda item, column: self.stackedWidget.setCurrentIndex(item.data(column, Qt.UserRole))

        if item.data(column, Qt.UserRole) is not None else None)
        self.module_switch_comboBox.currentIndexChanged.connect(self._current_moudle_treeWidget)

        self.nothing()
        #self._test_img()
        self.create_moudle_list()



    def _test_img(self):
        image = Cpath.get_icon_path()+'/title_icon.png'

        img = QPixmap(image)

        self.icon = QIcon(img)
        for i in range(50):
            self.widitem = QListWidgetItem()
            self.widitem.setIcon(self.icon)
            self.widitem.setText('Test{d}'.format(d=str(i)))
            self.serch_listWidget.addItem(self.widitem)

    def nothing(self):
        self.nothing = QLabel(' ')
        self.samp_info_stacked.addWidget(self.nothing)
        self.samp_info_stacked.setCurrentWidget(self.nothing)

    def get_moudle_data(self,path):
        return os.listdir(path)

    def create_moudle_list(self):
        for moudle in self.get_moudle_data(Cpath.get_library_path()):
            self.module_switch_comboBox.addItem(moudle)

    def _current_moudle_treeWidget(self):
        data = GetAsseatData()
        self.data = data.moudle_dict
        self.del_TreeWidget_list()
        current_moudle = self.module_switch_comboBox.currentText()

        for moudle in self.data.get(current_moudle):
            tree_child = QTreeWidgetItem(self.main_file_tree)
            tree_child.setText(0,moudle)


            for type in self.data[current_moudle].get(moudle):
                self.icon_data = self.data[current_moudle][moudle].get(type)

                self.list_widget = self.create_Icon_Widget(self.stackedWidget,self.icon_data)
                self.child_one = QTreeWidgetItem(tree_child)
                self.child_one.setText(0, type)
                self.child_one.setData(0, Qt.UserRole, self.stackedWidget.addWidget(self.list_widget))

                for a in self.icon_data:
                    child_two = QTreeWidgetItem(self.child_one)
                    child_two.setText(0, a)

    def create_Icon_Widget(self,ui_parent,asseat_path):
        self.asseat_path = asseat_path
        self.icon_widget = QListWidget()
        self.icon_widget.setViewMode(QListView.IconMode)
        self.icon_widget.setMovement(QListView.Static)
        self.icon_widget.setIconSize(QSize(140,140))
        self.icon_widget.setResizeMode(QListView.Adjust)
        self.Icon_list_widget_list.append(self.icon_widget)

        for i in self.asseat_path:
            icon = self.asseat_path[i].get('samp_icon')
            self.img = QPixmap(icon)
            self.icon = QIcon(self.img)
            self.widitem = QListWidgetItem()
            self.widitem.setIcon(self.icon)
            self.widitem.setText('{d}'.format(d=str(i)))
            self.icon_widget.addItem(self.widitem)

            name = self.asseat_path[i].get('samp_name')
            type = self.asseat_path[i].get('samp_type')
            filetype = self.asseat_path[i].get('samp_file_type')
            filesize = self.asseat_path[i].get('samp_file_size')
            setdate = self.asseat_path[i].get('samp_data')
            version = self.asseat_path[i].get('samp_version')
            file_path = self.asseat_path[i].get('samp_import')

            self.samp_info_win = SampInfoWin(icon, name, type, filetype, filesize, setdate, file_path, version)
            self.widitem.setData(Qt.UserRole,self.samp_info_stacked.addWidget(self.samp_info_win.samp_info_frame))

        self.icon_widget.itemClicked.connect(lambda item: self.samp_info_stacked.setCurrentIndex(item.data( Qt.UserRole)))

        return self.icon_widget


    def del_TreeWidget_list(self):
        self.main_file_tree.clear()

    def set_press_index(self):
        print 'adasdasd'

    def set_serch_list_size(self):
        size = int(self.icon_zoom_Slider.value())*2
        for i in self.Icon_list_widget_list:
            i.setIconSize(QSize(self.icon_size+size,self.icon_size+size))
        print self.icon_size,size,self.icon_size+size
        self.serch_listWidget.setIconSize(QSize(self.icon_size+size,self.icon_size+size))

if __name__ == '__main__':
    app = QApplication([])
    MFA = MainFunctionArea()
    MFA.show()
    app.exec_()