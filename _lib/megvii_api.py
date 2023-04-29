"""
@author: cuny
@file: megvii_api.py
@time: 2022/7/29 19:56
@description: 
整合旷视科技的人像相关api
附加材料：
1. 86点人脸关键点介绍：https://console.faceplusplus.com.cn/documents/5671270
2. 106点人脸关键点介绍：https://console.faceplusplus.com.cn/documents/13207408
3. 人脸检测API文档：https://console.faceplusplus.com.cn/documents/4888373
"""
import json
import base64
import requests
import numpy as np
from .__config import MEGVII_CONFIG_PATH


class MEGVIIFace83(object):
    FACE_POINTS = list(range(19, 83))  # 人脸内部轮廓点索引
    MOUTH_POINTS = list(range(37, 55))  # 嘴巴点索引
    RIGHT_BROW_POINTS = list(range(75, 83))  # 右眉毛索引
    LEFT_BROW_POINTS = list(range(29, 37))  # 左眉毛索引
    RIGHT_EYE_POINTS = list(range(65, 75))  # 右眼索引
    LEFT_EYE_POINTS = list(range(19, 29))  # 左眼索引
    NOSE_POINTS = list(range(55, 65))  # 鼻子索引
    JAW_POINTS = list(range(0, 19))  # 下巴索引


def megvii_face_detector(imageBytes: bytes, user=None):
    """
    旷视科技的人脸关键点检测api
    todo 做好一些异常捕捉机制
    Args:
        imageBytes: 输入的图像，比特流
        user: 请求用户配置，支持[]方式访问accessKey和accessSecret

    Returns:
        人脸数量、人脸位置、关键点信息(landmark, (x, y))、人脸姿态。
            其中关键点信息会被整理成矩阵形式（对于每一张脸而言）。
        事实上最终的人脸位置、关键点信息和人脸姿态都会是列表，列表里的每个元素代表一个人脸的信息，这是一一对应的
            比如人脸位置[0]和关键点信息[0]对应的人脸是同一张
            如果人脸数量为0，其余返回值为[]
    """
    if user is None:
        accessFile = json.load(open(MEGVII_CONFIG_PATH, 'rb'))
        data = {
            "api_key": accessFile["accessKey"],
            "api_secret": accessFile["accessSecret"],
            "return_landmark": 1,
            "return_attributes": "headpose"
        }
    else:
        data = {
            "api_key": user["accessKey"],
            "api_secret": user["accessSecret"],
            "return_landmark": 1,
            "return_attributes": "headpose"
        }
    data["image_base64"] = base64.b64encode(imageBytes)
    url = "https://api-cn.faceplusplus.com/facepp/v3/detect"
    response = requests.post(url, data=data, proxies={"http": None, "https": None})
    responseJson = response.json()
    face_num = responseJson["face_num"]
    faces = responseJson["faces"]
    face_rectangle = [x["face_rectangle"] for x in faces]
    landmarks = [np.mat([[y[k]['x'], y[k]['y']]for k in y]) for y in [x["landmark"] for x in faces]]
    headpose = [x["attributes"]["headpose"] for x in faces]
    return face_num, face_rectangle, landmarks, headpose
