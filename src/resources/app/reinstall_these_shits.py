import os
import sys

def reinstall_these_shits():
    pkg_name1 = 'io.appium.uiautomator2.server'
    pkg_name2 = 'io.appium.uiautomator2.server.test'
    pkg_name3 = 'io.appium.settings'
    pkg1_path = 'D:/pyproj/st/src/resources/app/appium-uiautomator2-server-v7.0.19.apk'
    pkg2_path = 'D:/pyproj/st/src/resources/app/appium-uiautomator2-server-debug-androidTest.apk'
    pkg3_path = 'D:/pyproj/st/src/resources/app/settings_apk-debug.apk'
    os.system(f'adb uninstall {pkg_name1}')
    os.system(f'adb uninstall {pkg_name2}')
    os.system(f'adb uninstall {pkg_name3}')
    os.system(f'adb install -r {pkg1_path}')
    os.system(f'adb install -r {pkg2_path}')
    os.system(f'adb install -r {pkg3_path}')

def grant_permissions(package_name):
    os.system(f'adb shell pm grant {package_name} android.permission.RECEIVE_BOOT_COMPLETED')
    os.system(f'adb shell pm grant {package_name} android.permission.GET_TASKS')
    os.system(f'adb shell pm grant {package_name} android.permission.REORDER_TASKS')
    os.system(f'adb shell pm grant {package_name} android.permission.PACKAGE_USAGE_STATS')
    os.system(f'adb shell pm grant {package_name} android.permission.SYSTEM_ALERT_WINDOW')
    

if __name__ == '__main__':
    reinstall_these_shits()
    # pkg_name1 = 'io.appium.uiautomator2.server'
    # pkg_name2 = 'io.appium.uiautomator2.server.test'
    # pkg_name3 = 'io.appium.settings'