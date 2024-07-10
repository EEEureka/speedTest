import threading
import re
import json
import subprocess
import requests
from loguru import logger
# 新建一个py文件，例如：mi_8se_testapp.py，将下面代码复制粘贴到py文件
import time

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
# appium 报错 需要安装 Appium-Python-Client；webdriver 报错需要安装 Appium Python Client: WebDriver module
#安装方式 在报错的提示地方点击 install


# For W3C actions
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.actions import interaction
# from selenium.webdriver.common.actions.action_builder import ActionBuilder
# from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# import heartrate

# heartrate.trace(browser=True)

class GlobalSpeedTestHandler:
    def __init__(self, packageName, platformVersion, port, api, webhook = '') -> None:
        self.packageName = packageName
        self.platformVersion = platformVersion
        self.port = port
        self.api = api
        self.larkWebhook = webhook
        self.driver = self.init_conn()

        

    def init_conn(self):
        caps = {
        "platformName": "Android",
        "appium:platformVersion": str(self.platformVersion),
        # "appium:appPackage": self.packageName,
        "appium:unicodeKeyboard": True,
        "appium:resetKeyboard": True,
        "appium:noReset": True,
        "appium:newCommandTimeout": 1000,
        "appium:automationName": "UiAutomator2",
        "appium:autoGrantPermissions": True,
        "appium:skipServerInstallation": True,
        "appium:skipDeviceInitialization": True,
        # "appium:appActivity": ".MainActivity",
        "appium:waitForIdleTimeout": 2,
        "appium:newCommandTimeout": 600,
        }
        driver = webdriver.Remote(f"http://localhost:{self.port}{self.api}", caps)
        return driver

    def get_device_info(self):
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

    def click_by_xpath(self, xpath, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((AppiumBy.XPATH, xpath))).click()
        except Exception as e:
            logger.error(f"An error occurred while clicking {xpath}: {str(e)}")
    
    def get_connected_wifi_ssid(self):
        try:
            # 执行 adb 命令以获取 WiFi 信息
            output = subprocess.check_output(['adb', 'shell', 'dumpsys', 'wifi'], encoding='utf-8')

            # 使用正则表达式提取 SSID
            ssid_match = re.search(r'SSID: ([^\s]+)', output)
            if ssid_match:
                ssid = ssid_match.group(1).replace('"', '').replace(',', '')
                return ssid
            else:
                print("No connected WiFi network found.")
                return None
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while getting WiFi info: {e}")
            return None

    def wait_for_element(self, elementXpath, timeout = 10):
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((AppiumBy.XPATH, elementXpath)))
        except Exception as e:
            logger.error(f"An error occurred while waiting for element {elementXpath}: {str(e)}")

    def check_element_exists(self, xpath):
        # 尝试查找元素
        elements = self.driver.find_elements(AppiumBy.XPATH, xpath)
        # 如果找到的元素列表不为空，则返回True，表示元素存在
        print(elements)
        return len(elements) > 0

    def find_elements_in_view_group(self, viewGroupXpath, timeout = 10):


        try:
            # 定位到ViewGroup
            view_group = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((AppiumBy.XPATH, viewGroupXpath))
            )
            # 获取ViewGroup中的所有元素
            elements_in_group = self.driver.find_elements(AppiumBy.XPATH, f"{viewGroupXpath}/descendant::*")
            # for i in elements_in_group:
            #     print(i.text)
            return elements_in_group
        except Exception as e:
            logger.error(f"An error occurred while finding elements in view group {viewGroupXpath}: {str(e)}")
            return []

    def find_element_by_xpath(self, xpath):
        return self.driver.find_element(AppiumBy.XPATH, xpath)

    def report_result_to_lark(self, tag, downrate, uprate, timestamp, formatted_time):
        # send post to self.larkWebhook to report the speed test result
        deviceInfo = self.get_device_info()
        data = {
            "code": 0,
            "msg": "SPD_TEST",
            "tag": tag,
            "data": {
                "downrate": downrate,
                "uprate": uprate,
                "timestamp": formatted_time,
                "Model": deviceInfo["Model"],
                "AndroidVersion": deviceInfo["Android Version"],
                "network": self.get_connected_wifi_ssid()
            }
        }
        # send post request
        session = requests.Session()
        session.headers.update({'Content-Type': 'application/json'})
        try:
            response = session.post(self.larkWebhook, data=json.dumps(data))
        except requests.exceptions.RequestException as e:
            input("pleace close the proxy and press enter to continue")
            response = session.post(self.larkWebhook, data=json.dumps(data))
        logger.info(f"result sent to lark, data:\n{json.dumps(data, indent=4)}")
        if response.status_code == 200:
            logger.info(f"response:\n{response.json()}")

    def start_speed_test(self):
        x_start_test = '//android.widget.Button[@resource-id="com.cnspeedtest.globalspeed:id/btn_star"]'
        self.click_by_xpath(x_start_test)
        flag_element = '//android.widget.TextView[@resource-id="com.cnspeedtest.globalspeed:id/ping_delay_value"]'
        while self.find_element_by_xpath(flag_element).text == '--':
            time.sleep(1)
        logger.info("start speed test successfully")
        return
    
    def speed_test_process(self):
        # get timestamp
        timestamp = time.time()
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
        
        # start speed test
        self.start_speed_test()
        flag_element = '//android.widget.TextView[@resource-id="com.cnspeedtest.globalspeed:id/upload_speed_value"]'
        while self.find_element_by_xpath(flag_element).text == '--':
            # logger.info("Speed test is in progress...")
            time.sleep(1)
        
        # collect downrate & uprate

        x_downrate = '//android.widget.TextView[@resource-id="com.cnspeedtest.globalspeed:id/download_speed_value"]'
        x_uprate = '//android.widget.TextView[@resource-id="com.cnspeedtest.globalspeed:id/upload_speed_value"]'
        downrate = float(self.find_element_by_xpath(x_downrate).text.split('Mbps')[0])
        uprate = float(self.find_element_by_xpath(x_uprate).text.split('Mbps')[0])

        # send result to lark
        
        # self.report_result_to_lark("信通院全球网测", downrate, uprate, timestamp, formatted_time)
        report_threading = threading.Thread(target=self.report_result_to_lark, args=("信通院全球网测", downrate, uprate, timestamp, formatted_time))
        report_threading.start()

        return
        
    def batch_execute_speed_test(self, count = 1):
        for i in range(count):
            self.speed_test_process()
        logger.info("Speed tests completed")
        
    def close(self):
        self.driver.quit()


def main():
    webhook = 'https://www.feishu.cn/flow/api/trigger-webhook/d6a7561781e891410f1b264bf2677bed'
    gst = GlobalSpeedTestHandler("com.cnspeedtest.globalspeed", 12, 4723, "/wd/hub", webhook)
    gst.batch_execute_speed_test(5)
    gst.close()
    


if __name__ == "__main__":
    main()