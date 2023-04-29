"""
@author: cuny
@file: GrindSkin.py
@time: 2022/7/2 14:44
@description: 
磨皮算法
"""
import cv2
import numpy as np


def grindSkin(src, grindDegree: int = 3, detailDegree: int = 1, strength: int = 9):
    """
    Dest =(Src * (100 - Opacity) + (Src + 2 * GaussBlur(EPFFilter(Src) - Src)) * Opacity) /100
    人像磨皮方案，后续会考虑使用一些皮肤区域检测算法来实现仅皮肤区域磨皮，增加算法的精细程度——或者使用人脸关键点
    https://www.cnblogs.com/Imageshop/p/4709710.html
    Args:
        src: 原图
        grindDegree: 磨皮程度调节参数
        detailDegree: 细节程度调节参数
        strength: 融合程度，作为磨皮强度（0 - 10）

    Returns:
        磨皮后的图像
    """
    if strength <= 0:
        return src
    dst = src.copy()
    opacity = min(10., strength) / 10.
    dx = grindDegree * 5  # 双边滤波参数之一
    fc = grindDegree * 12.5  # 双边滤波参数之一
    temp1 = cv2.bilateralFilter(src[:, :, :3], dx, fc, fc)
    temp2 = cv2.subtract(temp1, src[:, :, :3])
    temp3 = cv2.GaussianBlur(temp2, (2 * detailDegree - 1, 2 * detailDegree - 1), 0)
    temp4 = cv2.add(cv2.add(temp3, temp3), src[:, :, :3])
    dst[:, :, :3] = cv2.addWeighted(temp4, opacity, src[:, :, :3], 1 - opacity, 0.0)
    return dst


if __name__ == "__main__":
    input_image = cv2.imread("test_image/7.jpg")
    output_image = grindSkin(src=input_image)
    cv2.imwrite("grindSkinCompare.png", np.hstack((input_image, output_image)))
