import time
import argparse
import numpy as np
import pandas as pd
try:
    import pytrigno
except ImportError:
    import sys
    sys.path.insert(0, '..')
    import pytrigno

def record_emg(host):
    channel=6
    dev_emg = pytrigno.TrignoEMG(channel_range=(0,channel-1), samples_per_read=60000,
                        host=host)
    dev_emg.start()
    time_emg_begin = time.time()
    print('肌电开始时间：',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_emg_begin)))
    data_EMG = dev_emg.read()
    for i in range(3):
        data_EMG += dev_emg.read()
        assert data_EMG.shape == (channel, dev_emg.samples_per_read)#40*second
    time_emg_end = time.time()
    time_end_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_emg_end))
    print('肌电结束时间：', time_end_string)
    data_emg_timestamp = np.linspace(int(time_emg_begin*1000), int(time_emg_end*1000)+dev_emg.samples_per_read/2000-1, dev_emg.samples_per_read)  #构建时间戳
    time_end_string = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time_emg_end))
    data_EMG = np.vstack((data_emg_timestamp, data_EMG))
    data_EMG = pd.DataFrame(data_EMG, columns=None)
    data_EMG = data_EMG.T
    data_EMG.to_csv('./NData/emg/EMG'+str(int(time_emg_begin*1000))+'.csv', index=None)
    dev_emg.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '-a', '--addr',
        dest='host',
        # default='192.168.56.1',
        default='127.0.0.1',
        help="IP address of the machine running TCU. Default is localhost.")
    args = parser.parse_args()
    print(args.host)
    record_emg(args.host)

