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
    ic.move_single([ic.desired_pose_position_[0]+(random.random()-0.5)*10,ic.desired_pose_position_[1]+(random.random()-0.5)*10,ic.desired_pose_position_[2]])
    sleep(3)


def trigno_open():
    os.system('python ./emg/emg_record.py')

def qtthread():
    feedback()


if __name__ == '__main__':

    start = time.time()
    print('开始时间：', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start)))

    p1 = multiprocessing.Process(target=trigno_open)
    # 启动子进程
    p1.start()
    time.sleep(3)


    """
    moving:是否让机械臂运动
    euler:是否在旋转角度开启阻抗控制
    plot:是否将运动和力用visdom打印
    """
    moving = False
    euler = False
    plot = True

    args = sys.argv[1:]
    if len(args) == 1:
        moving = str2bool(args[0])
    elif len(args) == 2:
        moving = str2bool(args[0])
        euler = str2bool(args[1])
    elif len(args) == 3:
        moving = str2bool(args[0])
        euler = str2bool(args[1])
        plot = str2bool(args[2])


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

    feedback_thread = threading.Thread(target=qtthread)
    feedback_thread.daemon = True
    feedback_thread.start()

    initial_pose = [138.360397,-472.066620,407.361847,-179.488663,0.264109,179.605057]
    initial_joint = [90.0, 0.0, 100.0, -10.0, -90.0, 0.0]
    print(initial_pose)
    move.MovL(initial_pose[0],initial_pose[1],initial_pose[2],initial_pose[3],initial_pose[4],initial_pose[5])
    move.Sync()

    ic = IC(initial_pose=[initial_pose[0] / 1000, initial_pose[1] / 1000, initial_pose[2] / 1000, initial_pose[3], initial_pose[4], initial_pose[5]])

    if plot:
        record = threading.Thread(target=plot_viz)
        record.daemon = True
        record.start()

    if moving:
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