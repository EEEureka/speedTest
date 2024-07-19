import statistics
import random
import matplotlib.pyplot as plt
import numpy as np
import time
import os
import statistics
import pandas
import openpyxl
import json
# import src.main.model_mapping.model_mapping as mapping

from openpyxl.drawing.image import Image
from openpyxl.styles import Alignment
from loguru import logger

class DataAnalysHandler2:
    def __init__(self, input_file_path, output_file_path, file_name, serial)-> None:
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        self.file_name = file_name
        self.serial = serial
        # self.model_mapping = mapping.ModelMapping(model_base_path)

    def transfer_xlsx_to_json(self, serial):
        df = pandas.read_excel(self.input_file_path, sheet_name="测速数据收集")
        data = {}
        '''
        表格列有：环境	触发时间	云端（国内/海外）	云端环境(生产/测试）	版本（编号）	型号	系统	上行	下行
        需要将数据转换成：
        data = {
            "环境1":{
                "standard_uprate": 123,
                "standard_downrate": 123,
                "云端1":{
                    "云端环境1":{
                        "版本1":{
                            "型号1":{
                                "system":"xxx",
                                "测试数据": [
                                    {
                                        "uprate": 123,
                                        "downrate": 123,
                                        "time": "2021-01-01 00:00:00"
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
        '''
            
        for i in range(2, len(df)):
            if serial != df.loc[i, "执行编号"]:
                continue
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
        # print(data)
        return data
    
    def analyse_data(self, data):
        # data[env][cloud][cloud_env][version][model]["测试数据"]
        # output like: 
        '''output = {
            'env': {
                'reyee_cn': {
                    "device1": {
                        "up_fluctuation": 0.1,
                        "down_fluctuation": 0.1,
                        "up_result_set": [1, 2, 3],
                        "down_result_set": [1, 2, 3]
                    }

                },
                'reyee_intl': {
                },
                'global': {
                },
                'huaban': {
                }
            }
        }
        '''
        output = {}
        for env in data:
            if env not in output:
                output[env] = {}
            for cloud in data[env]:
                if cloud == '非睿易应用':
                    for app_tag in data[env][cloud]['非睿易应用']:
                        if app_tag not in output[env]:
                            output[env][app_tag] = {}
                        for device in data[env][cloud]['非睿易应用'][app_tag]:
                            if not device in output[env][app_tag]:
                                output[env][app_tag][device] = {}
                            up_result_set = [i['uprate'] for i in data[env][cloud]['非睿易应用'][app_tag][device]['测试数据']]
                            down_result_set = [i['downrate'] for i in data[env][cloud]['非睿易应用'][app_tag][device]['测试数据']]
                            up_fluctuation = self.calculate_cv(up_result_set)
                            down_fluctuation = self.calculate_cv(down_result_set)
                            output[env][app_tag][device]['up_fluctuation'] = up_fluctuation
                            output[env][app_tag][device]['down_fluctuation'] = down_fluctuation
                            output[env][app_tag][device]["up_result_set"] = up_result_set
                            output[env][app_tag][device]["down_result_set"] = down_result_set
                        
                else:
                    if cloud not in output[env]:
                        output[env][cloud] = {}
                    for cloud_env in data[env][cloud]:
                        for app_tag in data[env][cloud][cloud_env]:
                            for device in data[env][cloud][cloud_env][app_tag]:
                                if device not in output[env][cloud]:
                                    output[env][cloud][device] = {}
                                up_result_set = [i['uprate'] for i in data[env][cloud][cloud_env][app_tag][device]['测试数据']]
                                down_result_set = [i['downrate'] for i in data[env][cloud][cloud_env][app_tag][device]['测试数据']]
                                up_fluctuation = self.calculate_cv(up_result_set)
                                down_fluctuation = self.calculate_cv(down_result_set)
                                output[env][cloud][device]['up_fluctuation'] = up_fluctuation
                                output[env][cloud][device]['down_fluctuation'] = down_fluctuation
                                output[env][cloud][device]["up_result_set"] = up_result_set
                                output[env][cloud][device]["down_result_set"] = down_result_set

        print(output)
        return output

    def output_to_excel(self, input_data, file_path, file_name):
        # 创建一个workbook对象
        wb = openpyxl.Workbook()
        # 获取当前活跃的worksheet,默认就是第一个worksheet
        ws = wb.active
        # 设置表头
        # {环境名称}(上行/下行) 睿易国内版本 睿易海外版本 全球网测 花瓣测速
        # 波动在10%以内 {国内符合条件数据占比} {海外符合条件数据占比} {全球网测符合条件数据占比} {花瓣测速符合条件数据占比}
        # 波动在10%到20%之间 {国内符合条件数据占比} {海外符合条件数据占比} {全球网测符合条件数据占比} {花瓣测速符合条件数据占比}
        # 波动大于20% {国内符合条件数据占比} {海外符合条件数据占比} {全球网测符合条件数据占比} {花瓣测速符合条件数据占比}
        for env in input_data:
            ws.append([f"{env}(上行)", "睿易国内版本", "睿易海外版本", "全球网测", "花瓣测速"])
            conditions = {
                0.1: "波动在10%以内",
                0.2: "波动在10%和20%之间",
                0.3: "波动大于20%"
            }
            def condition_filter(x, i):
                if i == 0.1:
                    return x <= 0.1
                elif i == 0.2:
                    return 0.1 < x <= 0.2
                else:
                    return x > 0.2
            for i in conditions:
                # print(len(input_data[env]['CN'].keys()))
                ws.append([
                    conditions[i],
                    1.0*len([
                        device
                        for device in input_data[env]['CN']
                        if condition_filter(input_data[env]['CN'][device]['up_fluctuation'], i)    
                    ])/len(input_data[env]['CN'].keys()) if 'CN' in input_data[env] else 0,
                    1.0*len([
                        device
                        for device in input_data[env]['INTL']
                        if condition_filter(input_data[env]['INTL'][device]['up_fluctuation'], i)    
                    ])/len(input_data[env]['INTL'].keys()) if 'INTL' in input_data[env] else 0,
                    1.0*len([
                        device
                        for device in input_data[env]['信通院全球网测']
                        if condition_filter(input_data[env]['信通院全球网测'][device]['up_fluctuation'], i)    
                    ])/len(input_data[env]["信通院全球网测"].keys()) if '信通院全球网测' in input_data[env] else 0,
                    1.0*len([
                        device
                        for device in input_data[env]['花瓣测速']
                        if condition_filter(input_data[env]['花瓣测速'][device]['up_fluctuation'], i)    
                    ])/len(input_data[env]['花瓣测速'].keys()) if '花瓣测速' in input_data[env] else 0
                ])

            ws.append([f"{env}(下行)", "睿易国内版本", "睿易海外版本", "全球网测", "花瓣测速"])
            for i in conditions:
                    
                ws.append([
                    conditions[i],
                    len([
                        device
                        for device in input_data[env]['CN']
                        if condition_filter(input_data[env]['CN'][device]['down_fluctuation'], i)    
                    ])/len(input_data[env]['CN'].keys()) if 'CN' in input_data[env] else 0,
                    len([
                        device
                        for device in input_data[env]['INTL']
                        if condition_filter(input_data[env]['INTL'][device]['down_fluctuation'], i)    
                    ])/len(input_data[env]['INTL'].keys()) if 'INTL' in input_data[env] else 0,
                    len([
                        device
                        for device in input_data[env]['信通院全球网测']
                        if condition_filter(input_data[env]['信通院全球网测'][device]['down_fluctuation'], i)    
                    ])/len(input_data[env]["信通院全球网测"].keys()) if '信通院全球网测' in input_data[env] else 0,
                    len([
                        device
                        for device in input_data[env]['花瓣测速']
                        if condition_filter(input_data[env]['花瓣测速'][device]['down_fluctuation'], i)    
                    ])/len(input_data[env]["花瓣测速"].keys()) if '花瓣测速' in input_data[env] else 0
                ])
        wb.save(os.path.join(file_path, file_name))
    
    def execute(self):
        data = self.transfer_xlsx_to_json(self.serial)
        output = self.analyse_data(data)
        self.output_to_excel(output, self.output_file_path, self.file_name)
        return
               
                    
    def calculate_cv(self, input_list):
        # 计算变异系数
        return statistics.stdev(input_list)/statistics.mean(input_list)
    
    def calculate_iqr(self, input_list):
        # 计算四分位数
        return np.percentile(input_list, [75,25])
    
    def calculate_mad(self, input_list):
        # 计算绝对中位差
        return np.median(np.abs(input_list - np.median(input_list)))
    

