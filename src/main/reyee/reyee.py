import os
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
from src.main.security.GetCode import GetCode
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


class ReyeeSTHandler:
    def __init__(self, packageName, platformVersion, port, api, codepath, executeSerial, webhook = '') -> None:
        self.packageName = packageName
        self.platformVersion = platformVersion
        self.port = port
        self.api = api
        self.larkWebhook = webhook
        self.driver = self.init_conn()
        self.password = GetCode(codepath)
        self.executeSerial = executeSerial

        

    def init_conn(self):
        caps = {
        "platformName": "Android",
        "appium:platformVersion": str(self.platformVersion),
        "appium:appPackage": self.packageName,
        "appium:unicodeKeyboard": True,
        "appium:resetKeyboard": True,
        "appium:noReset": True,
        "appium:newCommandTimeout": 1000,
        "appium:automationName": "UiAutomator2",
        "appium:autoGrantPermissions": True,
        "appium:skipServerInstallation": True,
        "appium:skipDeviceInitialization": True,
        "appium:appActivity": ".MainActivity",
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

    def goto_speedTestPage(self):
        logger.info("goto speed test page")
        x_tool_kit = "//android.widget.Button[@content-desc=\"工具, tab, 4 of 5\"]/android.view.ViewGroup/android.view.ViewGroup"
        self.click_by_xpath(x_tool_kit)
        print("toolkit clicked")
        x_speed_test = "//android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup[3]/android.widget.ImageView"
        self.click_by_xpath(x_speed_test)

    def start_speed_test(self):
        time.sleep(2)
        # click element to start speed test
        x_start_test = "//android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup[2]"
        # exist_path = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.view.ViewGroup[2]/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup[2]/android.view.ViewGroup[2]/android.view.ViewGroup[3]'
        exist_path = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.view.ViewGroup[2]/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup[2]/android.view.ViewGroup[1]'
        self.click_by_xpath(x_start_test)
        time.sleep(5)
        while True:

            # delay = self.find_elements_in_view_group(exist_path)[1].text
            # if not self.check_element_exists(exist_path):
            if self.check_element_exists(exist_path) and self.find_elements_in_view_group(exist_path)[1].text == "--":
                time.sleep(2)
                logger.info("continue called")
                continue
            elif not self.check_element_exists(exist_path):
                self.click_by_xpath(x_start_test)
                time.sleep(2)
                continue
            else:
                logger.info("Speed test started")
                break
    
    def back_to_speed_test(self):
        target = '//android.widget.TextView[@text="返回"]'
        self.click_by_xpath(target)
        
    def report_result_to_lark(self, tag, downrate, uprate, timestamp, formatted_time, env = "unknown"):
        # send post to self.larkWebhook to report the speed test result
        deviceInfo = self.get_device_info()
        data = {
            "code": self.password,
            "msg": "SPD_TEST",
            "cloud": "CN",
            "env": env, # 对接正式/测试
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
    
    def speed_test_process(self, tag, env, from_desktop = True, i=0):
        timestamp = time.time()
        # transfer the timestamp to yyyy-mm-dd hh:mm:ss format
        timeArray = time.localtime(timestamp)
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        if from_desktop:
            self.goto_speedTestPage()
        self.start_speed_test()

        # wait for speed test to complete
        x_speed_test_complete = '//android.widget.TextView[@text="测速报告"]'
        self.wait_for_element(x_speed_test_complete, 60)

        #get up and down rate
        x_downrate = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[3]/android.view.ViewGroup[2]/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup/android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[3]/android.view.ViewGroup[1]'
        # x_downrate2 = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[3]/android.view.ViewGroup[2]/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup/android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[3]/android.view.ViewGroup[1]'
        x_uprate = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[3]/android.view.ViewGroup[2]/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup/android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[3]/android.view.ViewGroup[3]'
        x_uprate2 = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[3]/android.view.ViewGroup[2]/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup/android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[3]/android.view.ViewGroup[2]'
        try:
            downrate = float(self.find_elements_in_view_group(x_downrate)[2].text)
            uprate = float(self.find_elements_in_view_group(x_uprate)[2].text)
        except IndexError as e:
            downrate = float(self.find_elements_in_view_group(x_downrate)[2].text)
            uprate = float(self.find_elements_in_view_group(x_uprate2)[2].text)

        #使用多线程发送消息
        report_threading = threading.Thread(target=self.report_result_to_lark, args=(tag, downrate, uprate, timestamp, formatted_time, env))
        report_threading.start()
        # self.take_screen_shot("src/main/reyee/screenshots/", self.executeSerial+'_'+str(int(time.time()))+'_'+str(i)+'.jpg')
        
        self.back_to_speed_test()


    def execute_speed_tests(self, count, tag, env):
        try:
            self.speed_test_process(tag, env)
            for i in range(count-1):
                self.speed_test_process(tag, env, False, i+1)
            print("All process finished")
        except:
            print("An error occurred while executing speed tests")
            self.close()

    
    def take_screen_shot(self,save_path, file_name):
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        
        file_path = os.path.join(save_path, file_name)
        
        self.driver.get_screenshot_as_file(file_path)
        print(f"Screenshot saved to {file_path}")

    def close(self):
        self.driver.quit()

def main():
    webhook = 'https://www.feishu.cn/flow/api/trigger-webhook/d6a7561781e891410f1b264bf2677bed'
    codepath = "C:/Users/eureka/Downloads/code.txt"
    reyee = ReyeeSTHandler("cn.com.ruijie.ywl", 12, 4723, "/wd/hub", codepath, webhook)
    # reyee = ReyeeSTHandler("cn.com.ruijie.ywl", 13, 4723, "/wd/hub", webhook)
    # reyee.speed_test_process("CN")
    # reyee.speed_test_process("CN", False)
    reyee.execute_speed_tests(100, "enet-8.1.6", "PUBLIC")
    # reyee.execute_speed_tests(10, "海外内测对接正式")
    reyee.close()

if __name__ == "__main__":
    main()