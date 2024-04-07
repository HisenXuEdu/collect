import time
import argparse
import numpy as np
import pandas as pd
import time
try:
    import pytrigno
except ImportError:
    import sys
    sys.path.insert(0, '..')
    import pytrigno

from pynput import keyboard

def record_emg(host):
    channel=1
    dev_emg = pytrigno.TrignoEMG(channel_range=(0,channel-1), samples_per_read=500,
                        host=host)
    dev_emg.start()
    time_emg_begin = time.time()
    print('肌电开始时间：',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_emg_begin)))
    while(1):
        if stop_threads == 1:
            break
        data_EMG = dev_emg.read()
        data_EMG = np.abs(data_EMG)
        data_EMG = np.mean(data_EMG)
        print(data_EMG)
        time.sleep(0.1)

# 键盘按下执行的函数 使用try和except的原因是有特殊按键（功能键）
def keyboard_on_press(key):
    global stop_threads
    try:
        print('字母键{0} press'.format(key.char))
    except AttributeError:
        print('特殊键{0} press'.format(key))
        if key == keyboard.Key.esc:
            stop_threads = True
            return False


if __name__ == '__main__':

    stop_threads = False

    listener = keyboard.Listener(on_press=keyboard_on_press)
    listener.daemon = 1
    listener.start()

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

