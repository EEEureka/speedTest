import threading
import json
import requests
import uiautomator2 as u2

class ReyeeHandlerU2:
    
    def __init__(self, devices = [], webhook = ""):
        if devices == []:
            self.driver = [u2.connect()]
        else:
            self.driver = [u2.connect(device) for device in devices]
        for i in devices:
            i.settings['wait_timeout'] = 60
        self.larkWebhook = webhook
        self.packageName = "cn.com.ruijie.wyl"
    
    def openApp(self, driver: u2.Device):
        driver.app_start(self.packageName)
    
    def goto_speed_test_page(self, d: u2.Device):
        d(text="测速").click()
        d(text="工具").click()
        d(text="测网速").click()
    
    def start_speed_test(self, d: u2.Device):
        d(text="立即测速").click()
        
