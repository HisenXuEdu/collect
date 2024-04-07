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
    # print("开始使能...")
    # dashboard.EnableRobot()
    # print("完成使能:)")
    # feed_thread = threading.Thread(target=GetFeed, args=(feed,))
    # feed_thread.daemon = True
    # feed_thread.start()
    # feed_thread1 = threading.Thread(target=ClearRobotError, args=(dashboard,))
    # feed_thread1.daemon = True
    # feed_thread1.start()
    # print("循环执行...")
    dashboard.EnableRobot()

    # initial_angle = dashboard.GetAngle()
    # print(initial_angle)
    initial_angle = [90,0,90,0,-90,0]
    move.JointMovJ(90,0,90,0,-90,0)

    sec = 3

    cur_target = initial_angle.copy()

    # dtime = datetime.datetime.now()
    # print(dtime)
    # ans_time = time.mktime(dtime.timetuple())


    p1 = multiprocessing.Process(target=pose_open)
    p1.start()
    time.sleep(2)

    t_start = time.time()
    t_start_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t_start))
    print("运动开始时间：", t_start_string)
    t_end = time.time() + sec
    # print(int(t_start*1000))


    while time.time() < t_end:
        cur_target[0] = initial_angle[0] + (random.random()-0.5)*5   #随机加入-1到+1度的角度
        cur_target[1] = initial_angle[1] + (random.random()-0.5)*5
        cur_target[2] = initial_angle[2] #+ random.random()/50
        cur_target[3] = initial_angle[3] #+ random.random()/50
        cur_target[4] = initial_angle[4] #+ random.random()/50
        cur_target[5] = initial_angle[5] #+ random.random()/50
        # print(cur_target[0],cur_target[1])
        move.JointMovJ(cur_target[0],cur_target[1],cur_target[2],cur_target[3],cur_target[4],cur_target[5])
        sleep(0.8)
    
    t_end = time.time()
    t_end_string = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime(t_end))
    print("运动结束时间：", t_end_string)
    
    p1.join()