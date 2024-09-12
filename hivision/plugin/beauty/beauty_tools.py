"""
@author: cuny
@file: MakeBeautiful.py
@time: 2022/7/7 20:23
@description: 
美颜工具集合文件，作为暴露在外的插件接口
"""

from .grind_skin import grindSkin
from .whitening import MakeWhiter
from .thin_face import thinFace
import numpy as np


def BeautyTools(
    input_image: np.ndarray,
    landmark,
    thinStrength: int,
    thinPlace: int,
    grindStrength: int,
    whiterStrength: int,
) -> np.ndarray:
    """
    美颜工具的接口函数，用于实现美颜效果
    Args:
        input_image: 输入的图像
        landmark: 瘦脸需要的人脸关键点信息，为fd68返回的第二个参数
        thinStrength: 瘦脸强度，为0-10（如果更高其实也没什么问题），当强度为0或者更低时，则不瘦脸
        thinPlace: 选择瘦脸区域，为0-2之间的值，越大瘦脸的点越靠下
        grindStrength: 磨皮强度，为0-10（如果更高其实也没什么问题），当强度为0或者更低时，则不磨皮
        whiterStrength: 美白强度，为0-10（如果更高其实也没什么问题），当强度为0或者更低时，则不美白
    Returns:
        output_image 输出图像
    """
    try:
        _, _, _ = input_image.shape
    except ValueError:
        raise TypeError("输入图像必须为3通道或者4通道!")
    # 三通道或者四通道图像
    # 首先进行瘦脸
    input_image = thinFace(
        input_image, landmark, place=thinPlace, strength=thinStrength
    )
    # 其次进行磨皮
    input_image = grindSkin(src=input_image, strength=grindStrength)
    # 最后进行美白
    makeWhiter = MakeWhiter()
    input_image = makeWhiter.run(input_image, strength=whiterStrength)
    return input_image
