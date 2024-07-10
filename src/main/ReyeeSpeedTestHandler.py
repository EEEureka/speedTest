import uiautomator2 as u2
import time
import os

class ReyeeSpeedTestHandler:
    def __init__(self, d):
        self.d
        
    def initConn(self):
        self.d = u2.connect()
    
    def goToToolKit(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def startApp(self):
        raise NotImplementedError("Subclass must implement abstract method")
    
    