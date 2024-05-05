import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PIL import ImageGrab
import numpy as np
import cv2

class HaloWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.current_color = QtGui.QColor(255, 0, 0, 120)  # 初始化为红色
        self.initUI()
        self.dragPosition = None
        self.timer = QtCore.QTimer(self)  # 定时器用于周期性检查颜色
        self.timer.timeout.connect(self.updateColor)
        self.timer.start(10)  # 每x毫秒检查一次

    def initUI(self):
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 200, 200)  # 初始位置和大小

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setBrush(QtCore.Qt.NoBrush)
        qp.setPen(QtGui.QPen(self.current_color, 10))
        qp.drawEllipse(10, 10, 180, 180)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()
            self.updateColor()  # 在移动时也更新颜色

    def updateColor(self):
        x, y = self.pos().x(), self.pos().y()
        img = ImageGrab.grab(bbox=(x+10, y+10, x+190, y+190))
        img_np = np.array(img)
        if not self.contains_yellow(img_np):
            self.current_color = QtGui.QColor(0, 255, 0, 120)  # 无黄色时为绿色
        else:
            self.current_color = QtGui.QColor(255, 0, 0, 120)  # 否则为红色
        self.update()  # 触发重绘

    def contains_yellow(self, img_np):
        yellow_min = np.array([200, 100, 0], np.uint8)
        yellow_max = np.array([255, 255, 100], np.uint8)
        yellow_mask = cv2.inRange(img_np, yellow_min, yellow_max)
        return np.any(yellow_mask)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    halo = HaloWidget()
    halo.show()
    sys.exit(app.exec_())