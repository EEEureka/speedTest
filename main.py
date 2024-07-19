from loguru import logger
import time
from src.main.reyee_intl.ReyeeIntl import ReyeeIntlSTHandler
import src.main.DataAnalysHandler.DataAnalysHandler as DAH
from src.main.GlobalSpeedTest.GlobalSpeedTest import GlobalSpeedTestHandler
from src.main.reyee.reyee import ReyeeSTHandler
from src.main.HuaBanSpeedTest.HuaBanSpeedTest import HuaBanSpeedTestHandler
from src.main.DataAnalysHandler.DataAnalysHandler2 import DataAnalysHandler2


def main(serial):
    input_file_path = "C:/Users/eureka/Downloads/测速数据收集 (8).xlsx"
    output_file_path = "D:/pyproj/st/src/output"
    module_base_path = ""
    dah = DAH.DataAnalysHandler(input_file_path, output_file_path)
    dah.execute(input_file_path, output_file_path, serial)

def global_speed_test(serial):
    webhook = 'https://www.feishu.cn/flow/api/trigger-webhook/d6a7561781e891410f1b264bf2677bed'
    # gst = GlobalSpeedTestHandler("com.cnspeedtest.globalspeed", 14, 4723, "/wd/hub", webhook)
    codeFilePath = "C:/Users/eureka/Desktop/code.txt"
    gst = GlobalSpeedTestHandler(12, 4723, "/wd/hub", codeFilePath, serial, webhook)
    gst.batch_execute_speed_test(80)
    gst.close()

def reyee(serial):
    webhook = 'https://www.feishu.cn/flow/api/trigger-webhook/d6a7561781e891410f1b264bf2677bed'
    codepath = "C:/Users/eureka/Desktop/code.txt"
    reyee = ReyeeSTHandler("cn.com.ruijie.ywl", 12, 4723, "/wd/hub", codepath, serial, webhook)
    # reyee = ReyeeSTHandler("cn.com.ruijie.ywl", 12, 4723, "/wd/hub", codepath, serial, webhook)
    # reyee = ReyeeSTHandler("cn.com.ruijie.ywl", 13, 4723, "/wd/hub", webhook)
    # reyee.speed_test_process("CN")
    # reyee.speed_test_process("CN", False)
    reyee.execute_speed_tests(20, "enet-8.1.7_2407171826", "PUBLIC")
    # reyee.execute_speed_tests(10, "海外内测对接正式")
    reyee.close()

def reyee_intl(serial):
    webhook = 'https://www.feishu.cn/flow/api/trigger-webhook/d6a7561781e891410f1b264bf2677bed'
    codepath = "C:/Users/eureka/Desktop/code.txt"
    reyee_intl = ReyeeIntlSTHandler(12, 4723, "/wd/hub", codepath, serial, webhook)
    # reyee_intl.batch_speed_test("8.1.7-2407161002", 3)
    reyee_intl.speed_test_process("8.1.7-2407161002")
    # reyee_intl.test_find_view_group()
    reyee_intl.close()

def HB(serial):
    webhook = 'https://www.feishu.cn/flow/api/trigger-webhook/d6a7561781e891410f1b264bf2677bed'
    codepath = "C:/Users/eureka/Desktop/code.txt"
    hb = HuaBanSpeedTestHandler(12, 4723, "/wd/hub", serial, codepath, webhook)
    hb.batch_speed_test(3)
    hb.close()

def reyee_obj(serial, os):
    webhook = 'https://www.feishu.cn/flow/api/trigger-webhook/d6a7561781e891410f1b264bf2677bed'
    codepath = "C:/Users/eureka/Desktop/code.txt"
    return ReyeeSTHandler("cn.com.ruijie.ywl", os, 4723, "/wd/hub", codepath, serial, webhook)

def reyee_intl_obj(serial, os):
    webhook = 'https://www.feishu.cn/flow/api/trigger-webhook/d6a7561781e891410f1b264bf2677bed'
    codepath = "C:/Users/eureka/Desktop/code.txt"
    return ReyeeIntlSTHandler(os, 4723, "/wd/hub", codepath, serial, webhook)

def HB_obj(serial, os):
    webhook = 'https://www.feishu.cn/flow/api/trigger-webhook/d6a7561781e891410f1b264bf2677bed'
    codepath = "C:/Users/eureka/Desktop/code.txt"
    return HuaBanSpeedTestHandler(os, 4723, "/wd/hub", serial, codepath, webhook)

def global_obj(serial, os):
    webhook = 'https://www.feishu.cn/flow/api/trigger-webhook/d6a7561781e891410f1b264bf2677bed'
    codeFilePath = "C:/Users/eureka/Desktop/code.txt"
    return GlobalSpeedTestHandler(os, 4723, "/wd/hub", codeFilePath, serial, webhook)

def batch_execute_speed_test():
    serial = 'SELF_DEBUG_2'
    times = 3
    env = 'PUBLIC'
    cn_tag = 'enet-8.1.7_2407181528'
    intl_tag = 'ruijiecloud-8.1.7_2407191014.apk'
    os_version = 13
    # os_version = 13
    start_time = time.time()

    cn_reyee = reyee_obj(serial, os_version)
    cn_reyee.execute_speed_tests(times, cn_tag, env)
    cn_reyee.close()

    intl_reyee = reyee_intl_obj(serial, os_version)
    intl_reyee.batch_speed_test(intl_tag, times)
    intl_reyee.close()

    global_test = global_obj(serial, os_version)
    global_test.batch_execute_speed_test(times)
    global_test.close()

    hb = HB_obj(serial, os_version)
    hb.batch_speed_test(times)

    end_time = time.time()
    delta_time = end_time - start_time
    logger.info(f"耗时: {delta_time}")

    hb.close()

def data2():
    file_path = "C:/Users/eureka/Downloads/测速数据收集 (11).xlsx"
    output_path = "src/output/"
    file_name = 'output.xlsx'
    serial = 'SELF_DEBUG_2'
    dah = DataAnalysHandler2(file_path, output_path, file_name, serial)
    dah.execute()


if __name__ == "__main__":
    # executeSerial = "ST_UPDATE_2_0717"
    executeSerial = "SELF_DEBUG1"

    # executeSerial = "TEMP1"
    # global_speed_test(executeSerial)
    # reyee(executeSerial)
    # main()
    # reyee_intl(executeSerial)
    batch_execute_speed_test()
    # data2()