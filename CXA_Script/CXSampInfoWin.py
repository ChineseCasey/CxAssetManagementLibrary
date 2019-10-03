#coding=utf-8
import imp

try:
    imp.find_module('PySide2')
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
except:
    from PySide.QtGui import *
    from PySide.QtCore import *

from CXA_UIPY.SampInfo_Win import Ui_SampInfoForm

class SampInfoWin(QWidget,Ui_SampInfoForm):

    def __init__(self,icon_path,name,type,filetype,filesize,setdate,filepath,version=[],parent=None):
        super(SampInfoWin, self).__init__(parent)
        self.setupUi(self)

        self.icon = icon_path
        self.name = name
        self.type = type
        self.file_type = filetype
        self.file_size = filesize
        self.set_date = setdate
        self.version = version
        self.file_path = filepath

        self.pixmap = QPixmap(self.icon)
        self.samp_info_image_label.setPixmap(self.pixmap)
        #self.samp_info_image_label.setScaledContents(True)
        self.name_label.setText(self.name)
        self.type_label.setText(self.type)
        self.file_label.setText(self.file_type)
        self.file_Size_label.setText(self.file_size)
        self.date_label.setText(self.set_date)
        self.asseat_path.setText(self.file_path)
        self.asseat_path.setVisible(0)

    def create_version(self):
        if self.version:
            for v in self.version:
                self.Version_comboBox.addItem(v)
    '''
    def import_asseat(self):
        '''

if __name__ == '__main__':
    app = QApplication([])
    SIW = SampInfoWin()
    SIW.show()
    app.exec_()