#coding=utf-8

from PyQt4 import QtGui,QtCore
import sys

img_file = 'D:/CxAssetManagementLibrary/test_file/mimi.jpg'


class TestWin(QtGui.QWidget):
    def __init__(self,parent):
        super(TestWin, self).__init__(parent)
        self.main_win = QtGui.QVBoxLayout()
        self.setLayout(self.main_win)
        self.listwidget = QtGui.QListWidget()
        self.listwidget.setViewMode(QtGui.QListView.IconMode)
        self.listwidget.setMovement(QtGui.QListView.Static)
        #self.listwidget.setIconSize(QtCore.QSize(100,100))

        self.main_win.addWidget(self.listwidget)

        self.pixmap = QtGui.QPixmap(img_file)
        self.icon = QtGui.QIcon(self.pixmap)
        for i in range(10):
            self.tlist = test(img_file)
            self.listwidgetitem = QtGui.QListWidgetItem(self.listwidget)

            self.listwidgetitem.setSizeHint(self.tlist.sizeHint())
            #self.listwidgetitem.setIcon(self.icon)

            self.listwidget.addItem(self.listwidgetitem)
            self.listwidget.setItemWidget(self.listwidgetitem,self.tlist)

        self.btn = QtGui.QPushButton('test')
        self.main_win.addWidget(self.btn)

    def set_item_size(self):
        self.tlist.set_size(100*2,100*2)

class test(QtGui.QLabel):
    def __init__(self,pix,parent=None):
        super(test, self).__init__(parent)
        self.pixmap = QtGui.QPixmap(pix)
        self.pixmap.size()
        self.setText('asdasdasd')
        self.setPixmap(self.pixmap)
        self.setScaledContents(1)
        self.setFixedSize(10,10)
    def set_size(self,w,h):
        self.setFixedSize(w,h)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    tw = TestWin(None)
    tw.show()
    app.exec_()