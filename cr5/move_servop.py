import threading
from dobot_api import DobotApiDashboard, DobotApi, DobotApiMove, MyType, alarmAlarmJsonFile
from time import sleep
import time
import numpy as np
import re
import random
import pandas as pd
import datetime
import multiprocessing
import os



def ConnectRobot():
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
    
def pose_open():
    os.system('python ./cr5/pose_record.py')


if __name__ == '__main__':
    dashboard, move = ConnectRobot()
    dashboard.EnableRobot()

    initial_angle = [90,0,90,0,-90,0]
    move.JointMovJ(90,0,90,0,-90,0)
    # initial_pose = [138.360397,-472.066620,407.361847,179.488663,0.264109,179.605057]
    # initial_pose = dashboard.GetPose()
    # initial_pose
    # print(initial_pose)
    initial_pose = [138.207748,-473.024475,410.285980,179.924133,0.315713,179.610504]
    move.MovL(138.207748,-473.024475,410.285980,179.924133,0.315713,179.610504)

    sec = 30

    # cur_target = initial_angle.copy()


    p1 = multiprocessing.Process(target=pose_open)
    p1.start()
    time.sleep(3)

    t_start = time.time()
    t_start_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t_start))
    print("运动开始时间：", t_start_string)

    sleep(10)

    t_end = time.time() + sec
    # print(int(t_start*1000))
    dashboard.SpeedFactor(20)
    
    


    
    while time.time() < t_end:
        x = (random.random()-0.5)*20
        y = (random.random()-0.5)*20
        move.ServoP(138.207748+x,-473.024475+y,410.285980,179.924133,0.315713,179.610504)
        sleep(0.01)
        move.ServoP(138.207748-x,-473.024475-y,410.285980,179.924133,0.315713,179.610504)
        sleep(0.01)
        


    t_end = time.time()
    t_end_string = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime(t_end))
    print("运动结束时间：", t_end_string)

    dashboard.close()
    move.close()

    
    p1.join()