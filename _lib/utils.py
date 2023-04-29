"""
@author: cuny
@file: utils.py
@time: 2022/7/30 14:00
@description:
保存一些辅助调试用的工具函数，方便校验一些处理结果
"""
import cv2
import numpy as np


def draw_face_points(image: np.ndarray, points, radius: int = 3, imagePath: str = None, drawNun: bool = False):
    """
    本函数用于画出人脸关键点信息，核心是"画点"，事实上只要参数正确都可以。
    Args:
        image: 图像矩阵,不可为灰度图
        points: 图像的关键点信息，支持两种格式输入（list或者matrix），其中，我们默认points内部每个元素为（x，y）
        radius: 画出点的直径（px）
        imagePath: 图像保存路径，相对于主文件而言的路径
        drawNun: 是否要画数字
    Returns:
        imageWithPoints，必定为三通道形式
        如果imagePath不为None，则会创建相应的图像文件
    """
    if isinstance(points, np.matrix):
        points = points.tolist()
    assert isinstance(points, list), "points必须为list或者matrix"
    imageWithPoints = image[:, :, :3]
    for idx, p in enumerate(points):
        imageWithPoints = cv2.circle(imageWithPoints, (p[0], p[1]), radius, (0, 0, 255), -1)
        font = cv2.FONT_HERSHEY_SIMPLEX
        if drawNun is True:
            cv2.putText(imageWithPoints, str(idx + 1), p, font, 0.8, (0, 0, 255), 1, cv2.LINE_AA)
    if imagePath is not None:
        cv2.imread(imagePath, imageWithPoints)
    return imageWithPoints


class UserAPIConfig(object):
    pass
