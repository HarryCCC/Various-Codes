import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PIL import ImageGrab
import numpy as np
import cv2
import pyautogui
import time

class HaloWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.current_color_1 = QtGui.QColor(255, 0, 0, 120)
        self.current_color_2 = QtGui.QColor(255, 0, 0, 120)
        self.last_color_1 = None
        self.last_color_2 = None
        self.last_click_time = 0  # 初始化上次点击时间为0
        self.initUI()
        self.dragPosition = None
        self.operationArea = QtCore.QRect(1750, 1200, 100, 100)
        self.captureArea_1 = QtCore.QRect(1110, 620, 125, 250)
        self.captureArea_2 = QtCore.QRect(1110, 890, 125, 250)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateColor)
        self.timer.start(1) # 程序刷新频率
        self.isRunning = False

    def initUI(self):
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        desktop = QtWidgets.QApplication.desktop()
        screen_rect = desktop.screenGeometry()
        self.setGeometry(0, 0, screen_rect.width(), screen_rect.height())
        self.showInstructions()

    def showInstructions(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Adjust the detection and operation areas, then press Enter to start or Esc to exit.")
        msg.setWindowTitle("Instructions")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setBrush(QtCore.Qt.NoBrush)

        # 旋转识别区1
        qp.save()  # 保存当前画笔状态
        center1 = self.captureArea_1.center()
        qp.translate(center1.x(), center1.y())
        qp.rotate(-20)  # 旋转-n度
        qp.translate(-center1.x(), -center1.y())
        qp.setPen(QtGui.QPen(self.current_color_1, 10))
        qp.drawRect(self.captureArea_1)
        qp.drawText(self.captureArea_1.translated(-center1.x() + center1.x(), -center1.y() + center1.y()), QtCore.Qt.AlignCenter, "识别区1")
        qp.restore()  # 恢复画笔状态

        # 旋转识别区2
        qp.save()
        center2 = self.captureArea_2.center()
        qp.translate(center2.x(), center2.y())
        qp.rotate(20)  # 旋转n度
        qp.translate(-center2.x(), -center2.y())
        qp.setPen(QtGui.QPen(self.current_color_2, 10))
        qp.drawRect(self.captureArea_2)
        qp.drawText(self.captureArea_2.translated(-center2.x() + center2.x(), -center2.y() + center2.y()), QtCore.Qt.AlignCenter, "识别区2")
        qp.restore()

        # 绘制操作区，不旋转
        if not self.isRunning:
            qp.setPen(QtGui.QPen(QtGui.QColor(255, 255, 0), 4))
            qp.setBrush(QtGui.QColor(255, 255, 0, 120))
            qp.drawRect(self.operationArea)
            qp.drawText(self.operationArea, QtCore.Qt.AlignCenter, "操作区")

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        elif event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            self.isRunning = True
            self.update()  # Refresh to remove the operation zone from the display

    def mousePressEvent(self, event):
        if not self.isRunning:  # Only allow moving areas if not running
            if self.captureArea_1.contains(event.pos()):
                self.dragPosition = event.globalPos() - self.captureArea_1.topLeft()
                event.accept()
            elif self.captureArea_2.contains(event.pos()):
                self.dragPosition = event.globalPos() - self.captureArea_2.topLeft()
                event.accept()
            elif self.operationArea.contains(event.pos()):
                self.dragPosition = event.globalPos() - self.operationArea.topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton and self.dragPosition is not None:
            new_pos = event.globalPos() - self.dragPosition
            if self.operationArea.contains(event.pos()) and not self.isRunning:
                self.operationArea.moveTopLeft(new_pos)
            elif self.captureArea_1.contains(event.pos()):
                self.captureArea_1.moveTopLeft(new_pos)
            elif self.captureArea_2.contains(event.pos()):
                self.captureArea_2.moveTopLeft(new_pos)
            self.update()
            event.accept()

    def updateColor(self):
        if not self.isRunning:
            return
        current_time = time.time()
        img_1 = ImageGrab.grab(bbox=(self.captureArea_1.x(), self.captureArea_1.y(),
                                     self.captureArea_1.x() + self.captureArea_1.width(),
                                     self.captureArea_1.y() + self.captureArea_1.height()))
        img_np_1 = np.array(img_1)
        self.current_color_1 = self.detect_color(img_np_1)

        img_2 = ImageGrab.grab(bbox=(self.captureArea_2.x(), self.captureArea_2.y(),
                                     self.captureArea_2.x() + self.captureArea_2.width(),
                                     self.captureArea_2.y() + self.captureArea_2.height()))
        img_np_2 = np.array(img_2)
        self.current_color_2 = self.detect_color(img_np_2)

        if self.current_color_1 == QtGui.QColor(0, 255, 0, 120) and self.current_color_2 == QtGui.QColor(0, 255, 0, 120):
            if (current_time - self.last_click_time > 1.5):  # 检查是否已经过去了n秒
                self.autoClickInOperationArea()
                self.last_click_time = current_time  # 更新上次点击时间
        self.update()

    def detect_color(self, img_np):
        if not self.contains_yellow(img_np):
            return QtGui.QColor(0, 255, 0, 120)
        return QtGui.QColor(255, 0, 0, 120)

    def contains_yellow(self, img_np):
        yellow_min = np.array([210, 105, 30], np.uint8)
        yellow_max = np.array([235, 150, 55], np.uint8)
        yellow_mask = cv2.inRange(img_np, yellow_min, yellow_max)
        return np.any(yellow_mask)

    def autoClickInOperationArea(self):
        x = self.operationArea.x() + self.operationArea.width() // 2
        y = self.operationArea.y() + self.operationArea.height() // 2
        pyautogui.mouseDown(x, y, button='left')
        time.sleep(0.001)
        pyautogui.mouseUp(x, y, button='left')

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    halo = HaloWidget()
    halo.show()
    sys.exit(app.exec_())