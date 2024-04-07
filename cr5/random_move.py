import threading
from dobot_api import DobotApiDashboard, DobotApi, DobotApiMove, MyType, alarmAlarmJsonFile
from time import sleep
import time
import numpy as np
import re
import random
import pandas as pd
import datetime


# 全局变量(当前坐标)
current_actual = None
algorithm_queue = None
enableStatus_robot = None
robotErrorState = False
globalLockValue = threading.Lock()
timestamp_list = []
pose_list = []
first_feed = True
first_time = 0
timestamp = 0

sec = 3

def ConnectRobot():
    try:
        ip = "192.168.5.1"
        dashboardPort = 29999
        movePort = 30003
        feedPort = 30004
        print("正在建立连接...")
        dashboard = DobotApiDashboard(ip, dashboardPort)
        move = DobotApiMove(ip, movePort)
        feed = DobotApi(ip, feedPort)
        print(">.<连接成功>!<")
        return dashboard, move, feed
    except Exception as e:
        print(":(连接失败:(")
        raise e

def RunPoint(move: DobotApiMove, point_list: list):
    move.MovL(point_list[0], point_list[1], point_list[2], point_list[3], point_list[4], point_list[5])

def GetFeed(feed: DobotApi):
    global current_actual
    global algorithm_queue
    global enableStatus_robot
    global robotErrorState
    global timestamp_list
    global first_feed
    global sec
    global timestamp
    global first_time
    hasRead = 0
    while timestamp - first_time < 3000:
        data = bytes()
        while hasRead < 1440:
            temp = feed.socket_dobot.recv(1440 - hasRead)
            if len(temp) > 0:
                hasRead += len(temp)
                data += temp
        hasRead = 0
        feedInfo = np.frombuffer(data, dtype=MyType)
        if hex((feedInfo['test_value'][0])) == '0x123456789abcdef':
            # Refresh Properties
            globalLockValue.acquire()
            current_actual = feedInfo["tool_vector_actual"][0]
            algorithm_queue = feedInfo['run_queued_cmd'][0]
            enableStatus_robot=feedInfo['enable_status'][0]
            robotErrorState= feedInfo['error_status'][0]
            timestamp = feedInfo['time_stamp'][0]
            pose = feedInfo['tool_vector_actual'][0]
            print(timestamp - first_time)
            if first_feed:
                first_feed = False
                t_start = time.time()
                print(int(t_start*1000))
                first_time = timestamp
                print("first_time",first_time)
            timestamp_list.append(timestamp)
            pose_list.append(pose)
            globalLockValue.release()
        sleep(0.001)

def WaitArrive(point_list):
    while True:
        is_arrive = True
        globalLockValue.acquire()
        if current_actual is not None:
            for index in range(4):
                if (abs(current_actual[index] - point_list[index]) > 1):
                    is_arrive = False
            if is_arrive :
                globalLockValue.release()
                return
        globalLockValue.release()
        sleep(0.001)

def ClearRobotError(dashboard: DobotApiDashboard):
    global robotErrorState
    dataController,dataServo =alarmAlarmJsonFile()    # 读取控制器和伺服告警码
    while True:
      globalLockValue.acquire()
      if robotErrorState:
                numbers = re.findall(r'-?\d+', dashboard.GetErrorID())
                numbers= [int(num) for num in numbers]
                if (numbers[0] == 0):
                  if (len(numbers)>1):
                    for i in numbers[1:]:
                      alarmState=False
                      if i==-2:
                          print("机器告警 机器碰撞 ",i)
                          alarmState=True
                      if alarmState:
                          continue                
                      for item in dataController:
                        if  i==item["id"]:
                            print("机器告警 Controller errorid",i,item["zh_CN"]["description"])
                            alarmState=True
                            break 
                      if alarmState:
                          continue
                      for item in dataServo:
                        if  i==item["id"]:
                            print("机器告警 Servo errorid",i,item["zh_CN"]["description"])
                            break  
                       
                    choose = input("输入1, 将清除错误, 机器继续运行: ")     
                    if  int(choose)==1:
                        dashboard.ClearError()
                        sleep(0.01)
                        dashboard.Continue()

      else:  
         if int(enableStatus_robot)==1 and int(algorithm_queue)==0:
            dashboard.Continue()
      globalLockValue.release()
      sleep(5)
       
if __name__ == '__main__':
    dashboard, move, feed = ConnectRobot()
    print("开始使能...")
    dashboard.EnableRobot()
    print("完成使能:)")
    feed_thread = threading.Thread(target=GetFeed, args=(feed,))
    feed_thread.daemon = True
    feed_thread.start()
    feed_thread1 = threading.Thread(target=ClearRobotError, args=(dashboard,))
    feed_thread1.daemon = True
    feed_thread1.start()
    print("循环执行...")
    # point_a = [-19, -478, 154, -159,10,20]
    # point_b = [160, 260, -30, 170,10,10]
    # initial_angle = dashboard.GetAngle()
    # print(initial_angle)
    initial_angle = [90,0,90,0,-90,0]
    move.JointMovJ(90,0,90,0,-90,0)
    # # while True:
    # #     move.RelJointMovJ(10,0,0,0,0,20)
    # #     sleep(0.5)
    # #     move.RelJointMovJ(-10,0,0,0,0,-20)
    # #     sleep(0.5)

    cur_target = initial_angle.copy()

    dtime = datetime.datetime.now()
    print(dtime)
    ans_time = time.mktime(dtime.timetuple())
    t_start = time.time()
    t_end = time.time() + sec
    print(int(t_start*1000))
    


    while time.time() < t_end:
        cur_target[0] = initial_angle[0] + (random.random()-0.5)*2   #随机加入-1到+1度的角度
        cur_target[1] = initial_angle[1] + (random.random()-0.5)*2
        cur_target[2] = initial_angle[2] #+ random.random()/50
        cur_target[3] = initial_angle[3] #+ random.random()/50
        cur_target[4] = initial_angle[4] #+ random.random()/50
        cur_target[5] = initial_angle[5] #+ random.random()/50
        print(cur_target[0],cur_target[1])
        move.JointMovJ(cur_target[0],cur_target[1],cur_target[2],cur_target[3],cur_target[4],cur_target[5])
        sleep(0.3)

    feed_thread.join()
    
    data = pd.DataFrame(pose_list, columns=None)
    data['time'] = pd.DataFrame(timestamp_list)
    data.to_csv('./Data/pose/POSE'+ str(int(t_start*1000)) + '.csv', index=None)


    # move.RelJointMovJ(10,0,0,0,0,20)
    # move.MovL(point_list[0], point_list[1], point_list[2], point_list[3], point_list[4], point_list[5])
    # while True:   
    #     RunPoint(move, point_a)
    #     WaitArrive(point_a)
    #     RunPoint(move, point_b)
    #     WaitArrive(point_b)
