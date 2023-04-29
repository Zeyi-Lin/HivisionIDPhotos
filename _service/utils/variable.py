"""
@author: cuny
@file: variable.py
@time: 2022/7/14 15:55
@description: 
存储一些全局引用变量
"""
import os
local_path = os.path.dirname(__file__)  # 当前文件夹路径
config_path = os.path.join(local_path, "config")
func_version = os.environ.get("SCF_FUNCTIONVERSION")  # 函数运行情况，本地为None，云端测试版为$LATEST，其余我们认为是云端线上版
