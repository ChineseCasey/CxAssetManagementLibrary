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

from CXA_UIPY.Title import Ui_title_Form
from CXA_Script.CXMainFunctionArea import MainFunctionArea
import sys
import math

import CXA_Rely.get_project_path as Cpath

class CXAssetLibrary(QWidget):
    def __init__(self, parent=None, face_num=1, face_time=1000, title=u'AssetLibrary', color_enable=True, move_enable=True):
        super(CXAssetLibrary, self).__init__(parent)
        self.icon = Cpath.get_icon_path() +'/title_icon.png'
        self._title_icon = QPixmap(self.icon)
        self.margin_num = 6
        self.round_num = 0
        self._move_enable = move_enable
        self._face_time = face_time
        self._face_num = face_num
        self._left_button = False
        self._x_move_enbale = False
        self._y_move_enbale = False
        self._move_num = 10
        self._window_size = 1
        self._color = QColor(100, 130, 250, 255)
        self.win_hint = 1
        self.setWindowTitle(title)
        self.__init_ui()

        self.set_window_title(title)
        if color_enable:
            self._user_color_ctrl()

        self._set_window_ctrl()

        #self._user_test_wid()


    def __init_ui(self):

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowIcon(self._title_icon)

        self.setMinimumSize(1200,700)

        self._widget_layout = QVBoxLayout(self)
        self._widget_layout.setSpacing(0)
        self._widget_layout.setContentsMargins(6, 5, 6, 5)

        self._title_widget_layout = QHBoxLayout()
        self._title_widget_layout.setSpacing(0)
        self._title_widget_layout.setContentsMargins(0, 0, 0, 0)

        self._main_widget_layout = QHBoxLayout()
        self._main_widget_layout.setSpacing(0)
        self._main_widget_layout.setContentsMargins(0, 0, 1, 3)

        self._widget_layout.addLayout(self._title_widget_layout)
        self._widget_layout.addLayout(self._main_widget_layout)

        self._window_title = Ui_title_Form()
        self._window_title.setupUi(self)
        self._window_title.lineEdit.setVisible(0)

        self._window_title.icon_label.setPixmap(self._title_icon)
        '''设置按钮的样式类'''
        self._window_title._close_btn.setProperty('class','close')
        self._window_title._max_btn.setProperty('class', 'max')
        self._window_title._min_btn.setProperty('class', 'min')
        self._window_title.top_set_btn.setProperty('class', 'zhiding')

        self._window_title.top_set_btn.clicked.connect(self._user_tophint)
        self._window_title.title_frame.mouseDoubleClickEvent = lambda *args: self._set_window_size()


        self._title_widget_layout.addWidget(self._window_title.title_frame)

        self._ctrl_layout = QHBoxLayout()
        self.setMouseTracking(True)

        self.main_widget = QWidget()
        self.main_widget.setMouseTracking(True)
        #self._main_widget_layout.addWidget(self.main_widget)

        '''这里设置主layout'''
        self._main_win = MainFunctionArea()
        self._main_widget_layout.addWidget(self._main_win.Main_frame)

    def _user_tophint(self):
        if self.win_hint:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnBottomHint)
            self.win_hint=0
            self.show()
        else:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
            self.win_hint=1
            self.show()

    def set_window_title(self, title):
        self._window_title.title_label.setText(' ' * 2 + title)

    def _user_color_ctrl(self):
        self._color_pb = self._window_title.color_pd_btn
        self._color_pb.setMaximumSize(32, 30)
        self._color_pb.setMinimumSize(32, 30)
        self._color_pb.clicked.connect(self._color_dialog_call)

    def _color_dialog_call(self):
        self._color_dialog = QColorDialog()
        self._color_dialog.setOption(QColorDialog.ShowAlphaChannel)
        self._color_dialog.currentColorChanged.connect(self.change_color)
        self._color_dialog.show()

    def change_color(self, color):
        self._color = color
        self.update()

    def _set_window_ctrl(self):
        self._lower_button = self._window_title._min_btn
        self._lower_button.clicked.connect(self.showMinimized)

        self._maximized_button = self._window_title._max_btn
        self._maximized_button.clicked.connect(self._set_window_size)

        self._close_button = self._window_title._close_btn

    def _set_window_size(self):
        if self._window_size == 1:
            self.showMaximized()
            self._window_size = 2
        elif self._window_size == 2:
            self.showNormal()
            self._window_size = 1
        self.update()

    def _face_in(self):
        u"""淡入功能函数"""
        self._face_ani_in = QPropertyAnimation(self, 'windowOpacity')
        self._face_ani_in.setStartValue(0)
        self._face_ani_in.setEndValue(self._face_num)
        self._face_ani_in.setDuration(self._face_time)
        self._face_ani_in.setEasingCurve(QEasingCurve.Linear)
        self._face_ani_in.start()

    def _face_out(self):
        u"""淡出功能函数"""
        self._face_ani_out = QPropertyAnimation(self, 'windowOpacity')
        self._face_ani_out.setStartValue(self._face_num)
        self._face_ani_out.setEndValue(0)
        self._face_ani_out.setDuration(self._face_time)
        self._face_ani_out.setEasingCurve(QEasingCurve.Linear)
        self._face_ani_out.finished.connect(self.close)
        self._face_ani_out.start()

    def show(self, *args, **kwargs):
        u"""重写show函数加入淡入功能"""
        super(CXAssetLibrary, self).show()
        self._face_in()
        self._close_button.clicked.connect(self._face_out_close)

    def _face_out_close(self):
        u"""关闭功能函数加入淡出功能"""
        self._face_out()
        self._close_button.clicked.disconnect()

    def mousePressEvent(self, event):
        u"""重写鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self._left_button = True
            self._m_point = event.pos()
            self._widget_geometry = self.geometry()
            self._x_move_enbale = self._m_point.x() > self._widget_geometry.width() - self._move_num
            self._y_move_enbale = self._m_point.y() > self._widget_geometry.height() - self._move_num

    def mouseMoveEvent(self, event):
        u"""重写鼠标移动事件"""
        x_move = event.pos().x() > self.geometry().width() - self._move_num
        y_move = event.pos().y() > self.geometry().height() - self._move_num
        if x_move and y_move:
            self.setCursor(Qt.SizeFDiagCursor)
        elif x_move:
            self.setCursor(Qt.SizeHorCursor)
        elif y_move:
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        if self._x_move_enbale and self._y_move_enbale:
            self.setGeometry(self._widget_geometry.x(), self._widget_geometry.y(),
                             max(self._widget_geometry.width() + event.pos().x() - self._m_point.x(), 0),
                             max(self._widget_geometry.height() + event.pos().y() - self._m_point.y(), 0))

        elif self._x_move_enbale:
            self.setGeometry(self._widget_geometry.x(), self._widget_geometry.y(),
                             max(self._widget_geometry.width() + event.pos().x() - self._m_point.x(), 0),
                             self._widget_geometry.height())

        elif self._y_move_enbale:
            self.setGeometry(self._widget_geometry.x(), self._widget_geometry.y(), self._widget_geometry.width(),
                             max(self._widget_geometry.height() + event.pos().y() - self._m_point.y(), 0))
        else:
            if self._move_enable:
                if self._left_button:
                    self.move(event.globalPos() - self._m_point)

    def mouseReleaseEvent(self, event):
        u"""重写鼠标放开事件"""
        if event.button() == Qt.LeftButton:
            self._x_move_enbale = False
            self._y_move_enbale = False
            self._left_button = False

    def paintEvent(self, event):
        u"""重新绘图事件"""
        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)

        if self._window_size == 1:
            path.addRoundedRect(self.margin_num, self.margin_num, self.width() - self.margin_num *2 ,
                                self.height() - self.margin_num * 2, self.round_num, self.round_num)
        elif self._window_size == 2:
            path.addRoundedRect(0, 0, self.width(), self.height(), self.round_num, self.round_num)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.fillPath(path, QBrush(QColor(240, 240, 240, 255)))

        if self._window_size == 1:
            _range = range(self.margin_num)
            attenuation = 80
            max_a = math.sqrt(max(_range)) * attenuation

            for i in _range:
                s_path = QPainterPath()
                s_path.setFillRule(Qt.WindingFill)
                rect = QRectF(self.margin_num - i, self.margin_num - i, self.width() - (self.margin_num - i) * 2,
                              self.height() - (self.margin_num - i) * 2)
                s_path.addRoundedRect(rect, self.round_num, self.round_num)
                '''亮边'''

                self._color.setAlpha(max_a - math.sqrt(i) * attenuation)
                painter.setPen(self._color)
                painter.drawPath(s_path)

    def main(self):
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    CXAL = CXAssetLibrary()
    CXAL.main()
    sys.exit(app.exec_())