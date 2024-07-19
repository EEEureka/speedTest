import os
import sys
import time


def get_uix():
    #在手机上创建目录/tmp
    os.system('adb shell mkdir /sdcard/tmp')
    # 执行adb shell uiautomator dump /tmp/tmp1.uix
    os.system('adb shell uiautomator dump /sdcard/tmp/tmp1.uix')
    # 将uix文件adb pull 到/uixs/目录下
    os.system('adb pull /sdcard/tmp/tmp1.uix src/main/tools/uixs/temp1.uix')

def get_png():
    # 在手机上创建目录/tmp
    os.system('adb shell mkdir /sdcard/tmp')
    # 执行adb shell screencap -p /tmp/tmp1.png
    os.system('adb shell screencap -p /sdcard/tmp/tmp1.png')
    # 将png文件adb pull 到/pngs/目录下
    os.system('adb pull /sdcard/tmp/tmp1.png src/main/tools/pngs/temp1.png')

def get_uv():
    get_uix()
    get_png()

if __name__ == '__main__':
    get_uv()
    print('get uv success')