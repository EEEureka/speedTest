import threading
import re
import json
import subprocess
import requests
from loguru import logger

import time

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from src.main.security.GetCode import GetCode


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class HuaBanSpeedTestHandler:
    def __init__(self, platformVersion, port, api, serial, codepath, webhook = '') -> None:
        self.packageName =  "com.huawei.genexcloud.speedtest"
        self.platformVersion = platformVersion,
        self.activity = ".ui.SplashActivity"
        self.port = port
        self.api = api
        self.larkWebhook = webhook
        self.driver = self.init_conn()
        self.executeSerial = serial
        self.password = GetCode(codepath)

        

    def init_conn(self):
        caps = {
        "platformName": "Android",
        "appium:platformVersion": str(self.platformVersion),
        "appium:appPackage": self.packageName,
        "appium:unicodeKeyboard": True,
        "appium:resetKeyboard": True,
        "appium:noReset": True,
        "appium:newCommandTimeout": 100,
        "appium:automationName": "UiAutomator2",
        "appium:autoGrantPermissions": True,
        "appium:skipServerInstallation": True,
        "appium:skipDeviceInitialization": True,
        "appium:appActivity": self.activity,
        "appium:waitForIdleTimeout": 2,
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
        # print(len(elements))
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

    def report_result_to_lark(self, tag, downrate, uprate, timestamp, formatted_time):
        # send post to self.larkWebhook to report the speed test result
        deviceInfo = self.get_device_info()
        data = {
            "code": self.password,
            "msg": "SPD_TEST",
            "cloud": "非睿易应用",
            "env": "非睿易应用", # 对接正式/测试
            "tag": tag, # 版本编号， 即打包出来时的文件名
            "executeSerial": self.executeSerial,
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

    def find_element_by_xpath(self, xpath):
        return self.driver.find_element(AppiumBy.XPATH, xpath)

    def start_speed_test(self):
        target_element = '//android.view.View[@resource-id="com.huawei.genexcloud.speedtest:id/mainPart"]'
        self.click_by_xpath(target_element)
        check_element = '//android.view.View[@resource-id="com.huawei.genexcloud.speedtest:id/lineChart"]'
        while not self.check_element_exists(check_element):
            self.click_by_xpath(target_element)
            time.sleep(1)
        time.sleep(2)
        error_target = '//android.widget.TextView[@resource-id="com.huawei.genexcloud.speedtest:id/tvDialogTitle"]'
        if self.check_element_exists(error_target):
            self.click_by_xpath('//android.widget.Button[@resource-id="com.huawei.genexcloud.speedtest:id/btnRight"]')
            self.click_by_xpath('//android.widget.TextView[@text="使用推荐节点"]')
            self.speed_test_process()
    
    def speed_test_process(self, from_main_page = True):
        # get timestamp
        timestamp = time.time()
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))

        # main process
        if from_main_page:
            self.start_speed_test()
        target_element = '//android.widget.Button[@resource-id="com.huawei.genexcloud.speedtest:id/btn_test_again"]'
        self.wait_for_element(target_element, 60)
        x_downrate = '//android.widget.TextView[@resource-id="com.huawei.genexcloud.speedtest:id/tv_downspeed"]'
        x_uprate = '//android.widget.TextView[@resource-id="com.huawei.genexcloud.speedtest:id/tv_uploadspeed"]'
        downrate = float(self.find_element_by_xpath(x_downrate).text)
        uprate = float(self.find_element_by_xpath(x_uprate).text)

        # report result to lark
        report_threading = threading.Thread(target=self.report_result_to_lark, args=("花瓣测速", downrate, uprate, timestamp, formatted_time))
        report_threading.start()

        return
        
    def test_again(self):
        target = '//android.widget.Button[@resource-id="com.huawei.genexcloud.speedtest:id/btn_test_again"]'
        self.click_by_xpath(target)
        while self.check_element_exists(target):
            self.click_by_xpath(target)
            time.sleep(1)
        time.sleep(2)
        error_target = '//android.widget.TextView[@resource-id="com.huawei.genexcloud.speedtest:id/tvDialogTitle"]'
        if self.check_element_exists(error_target):
            self.click_by_xpath('//android.widget.Button[@resource-id="com.huawei.genexcloud.speedtest:id/btnRight"]')
            self.click_by_xpath('//android.widget.TextView[@text="使用推荐节点"]')
            self.speed_test_process()
        self.speed_test_process(False)

    def batch_speed_test(self, times = 1):
        try:
            self.speed_test_process()
            for i in range(times-1):
                self.test_again()
        except Exception as e:
            logger.error(f"An error occurred while batch speed test: {str(e)}")
            self.close()
    
    def close(self):
        self.driver.quit()


def main():
    webhook = 'https://www.feishu.cn/flow/api/trigger-webhook/d6a7561781e891410f1b264bf2677bed'
    hb = HuaBanSpeedTestHandler("com.huawei.genexcloud.speedtest", 12, 4723, "/wd/hub", webhook)
    hb.batch_speed_test(5)
    hb.close()
    # hb.test_again()

if __name__ == "__main__":
    main()
    