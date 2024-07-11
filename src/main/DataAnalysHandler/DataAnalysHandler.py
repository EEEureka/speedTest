import random
import matplotlib.pyplot as plt
import numpy as np
import time
import os
import statistics
import pandas
import openpyxl
import json

from openpyxl.drawing.image import Image

class DataAnalysHandler:
    
    def __init__(self, input_file_path, output_file_path) -> None:
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        
    def transfer_xlsx_to_json(self):
        df = pandas.read_excel(self.input_file_path, sheet_name="测速数据收集")
        data = {}
        # 表格列有：环境	触发时间	云端（国内/海外）	云端环境(生产/测试）	版本（编号）	型号	系统	上行	下行
        # 需要将数据转换成：
        # data = {
        #     "环境1":{
        #         "云端1":{
        #             "云端环境1":{
        #                 "版本1":{
        #                     "型号1":{
        #                         "system":"xxx",
        #                         "测试数据": [
        #                             {
        #                                 "uprate": 123,
        #                                 "downrate": 123,
        #                                 "time": "2021-01-01 00:00:00"
        #                             }
        #                         ]
        #                     }
        #                 }
        #             }
        #         }
        #     }
        # }
            
        for i in range(2, len(df)):
            # 访问"环境"列i行值
            env = df.loc[i, "环境"]
            cloud = df.loc[i, "云端（国内/海外）"]
            cloud_env = df.loc[i, "环境(生产/测试)"]
            version = df.loc[i, "版本（编号）"]
            model = df.loc[i, "型号"]
            system = df.loc[i, "系统"]
            uprate = df.loc[i, "上行"]
            downrate = df.loc[i, "下行"]
            
            # 判断data中是否有该key
            if env not in data:
                data[env] = {}
            if cloud not in data[env]:
                data[env][cloud] = {}
            if cloud_env not in data[env][cloud]:
                data[env][cloud][cloud_env] = {}
            if version not in data[env][cloud][cloud_env]:
                data[env][cloud][cloud_env][version] = {}
            if model not in data[env][cloud][cloud_env][version]:
                data[env][cloud][cloud_env][version][model] = {}
                data[env][cloud][cloud_env][version][model]["system"] = system
                data[env][cloud][cloud_env][version][model]["测试数据"] = []
            data[env][cloud][cloud_env][version][model]["测试数据"].append({
                "uprate": uprate,
                "downrate": downrate,
                "time": df.loc[i, "触发时间"]
            })
        
        return data
    
    def analyse_data(self, data):
        # 计算每个环境-云端-云端环境-版本-型号的:
        # 1. 上行平均值
        # 2. 下行平均值
        # 3. 上行波动值: 使用标准差计算
        # 4. 下行波动值: 使用标准差计算
        # 5. 上行波动范围: 最大值-最小值
        # 6. 下行波动范围: 最大值-最小值
        # 输出数据:
        output = [
            {
                "环境": "环境1",
                "云端": "云端1",
                "版本": "版本1",
                "设备型号": "型号1_系统1",
                "上行平均值": 123,
                "下行平均值": 123,
                "上行波动值": 123,
                "下行波动值": 123,
                "上行波动范围": 123,
                "下行波动范围": 123,
                "上行分布图": "path/to/figure1.png",
                "下行分布图": "path/to/figure2.png",
                "样本数量": 123
            },
            {...}
        ]
        output = []
        for env in data:
            for cloud in data[env]:
                for cloud_env in data[env][cloud]:
                    for version in data[env][cloud][cloud_env]:
                        for model in data[env][cloud][cloud_env][version]:
                            uprates = []
                            downrates = []
                            for test_data in data[env][cloud][cloud_env][version][model]["测试数据"]:
                                uprates.append(test_data["uprate"])
                                downrates.append(test_data["downrate"])
                            # 计算样本平均值
                            uprate_mean = statistics.mean(uprates)
                            downrate_mean = statistics.mean(downrates)
                            # 计算总体标准差
                            uprates_std = statistics.stdev(uprates) if len(uprates) > 1 else 0
                            downrates_std = statistics.stdev(downrates) if len(downrates) > 1 else 0
                            # 计算波动范围
                            uprate_range = max(uprates) - min(uprates)
                            downrate_range = max(downrates) - min(downrates)
                            # 绘制上下行偏差分布图
                            path = "src/main/DataAnalysHandler/figures/"
                            uprate_file_path = self.generate_and_save_plot(uprates, path, f"{env}_{cloud}_{cloud_env}_{version}_{model}_uprate")
                            downrate_file_path = self.generate_and_save_plot(downrates, path, f"{env}_{cloud}_{cloud_env}_{version}_{model}_downrate")
                            output.append({
                                "环境": env,
                                "云端": cloud,
                                "版本": version,
                                "设备型号": f"{model}_{data[env][cloud][cloud_env][version][model]['system']}",
                                "上行平均值": uprate_mean,
                                "下行平均值": downrate_mean,
                                "上行波动值": uprates_std,
                                "下行波动值": downrates_std,
                                "上行波动范围": uprate_range,
                                "下行波动范围": downrate_range,
                                "上行分布图": uprate_file_path,
                                "下行分布图": downrate_file_path,
                                "样本数量": len(uprates)
                            })
        return output
    
    def save_data_to_xlsx(self, data, output_file_path):
        # data 格式:
        # data = [
        #     {
        #         "环境": "环境1",
        #         "云端": "云端1",
        #         "版本": "版本1",
        #         "设备型号": "型号1_系统1",
        #         "上行平均值": 123,
        #         "下行平均值": 123,
        #         "上行波动值": 123,
        #         "下行波动值": 123,
        #         "上行波动范围": 123,
        #         "下行波动范围": 123,
        #         "上行分布图": "path/to/figure1.png",
        #         "下行分布图": "path/to/figure2.png",
        #         "样本数量": 123
        #     },
        #     {...}
        # ]
        # 创建一个新的Excel文件
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        # "环境"第一列, 云端第二列, 版本第三列, 
        # 上行平均值第一行, 上行波动值第二行, 上行波动范围第三行, 上行分布图第四行, 下行同理
        # 写入表头: 环境, 云端, 版本, 详细信息
        sheet["A1"] = "环境"
        sheet["B1"] = "云端"
        sheet["C1"] = "版本"
        sheet["D1"] = "设备型号"
        sheet["E1"] = "详细信息"
        sheet["F1"] = "详细信息"
        unit = 9
        counter = 0
        imgsize = (1280 / 3, 720 / 3)
        sheet.column_dimensions["F"].width = imgsize[0]*0.14
        sheet.column_dimensions["D"].width = 20
        sheet.column_dimensions["E"].width = 20
        sheet.column_dimensions["A"].width = 20
        sheet.column_dimensions["B"].width = 20
        sheet.column_dimensions["C"].width = 20
        for i in data:
            sheet.append([i["环境"], i["云端"], i["版本"], i["设备型号"], "上行平均值", i["上行平均值"]])
            sheet.append([i["环境"], i["云端"], i["版本"], i["设备型号"], "上行标准差", i["上行波动值"]])
            sheet.append([i["环境"], i["云端"], i["版本"], i["设备型号"], "上行波动范围", i["上行波动范围"]])
            sheet.append([i["环境"], i["云端"], i["版本"], i["设备型号"], "上行分布图"])
            img = Image(i["上行分布图"])
            img.width, img.height = imgsize
            sheet.add_image(img, f"F{unit*counter+5}")
            sheet.row_dimensions[unit*counter+5].height = imgsize[1]*0.8

            sheet.append([i["环境"], i["云端"], i["版本"], i["设备型号"], "下行平均值", i["下行平均值"]])
            sheet.append([i["环境"], i["云端"], i["版本"], i["设备型号"], "下行标准差", i["下行波动值"]])
            sheet.append([i["环境"], i["云端"], i["版本"], i["设备型号"], "下行波动范围", i["下行波动范围"]])
            sheet.append([i["环境"], i["云端"], i["版本"], i["设备型号"], "下行分布图"])
            img = Image(i["下行分布图"])
            img.width, img.height = imgsize
            sheet.add_image(img, f"F{unit*counter+9}")
            sheet.row_dimensions[unit*counter+9].height = imgsize[1]*0.8

            sheet.append([i["环境"], i["云端"], i["版本"], i["设备型号"], "样本数量", i["样本数量"]])
            counter += 1
        # 从第二行开始, 每9行分别合并1-4列单元格
        for i in range(2, len(data)*unit, unit):
            sheet.merge_cells(f"A{i}:A{i+8}")
            sheet.merge_cells(f"B{i}:B{i+8}")
            sheet.merge_cells(f"C{i}:C{i+8}")
            sheet.merge_cells(f"D{i}:D{i+8}")
        
        book_name = output_file_path+"output.xlsx" if output_file_path[-1] == "/" else output_file_path+"/output.xlsx"
        # 保存文件
        workbook.save(book_name)
        return
    
    def execute(self, input_file_path, output_file_path):
        data = self.transfer_xlsx_to_json()
        # 将data写入output.json
        # print(data)
        output = self.analyse_data(data)
        self.save_data_to_xlsx(output, output_file_path)
                    
                            
    def generate_and_save_plot(self, data, folder_path, fig_name):
    
        # 计算平均值
        mean_value = statistics.mean(data)

        # 计算每个样本的相对偏差值并转换为百分比
        deviation_percent = [abs(x - mean_value) / mean_value * 100 for x in data]

        # 初始化10个偏差值范围的计数器
        deviation_counts = [0] * 10

        # 对每个样本的偏差值进行分组计数
        for deviation in deviation_percent:
            index = int(deviation // 10)
            index = min(index, 9)  # 确保最大的偏差值（100%）也被包含在最后一组
            deviation_counts[index] += 1

        # 将计数转换为占比
        total_samples = len(data)
        deviation_proportions = [count / total_samples for count in deviation_counts]

        plt.figure(figsize=(12, 6))
        bars = plt.bar(range(10), deviation_proportions, tick_label=[f'{i*10}-{(i+1)*10}%' for i in range(10)])

        # 在每个柱子上方添加y值
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2.0, height, f'{height:.2%}', ha='center', va='bottom')

        # 使用32位随机字符串作为文件名
        
        file_name = f"{fig_name}.png"
        file_path = os.path.join(folder_path, file_name)

        # 保存图片
        plt.savefig(file_path)

        # 清除当前的figure，防止重复绘制
        plt.clf()
        
        # 获取工作目录
        

        # 返回图片文件的路径
        return os.getcwd().replace("\\", "/") + "/" + file_path if file_path[1] != ":" else file_path


def main():
    input_file_path = "C:/Users/eureka/Downloads/测速数据收集 (4).xlsx"
    output_file_path = "D:/pyproj/st/src/output"
    dah = DataAnalysHandler(input_file_path, output_file_path)
    dah.execute(input_file_path, output_file_path)

if __name__ == "__main__":
    main()