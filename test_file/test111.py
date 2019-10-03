from PyQt4.QtGui import *



class Test(QWidget):
    def __init__(self,parent=None):
        super(Test, self).__init__(parent)
        lay = QVBoxLayout()
        self.setLayout(lay)

        self.listWidget = QListWidget()
        self.listWidget.setObjectName('ha')
        self.listWidget.addItem('hahahahha')

        self.listWidget1 = QListWidget()
        self.listWidget1.setObjectName('123')
        self.listWidget1.addItem('123123323')

        self.stacked = QStackedWidget()
        self.stacked.addWidget(self.listWidget)
        self.stacked.addWidget(self.listWidget1)

        self.btn1 = QPushButton('hahah')
        self.btn1.clicked.connect(self.test)
        self.btn2 = QPushButton('123123132')
        self.btn2.clicked.connect(self.test1)
        lay.addWidget(self.stacked)
        lay.addWidget(self.btn1)
        lay.addWidget(self.btn2)

    def test(self):
        print self.findChild(QListWidget,'ha')
        self.stacked.setCurrentWidget(self.listWidget)

    def test1(self):
        print self.listWidget1.objectName()
        self.stacked.setCurrentWidget(self.listWidget1)
app = QApplication([])
t = Test()
t.show()
app.exec_()