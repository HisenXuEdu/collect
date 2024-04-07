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
    move.RelMovJUser(0,0,-100,0,0,0,0)

    sec = 30


    p1 = multiprocessing.Process(target=pose_open)
    p1.start()
    time.sleep(3)

    t_start = time.time()
    t_start_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t_start))
    print("运动开始时间：", t_start_string)
    t_end = time.time() + sec
    dashboard.SpeedFactor(20)

    move.RelMovJUser(0,0,-60,0,0,0,0)
    sleep(3)


    
    while time.time() < t_end:
        x = (random.random()-0.5)*20
        y = (random.random()-0.5)*20
        move.RelMovJUser(x,y,0,0,0,0,0)
        sleep(0.4)
        move.RelMovJUser(-x,-y,0,0,0,0,0)
        sleep(0.4)
        


    t_end = time.time()
    t_end_string = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime(t_end))
    print("运动结束时间：", t_end_string)

    dashboard.close()
    move.close()

    
    p1.join()