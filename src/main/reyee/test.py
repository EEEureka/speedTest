import subprocess
import re

def get_device_info():
        try:
            # 获取设备型号
            model = subprocess.check_output(['adb', 'shell', 'getprop', 'ro.product.model']).decode('utf-8').strip()
            
            # 获取设备厂商
            manufacturer = subprocess.check_output(['adb', 'shell', 'getprop', 'ro.product.manufacturer']).decode('utf-8').strip()
            
            # 获取系统版本
            android_version = subprocess.check_output(['adb', 'shell', 'getprop', 'ro.build.version.release']).decode('utf-8').strip()
            
            # 获取设备名
            device_name = subprocess.check_output(['adb', 'shell', 'getprop', 'ro.product.device']).decode('utf-8').strip()
            
            # 获取设备品牌
            brand = subprocess.check_output(['adb', 'shell', 'getprop', 'ro.product.brand']).decode('utf-8').strip()
            
            return {
                "Model": model,
                "Manufacturer": manufacturer,
                "Android Version": android_version,
                "Device Name": device_name,
                "Brand": brand
            }
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while getting device info: {e}")
            return None
if __name__ == "__main__":
    # wifi_ssid = get_device_info()
    # print(wifi_ssid)
    element = '113.42Mbps'
    print(element.split('Mbps')[0])