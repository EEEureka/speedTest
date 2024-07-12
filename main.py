import src.main.DataAnalysHandler.DataAnalysHandler as DAH
from src.main.GlobalSpeedTest.GlobalSpeedTest import GlobalSpeedTestHandler


def main():
    input_file_path = "C:/Users/eureka/Downloads/测速数据收集 (7).xlsx"
    output_file_path = "D:/pyproj/st/src/output"
    module_base_path = ""
    dah = DAH.DataAnalysHandler(input_file_path, output_file_path)
    dah.execute(input_file_path, output_file_path)

def global_speed_test():
    webhook = 'https://www.feishu.cn/flow/api/trigger-webhook/d6a7561781e891410f1b264bf2677bed'
    # gst = GlobalSpeedTestHandler("com.cnspeedtest.globalspeed", 14, 4723, "/wd/hub", webhook)
    codeFilePath = ""
    gst = GlobalSpeedTestHandler("com.cnspeedtest.globalspeed", 12, 4723, "/wd/hub", codeFilePath, webhook)
    gst.batch_execute_speed_test(2)
    gst.close()

if __name__ == "__main__":
    global_speed_test()