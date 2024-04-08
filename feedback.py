import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QSlider
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
import threading
from time import sleep


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Keyboard Movement")
        self.setGeometry(100, 100, 500, 500)

        self.origin_label = QLabel(self)
        self.origin_label.setGeometry(190, 190, 120, 120)
        self.origin_position = (190, 190)  # 初始位置
        self.origin_label.setStyleSheet("background-color:blue;border-radius: 15px")
        self.origin_label.move(*self.origin_position)

        self.image_label = QLabel(self)
        self.image_label.setGeometry(50, 50, 100, 100)
        # self.image_label.setPixmap(QPixmap('circle.png').scaled(self.image_label.size())) 
        self.image_label.setStyleSheet("background-color: green;border-radius: 15px")
        self.image_position = (200, 200)  # 初始位置

        self.slider = QSlider(Qt.Vertical)
        self.slider.setValue(50)
        self.slider.resize(200, 28)
        self.slider.move(50, 61)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_label)  # 绑定定时器的 timeout 信号到自定义的槽函数 update_label
        self.timer.start(100)  # 以毫秒为单位设置定时器的间隔（1秒 = 1000毫秒）

    def update_label(self):
        # global pose,initial_pose
        # x_factor=(pose[0]*1000-initial_pose[0])/10
        # y_factor=(pose[1]*1000-initial_pose[1])/10
        self.image_position = (self.image_position[0], self.image_position[1])
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())