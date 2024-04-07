import time
import socket
import struct
import numpy as np
import pandas as pd
import xlsxwriter as xw


PORT = 49152  # Ethernet DAQ使用的端口号
SAMPLE_COUNT = 100000  # 10个输入样本
SPEED = 10  # 1000 / SPEED = 频率（单位：赫兹）;  //0-255，频率通过 1000/num 计算
FILTER = 4  # 0 = 无滤波; 1 = 500赫兹; 2 = 150赫兹; 3 = 50赫兹; 4 = 15赫兹; 5 = 5赫兹; 6 = 1.5赫兹
BIASING_ON = 0xFF  # 开启偏置
BIASING_OFF = 0x00  # 关闭偏置


COMMAND_START = 0x0002  # Command for start streaming
COMMAND_STOP = 0x0000  # Command for stop streaming
COMMAND_BIAS = 0x0042  # Command for toggle biasing
COMMAND_FILTER = 0x0081  # Command for setting filter
COMMAND_SPEED = 0x0082  # Command for setting speed


def connect():
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.connect(('192.168.2.3',49152))
    send_command(s, COMMAND_SPEED, SPEED)
    send_command(s, COMMAND_FILTER, FILTER)
    send_command(s, COMMAND_BIAS, BIASING_ON)
    send_command(s, COMMAND_START, SAMPLE_COUNT)
    return s

# def send_command(s, command, data):
#     # Prepare the request data  
#     request = bytearray(8)  
#     request[0:2] = htons(0x1234)  
#     request[2:4] = htons(command) # Replace 'command' with your command value  
#     request[4:8] = htonl(data) # Replace 'data' with your data value  
    
#     # Send the request to the server  
#     s.sendall(request)  
    
#     # Wait for a while to make sure that the command has been processed by Ethernet DAQ  
#     time.sleep(5)

def send_command(sock, command, data):
    request = bytearray(8)
    struct.pack_into('!H', request, 0, 0x1234)
    struct.pack_into('!H', request, 2, command)
    struct.pack_into('!L', request, 4, data)
    sock.send(request)
    time.sleep(0.005)  # Wait a little, assuming the command has been processed by the Ethernet DAQ

def xw_toExcel(worksheet1, data, row):  # xlsxwriter库储存数据到excel
    i = row  # 从第二行开始写入数据
    for j in range(len(data)):
        insertData = [data[j][0], data[j][1], data[j][2], data[j][3], data[j][4], data[j][5], data[j][6], data[j][7], data[j][8]]
        row = 'A' + str(i)
        worksheet1.write_row(row, insertData)
        i += 1



#处理数据
def parse_data(inBuffer):
    FORCE_DIV = 10000.0 
    cur = list(range(9))
    cur[0] = struct.unpack('>I', inBuffer[:4])[0]
    cur[1] = struct.unpack('I', inBuffer[4:8])[0]
    cur[2] = struct.unpack('I', inBuffer[8:12])[0]
    uItems = 0
    cur[3] = struct.unpack('>i', inBuffer[12 + (uItems * 4):16 + (uItems * 4)])[0]/FORCE_DIV
    uItems += 1
    cur[4] = struct.unpack('>i', inBuffer[12 + (uItems * 4):16 + (uItems * 4)])[0]/FORCE_DIV
    uItems += 1
    cur[5] = struct.unpack('>i', inBuffer[12 + (uItems * 4):16 + (uItems * 4)])[0]/FORCE_DIV
    uItems += 1
    cur[6] = struct.unpack('>i', inBuffer[12 + (uItems * 4):16 + (uItems * 4)])[0]/FORCE_DIV
    uItems += 1
    cur[7] = struct.unpack('>i', inBuffer[12 + (uItems * 4):16 + (uItems * 4)])[0]/FORCE_DIV
    uItems += 1
    cur[8] = struct.unpack('>i', inBuffer[12 + (uItems * 4):16 + (uItems * 4)])[0]/FORCE_DIV
    return cur



s = connect()

# row = 2
# workbook = xw.Workbook("test.xlsx")  # 创建工作簿
# worksheet1 = workbook.add_worksheet("sheet1")  # 创建子表
# worksheet1.activate()  # 激活表
# title = ['sampleCounter', 'sequenceNumber', 'status', 'fx', 'fy', 'fz', 'tx', 'ty', 'tz']  # 设置表头
# worksheet1.write_row('A1', title)  # 从A1单元格开始写入表头

data = []
time_force_begin = time.time()
print('六维力开始时间：',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_force_begin)))
# while True:
sec = 60
for i in range(int(1000/SPEED)*sec):
    if i==1:
        time_force_begin = time.time()
    # print(i)
    # 接收 36 个字节的数据
    inBuffer = s.recv(36)
    data.append(parse_data(inBuffer))

time_force_end = time.time()
time_end_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_force_end))
print('六维力结束时间：', time_end_string)
data_force_timestamp = np.linspace(int(time_force_begin*1000), int(time_force_begin*1000)+sec*1000-1, int(1000/SPEED)*sec)  #构建时间戳
time_end_string = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time_force_end))
# data = np.array(data)
data = pd.DataFrame(data, columns=None)
data['time'] = pd.DataFrame(data_force_timestamp)
print(data.shape)

# data_EMG = np.vstack((data_emg_acc_timestamp, data))
# data_EMG = pd.DataFrame(data_EMG, columns=None)
data.to_csv('./NData/force/FORCE'+str(int(time_force_begin*1000))+'.csv', index=None)
# data.to_csv('1'+'.csv', index=None)


# xw_toExcel(worksheet1, data, row)
# workbook.close()  # 关闭表