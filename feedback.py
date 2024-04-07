import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
import threading
from time import sleep


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Keyboard Movement")
        self.setGeometry(100, 100, 400, 400)

        self.image_label = QLabel(self)
        self.image_label.setGeometry(50, 50, 100, 100)
        self.image_label.setPixmap(QPixmap('circle.png').scaled(self.image_label.size())) 
        #self.image_label.setStyleSheet("background-color: red")

        self.image_position = (50, 50)  # 初始位置

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_label)  # 绑定定时器的 timeout 信号到自定义的槽函数 update_label
        self.timer.start(1000)  # 以毫秒为单位设置定时器的间隔（1秒 = 1000毫秒）

    def update_label(self):
        self.image_position = (self.image_position[0] - 10, self.image_position[1])
        self.image_label.move(*self.image_position)



    # def keyPressEvent(self, event):
    #     step = 10  # 每次移动的步长
    #     key = event.key()

    #     if key == Qt.Key_Left:
    #         self.image_position = (self.image_position[0] - step, self.image_position[1])
    #     elif key == Qt.Key_Right:
    #         self.image_position = (self.image_position[0] + step, self.image_position[1])
    #     elif key == Qt.Key_Up:
    #         self.image_position = (self.image_position[0], self.image_position[1] - step)
    #     elif key == Qt.Key_Down:
    #         self.image_position = (self.image_position[0], self.image_position[1] + step)

    #     self.image_label.move(*self.image_position)

    #     event.accept()


def feedback():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())