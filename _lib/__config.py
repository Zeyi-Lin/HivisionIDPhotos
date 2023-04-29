"""
@author: cuny
@file: __config.py
@time: 2022/7/21 13:46
@description: 
存储一些_lib文件夹下的变量
"""
import os
from _service import func_version
local_path_lib = os.path.dirname(__file__)
# 阿里云的api
HUMAN_MATTING_CONFIG_PATH = os.path.join(local_path_lib, "config/aliyun-human-matting-api.json")
# 旷视API的文件路径
MEGVII_CONFIG_PATH = os.path.join(local_path_lib, "config/megvii-face-plus-api.json")
if func_version is None:  # 本地
    # 自训练modnet模型依赖于HY-sdk，目前暂时不整合进_lib，仅仅是将模型和模型路径放于此
    HY_HUMAN_MATTING_WEIGHTS_PATH = os.path.join(local_path_lib, "weights/huanying_human_matting02.onnx")  # 人像抠图
    HY_HEAD_MATTING_WEIGHTS_PATH = os.path.join(local_path_lib, "weights/huanying_head3.onnx")  # 人头抠图
    HY_HEADNECK_MATTING_WEIGHTS_PATH = os.path.join(local_path_lib, "weights/huanying_headneck3.onnx")  # 脖子抠图
    # dlib关键点检测模型
    FACE_PREDICTOR_68_PATH = os.path.join(local_path_lib, "weights/shape_predictor_68_face_landmarks.dat")
else:
    # 自训练modnet模型依赖于HY-sdk，对于云函数版本，会引用层中路径
    HY_HUMAN_MATTING_WEIGHTS_PATH = "/opt/huanying_human_matting02.onnx"  # 人像抠图
    HY_HEAD_MATTING_WEIGHTS_PATH = "/opt/huanying_head3.onnx"  # 人头抠图
    HY_HEADNECK_MATTING_WEIGHTS_PATH = "/opt/huanying_headneck3.onnx"  # 脖子抠图
    # dlib关键点检测模型
    FACE_PREDICTOR_68_PATH = "/opt/shape_predictor_68_face_landmarks.dat"

