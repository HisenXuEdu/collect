"""
*点镇定阻抗控制展示
*运动过程阻抗控制展示
"""

import sys
from util.dobot_api import DobotApiDashboard, DobotApi, DobotApiMove, MyType, alarmAlarmJsonFile
from time import sleep
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from ic.ic import IC
from ic.force import Force
import threading
from visdom import Visdom
from util.plot import Plot
from util.util import *
import os
import multiprocessing
import feedback
import random

def connect_robot():
    try:
        ip = "192.168.5.1"
        dashboardPort = 29999
        movePort = 30003
        # print("正在建立连接...")
        dashboard = DobotApiDashboard(ip, dashboardPort)
        move = DobotApiMove(ip, movePort)
        # print(">.<move连接成功>!<")
        return dashboard, move
    except Exception as e:
        print(":(move连接失败:(")
        raise e


def plot_viz():
    global force_,pose,euler,initial_pose
    sleep(2)
    plt_force=Plot(200,'FORCE')
    plt_pose=Plot(200,'POSE')

    while True:
        plt_force.plot(force_)
        plt_pose.plot(pose*1000-initial_pose[:3])


def generate_move(ic,step):
    while(True):
        ic.move_single([initial_pose[0]/1000+(random.random()-0.5)/20,initial_pose[1]/1000+(random.random()-0.5)/20,initial_pose[2]/1000])
        print(ic.desired_pose_position_[0],ic.desired_pose_position_[1],ic.desired_pose_position_[2])
        ic.change_para(d=[80, 80, 80, 12, 12, 12], k=[500, 500, 500, 5, 5, 5])
        sleep(3)


def trigno_open():
    os.system('python ./emg/emg_record.py')


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
        

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_label)  # 绑定定时器的 timeout 信号到自定义的槽函数 update_label
        self.timer.start(100)  # 以毫秒为单位设置定时器的间隔（1秒 = 1000毫秒）

    def update_label(self):
        global pose,initial_pose
        x_factor=(pose[0]*1000-initial_pose[0])/0.5
        y_factor=-(pose[1]*1000-initial_pose[1])/0.5
        print(x_factor,y_factor)
        if(abs(x_factor)>18 or abs(y_factor)>18):
            self.image_label.setStyleSheet("background-color: red;border-radius: 15px")
        else:
            self.image_label.setStyleSheet("background-color: green;border-radius: 15px")
        self.image_position = (200+x_factor, 200+y_factor)
        self.image_label.move(*self.image_position)

def feedback():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

def qtthread():
    feedback()


if __name__ == '__main__':

    start = time.time()
    print('开始时间：', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start)))

    # p1 = multiprocessing.Process(target=trigno_open)
    # # 启动子进程
    # p1.start()
    # time.sleep(3)


    dashboard, move = connect_robot()
    dashboard.EnableRobot()
    dashboard.ClearError()
    dashboard.SetSafeSkin(0)
    dashboard.SetCollisionLevel(0)
    dashboard.SpeedFactor(30)


    force=Force()

    force_thread = threading.Thread(target=force.get_force)
    force_thread.daemon = True
    force_thread.start()


    initial_pose = [138.360397,-472.066620,407.361847,-179.488663,0.264109,179.605057]
    pose = [138.360397,-472.066620,407.361847,-179.488663,0.264109,179.605057]
    initial_joint = [90.0, 0.0, 100.0, -10.0, -90.0, 0.0]
    print(initial_pose)
    move.MovL(initial_pose[0],initial_pose[1],initial_pose[2],initial_pose[3],initial_pose[4],initial_pose[5])
    move.Sync()

    feedback_thread = threading.Thread(target=qtthread)
    feedback_thread.daemon = True
    feedback_thread.start()

    ic = IC(initial_pose=[initial_pose[0] / 1000, initial_pose[1] / 1000, initial_pose[2] / 1000, initial_pose[3], initial_pose[4], initial_pose[5]])

    tra = threading.Thread(target=generate_move,args=(ic,0.01))
    tra.daemon = True
    tra.start()

    while True:
        start_time = time.time()
        # wrench_external_ = [force[1]/10,-force[2]/3,-force[0]/10,force[4]*10,-force[5]*10,-force[3]*10]
        force_ = [-force.force[1],-force.force[0],-force.force[2],force.force[4]*10,force.force[3]*10,-force.force[5]*10]  #这里将z轴的力设置为旋转轴的力，因为z轴受力没法传给六维力传感器。
        pose, euler = ic.compute_admittance(force_)
        # print(pose[0]*1000,pose[1]*1000,pose[2]*1000,initial_pose[3],initial_pose[4],initial_pose[5])
        move.ServoP(pose[0]*1000,pose[1]*1000,pose[2]*1000,initial_pose[3],initial_pose[4],initial_pose[5])
        while time.time() - start_time < 0.016:
            pass