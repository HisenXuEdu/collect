import os
import time
import multiprocessing

def trigno_open():
    os.system('python ./emg/emg_record.py')

def force_open():
    os.system('python ./force/force_record.py')

def cr5_open():
    os.system('python ./cr5/move_mode.py')

if __name__ == "__main__":
    start = time.time()
    print('开始时间：', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start)))

    p1 = multiprocessing.Process(target=trigno_open)
    p2 = multiprocessing.Process(target=force_open)
    p3 = multiprocessing.Process(target=cr5_open)

    # 启动子进程
    p1.start()
    time.sleep(3)
    p2.start()
    time.sleep(2)
    p3.start()

    #等待程序执行完成
    p1.join()
    p2.join()
    p3.join()
    end = time.time()
    print('结束时间：', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end)))