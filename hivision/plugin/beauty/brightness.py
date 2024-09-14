import cv2
import numpy as np


def adjust_brightness(image, brightness_factor):
    """
    调整图像的亮度。

    参数:
    image (numpy.ndarray): 输入的图像数组。
    brightness_factor (float): 亮度调整因子。大于1增加亮度，小于1降低亮度。

    返回:
    numpy.ndarray: 调整亮度后的图像。
    """
    # 将图像转换为HSV颜色空间
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 分离HSV通道
    h, s, v = cv2.split(hsv)

    # 调整V通道（亮度）
    v = np.clip(v * brightness_factor, 0, 255).astype(np.uint8)

    # 合并通道
    hsv = cv2.merge((h, s, v))

    # 转换回BGR颜色空间
    adjusted = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    return adjusted
