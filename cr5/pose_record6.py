from dobot_api import DobotApiDashboard, DobotApi, DobotApiMove, MyType, alarmAlarmJsonFile,type6
import numpy as np
import time
import pandas as pd



def ConnectRobot():
    try:
        ip = "192.168.5.1"
        feedPort = 30006
        # print("正在建立连接...")
        feed = DobotApi(ip, feedPort)
        # print(">.<pose_record连接成功>!<")
        return feed
    except Exception as e:
        print(":(pose_record连接失败:(")
        raise e
    

if __name__ == '__main__':
    feed = ConnectRobot()
    timestamp_list = []
    pose_list = []
    hasRead = 0
    timestamp = 0
    first_time = 0
    first_feed = True


    t_start = time.time()
    t_start_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t_start))
    print("位置开始时间：", t_start_string)

    while timestamp - first_time < 6000:
        data = bytes()
        while hasRead < 64:
            temp = feed.socket_dobot.recv(64 - hasRead)
            if len(temp) > 0:
                hasRead += len(temp)
                data += temp
        hasRead = 0
        feedInfo = np.frombuffer(data, dtype=type6)


        if hex((feedInfo['test_value'][0])) == '0x123456789abcdef':
            timestamp = feedInfo['time_stamp'][0]
            pose = feedInfo['tool_vector_actual'][0]
            if first_feed:
                first_feed = False
                t_start = time.time()
                t_start_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t_start))
                # print(t_start_string)
                print(int(t_start*1000))
                first_time = timestamp
                # t_robot = first_time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t_start))
                # print(t_robot)
            timestamp_list.append(timestamp)
            pose_list.append(pose)
        
    t_end = time.time()
    t_end_string = time.strftime("%Y-%m-%d%H:%M:%S", time.localtime(t_end))
    print("位置结束时间：", t_end_string)

    data = pd.DataFrame(pose_list, columns=None)
    data['time'] = pd.DataFrame(timestamp_list)

    data.to_csv('./Data/pose/POSE'+ str(int(t_start*1000)) +'.csv', index=None)
