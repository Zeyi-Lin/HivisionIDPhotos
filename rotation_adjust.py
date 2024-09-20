"""
人脸旋转矫正模块

本模块提供了用于旋转图像的函数，主要用于人脸旋转矫正。
包含了处理3通道和4通道图像的旋转函数。
"""

import cv2
import numpy as np


def rotate_bound(image: np.ndarray, angle: float, center=None):
    """
    旋转图像而不损失信息的函数

    Args:
        image (np.ndarray): 输入图像，3通道numpy数组
        angle (float): 旋转角度（度）
        center (tuple, optional): 旋转中心坐标，默认为图像中心

    Returns:
        tuple: 包含以下元素的元组：
            - rotated (np.ndarray): 旋转后的图像
            - cos (float): 旋转角度的余弦值
            - sin (float): 旋转角度的正弦值
            - dW (int): 宽度变化量
            - dH (int): 高度变化量
    """
    (h, w) = image.shape[:2]
    if center is None:
        (cX, cY) = (w / 2, h / 2)
    else:
        (cX, cY) = center

    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    rotated = cv2.warpAffine(image, M, (nW, nH))

    # 计算偏移量
    dW = nW - w
    dH = nH - h

    return rotated, cos, sin, dW, dH


def rotate_bound_4channels(image: np.ndarray, a: np.ndarray, angle: float, center=None):
    """
    旋转4通道图像的函数

    这是rotate_bound函数的4通道版本，可以同时处理RGB图像和其对应的alpha通道。

    Args:
        image (np.ndarray): 输入的3通道RGB图像
        a (np.ndarray): 输入图像的alpha通道
        angle (float): 旋转角度（度）
        center (tuple, optional): 旋转中心坐标，默认为图像中心

    Returns:
        tuple: 包含以下元素的元组：
            - input_image (np.ndarray): 旋转后的3通道RGB图像
            - result_image (np.ndarray): 旋转后的4通道RGBA图像
            - cos (float): 旋转角度的余弦值
            - sin (float): 旋转角度的正弦值
            - dW (int): 宽度变化量
            - dH (int): 高度变化量
    """
    input_image, cos, sin, dW, dH = rotate_bound(image, angle, center)
    new_a, _, _, _, _ = rotate_bound(a, angle, center)  # 对alpha通道进行旋转
    b, g, r = cv2.split(input_image)
    result_image = cv2.merge((b, g, r, new_a))  # 合并旋转后的RGB通道和alpha通道

    return input_image, result_image, cos, sin, dW, dH
