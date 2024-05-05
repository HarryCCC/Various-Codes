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
        self.current_color = QtGui.QColor(255, 0, 0, 120)
        self.last_color = None
        self.initUI()
        self.dragPosition = None
        self.operationArea = QtCore.QRect(250, 400, 100, 100)
        self.captureArea = QtCore.QRect(400, 400, 100, 100)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateColor)
        self.timer.start(1) # 修改定时器的间隔
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
        qp.setPen(QtGui.QPen(self.current_color, 10))
        qp.drawRect(self.captureArea)
        qp.drawText(self.captureArea, QtCore.Qt.AlignCenter, "识别区")

        if not self.isRunning:  # Only draw the operation area if not running
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
            if self.captureArea.contains(event.pos()):
                self.dragPosition = event.globalPos() - self.captureArea.topLeft()
                event.accept()
            elif self.operationArea.contains(event.pos()):
                self.dragPosition = event.globalPos() - self.operationArea.topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton and self.dragPosition is not None:
            new_pos = event.globalPos() - self.dragPosition
            if self.operationArea.contains(event.pos()) and not self.isRunning:
                self.operationArea.moveTopLeft(new_pos)
            elif self.captureArea.contains(event.pos()):
                self.captureArea.moveTopLeft(new_pos)
            self.update()
            event.accept()

    def updateColor(self):
        if not self.isRunning:
            return
        x, y = self.captureArea.x(), self.captureArea.y()
        img = ImageGrab.grab(bbox=(x, y, x + self.captureArea.width(), y + self.captureArea.height()))
        img_np = np.array(img)
        self.last_color = self.current_color
        if not self.contains_yellow(img_np):
            self.current_color = QtGui.QColor(0, 255, 0, 120)  # Green when no yellow is detected
            if self.last_color != self.current_color:
                self.autoClickInOperationArea()
        else:
            self.current_color = QtGui.QColor(255, 0, 0, 120)  # Red otherwise
        self.update()

    def contains_yellow(self, img_np):
        yellow_min = np.array([200, 100, 0], np.uint8)
        yellow_max = np.array([255, 255, 100], np.uint8)
        yellow_mask = cv2.inRange(img_np, yellow_min, yellow_max)
        return np.any(yellow_mask)

    def autoClickInOperationArea(self):
        x = self.operationArea.x() + self.operationArea.width() // 2
        y = self.operationArea.y() + self.operationArea.height() // 2
        pyautogui.mouseDown(x, y, button='left')
        time.sleep(0.01)  # Customize this duration to match the required click duration
        pyautogui.mouseUp(x, y, button='left')

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    halo = HaloWidget()
    halo.show()
    sys.exit(app.exec_())
