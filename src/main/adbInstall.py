import time
import os
import subprocess

# 配置你的ADB路径和APK文件夹路径
app_path = "C:/Users/eureka/Downloads/settings_apk-debug.apk"
app_path2 = "C:/Users/eureka/Downloads/ruijiecloud-8.1.6_2407090929.apk"
# app_path3 = "C:/Users/eureka/Downloads/enet-8.1.7-02-931-g12c5e54-2407082007_2407082007.apk"
# app_path3 = "C:/Users/eureka/Downloads/enet-8.1.6_2407060837.apk"
app_path3 = "C:/Users/eureka/Downloads/enet-8.1.6_2407090929.apk"

adb_path = "D:/adb_latest/platform-tools/adb.exe"

def install_apk(apk_path):
    try:
        result = subprocess.run([adb_path, "install", apk_path], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Successfully installed {apk_path}")
        else:
            print(f"Failed to install {apk_path}: {result.stderr}")
    except Exception as e:
        print(f"An error occurred while installing {apk_path}: {str(e)}")


def main():
    apk = [app_path, app_path2, app_path3]
    for i in apk:
        install_apk(i)
if __name__ == "__main__":
    main()
