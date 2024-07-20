import threading
import re
import json
import subprocess
import requests
from loguru import logger

import time

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.main.security.GetCode import GetCode

class ReyeeIntlSTHandler:
    
    def __init__(self, platformVersion, port, api, codepath, serial, webhook = '') -> None:
        self.packageName = "cn.com.ruijie.cloudapp"
        self.platformVersion =platformVersion
        self.activity = ".MainActivity"
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

    def text_locator(self, text):
        return AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")'
    
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
    
    def click_by_text(self, text, timeout=10):
        logger.info(f"text is {text}")
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(self.text_locator(text))).click()
        except Exception as e:
            logger.error(f"An error occurred while clicking {text}: {str(e)}")
    
    def click_by_elementId(self, elementId, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((AppiumBy.ID, elementId))).click()
        except Exception as e:
            logger.error(f"An error occurred while clicking {elementId}: {str(e)}")
    
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
    
    def wait_for_element_by_text(self, text, timeout = 10): 
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(self.text_locator(text)))
            return True
        except Exception as e:
            logger.error(f"An error occurred while waiting for element {text}: {str(e)}")
            return False

    def check_element_exists(self, xpath):
        # 尝试查找元素
        elements = self.driver.find_elements(AppiumBy.XPATH, xpath)
        # 如果找到的元素列表不为空，则返回True，表示元素存在
        # print(elements)
        return len(elements) > 0

    def find_elements_in_view_group(self, viewGroupXpath, timeout = 10):
        try:
            # 定位到ViewGroup
            view_group = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((AppiumBy.XPATH, viewGroupXpath))
            )
            # 获取ViewGroup中的所有元素
            elements_in_group = self.driver.find_elements(AppiumBy.XPATH, f"{viewGroupXpath}/descendant::*")
            for i in elements_in_group:
                print(i.text)
            return elements_in_group
        except Exception as e:
            logger.error(f"An error occurred while finding elements in view group {viewGroupXpath}: {str(e)}")
            return []
    
    def test_find_view_group(self, timeout = 10):
        while True:
            viewGroupXpath = input("Please input the xpath of the view group: ")
            try:
                # 定位到ViewGroup
                view_group = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((AppiumBy.XPATH, viewGroupXpath))
                )
                # 判断是否获取到ViewGroup
                if view_group:
                    logger.info(f"View group found: {view_group}")
                    # 获取ViewGroup中的所有元素
                    elements_in_group = self.driver.find_elements(AppiumBy.XPATH, f"{viewGroupXpath}/descendant::*")
                    for i in elements_in_group:
                        logger.info(i.text)
            except Exception as e:
                logger.error(f"An error occurred while finding elements in view group {viewGroupXpath}: {str(e)}")
                return None

    def find_element_by_xpath(self, xpath):
        return self.driver.find_element(AppiumBy.XPATH, xpath)
    
    def find_elements_by_text(self, text, timeout = 10):
        return self.driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")')

    def report_result_to_lark(self, tag, downrate, uprate, formatted_time):

        # send post to self.larkWebhook to report the speed test result
        deviceInfo = self.get_device_info()
        data = {
            "code": self.password,
            "msg": "SPD_TEST",
            "cloud": "INTL",
            "env": "PUBLIC", # 对接正式/测试
            "tag": tag,
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
    
    def change_language_to_english(self):
        x_tabs = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.ViewGroup[4]/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[6]/android.view.ViewGroup'
        self.find_elements_in_view_group(x_tabs)[4].click()
        x_more = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.ViewGroup[5]/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[5]/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup'
        self.click_by_xpath(x_more)
        x_language = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.ViewGroup[5]/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.view.ViewGroup[2]/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup[2]/android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[7]'
        self.click_by_xpath(x_language)
        self.click_by_text("English")
        x_confirm = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.ViewGroup[7]/android.view.ViewGroup/android.view.ViewGroup[2]/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[1]'
        self.click_by_xpath(x_confirm)
        time.sleep(5)
        
    def goto_speed_test(self):
        x_toolkit = '//android.widget.Button[@content-desc="Toolkit, tab, 4 of 5"]'
        self.click_by_xpath(x_toolkit, timeout = 20)
        x_speed_test = '//android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup[3]/android.widget.ImageView'
        self.click_by_xpath(x_speed_test)
        time.sleep(1)
        # if self.wait_for_element('//android.widget.TextView[@text="Test Now"]'):
        #     logger.info("Speed test page loaded successfully.")
        #     return
        
    def start_speed_test(self):
        logger.info("waiting for click 'test now' button")
        x_st_btn = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.view.ViewGroup[2]/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup[2]/android.view.ViewGroup[1]/android.view.ViewGroup[4]'
        # data_view_group = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.ViewGroup[3]/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.view.ViewGroup[2]/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup[2]/android.view.ViewGroup[1]'
        while True:
            self.click_by_xpath(x_st_btn)
            time.sleep(3)
            x_para_exists = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.view.ViewGroup[2]/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup[2]/android.view.ViewGroup[1]'
            vg_list = self.find_elements_in_view_group(x_para_exists)
            if self.check_element_exists(x_para_exists):
                logger.info("找到延迟")
                # 判断vg_list[1].text可否被转换成float
                try:
                    float(vg_list[1].text)
                    logger.info(f"延迟为{vg_list[1].text}, 测速确认开始")
                    break
                except ValueError:
                    logger.info("延迟不是数字，继续等待")
                    continue
            else:
                logger.info("找不到元素，继续等待")
                continue
        return
    
    def data_collection(self, tag, formatted_time):
        # self.wait_for_element_by_text("Report", timeout = 60)
        x_report = '//android.widget.TextView[@text="Report"]'
        while not self.check_element_exists(x_report):
            time.sleep(1)

        logger.info("start collecting data")
        # x_uprate = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[3]/android.view.ViewGroup[2]/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup/android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[3]/android.view.ViewGroup[1]'
        # x_downrate = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[3]/android.view.ViewGroup[2]/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup/android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[3]/android.view.ViewGroup[3]'
        x_uprate = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[3]/android.view.ViewGroup[2]/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup/android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[3]/android.view.ViewGroup[3]'
        x_downrate = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[3]/android.view.ViewGroup[2]/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup/android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[3]/android.view.ViewGroup[1]'
        # logger.info(self.find_elements_in_view_group(x_uprate))
        # logger.info(self.find_elements_in_view_group(x_downrate))
        uprate = float(self.find_elements_in_view_group(x_uprate)[2].text)
        downrate = float(self.find_elements_in_view_group(x_downrate)[2].text)


        report_threading = threading.Thread(target=self.report_result_to_lark, args=(tag, downrate, uprate, formatted_time))
        report_threading.start()
        back_btn = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[3]/android.view.ViewGroup[2]/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup/android.view.ViewGroup[3]/android.view.ViewGroup[1]'
        self.click_by_xpath(back_btn)
        # self.click_by_text("Back")

    def speed_test_process(self, tag, is_from_main_page = True):
        if is_from_main_page:
            self.goto_speed_test()

        # get timestamp
        timestamp = time.time()
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))

        # main process
        self.start_speed_test()
        self.data_collection("ReyeeIntl", formatted_time)
        return

    def batch_speed_test(self, tag, num):
        try:
            for i in range(num):
                self.speed_test_process(tag, True if i == 0 else False)
            logger.info(f"Speed test finished, {num} times in total.")
            return
        except:
            logger.error("Speed test failed.")
            self.close()

    def close(self):
        self.driver.quit()
        return
    
    