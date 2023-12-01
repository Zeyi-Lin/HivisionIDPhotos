"""
@author: cuny
@file: EulerX.py
@time: 2022/4/1 13:54
@description: 
寻找三维z轴旋转角roll,实现：
1. 输入一张三通道图片（四通道、单通道将默认转为三通道）
2. 输出人脸在x轴的转角roll，顺时针为正方向，角度制
"""
import cv2
import numpy as np
from math import asin, pi  # -pi/2 ~ pi/2


# 获得人脸的关键点信息
def get_facePoints(src: np.ndarray, fd68):
    if len(src.shape) == 2:
        src = cv2.cvtColor(src, cv2.COLOR_GRAY2BGR)
    elif src.shape[2] == 4:
        src = cv2.cvtColor(src, cv2.COLOR_BGRA2BGR)
    status, dets, landmarks, _ = fd68.facePointsEuler(src)

    if status == 0:
        return 0, None, None
    elif status == 2:
        return 2, None, None
    else:
        return 1, dets, np.fliplr(landmarks)


def eulerZ(landmark: np.matrix):
    # 我们规定顺时针为正方向
    def get_pi_2(r):
        pi_2 = pi / 2.
        if r >= 0.0:
            return pi_2
        else:
            return -pi_2
    orbit_points = np.array([[landmark[21, 0], landmark[21, 1]], [landmark[71, 0], landmark[71, 1]],
                                   [landmark[25, 0], landmark[25, 1]], [landmark[67, 0], landmark[67, 1]]])
    # [[cos  a],[sin a],[point_x],[point_y]]
    # 前面两项是有关直线与Y正半轴夹角a的三角函数，所以对于眼睛部分来讲sin a应该接近1
    # "我可以认为"cv2.fitLine的y轴正方向为竖直向下，且生成的拟合直线的方向为从起点指向终点
    # 与y轴的夹角为y轴夹角与直线方向的夹角，方向从y指向直线，逆时针为正方向
    # 所以最后对于鼻梁的计算结果需要取个负号
    orbit_line = cv2.fitLine(orbit_points, cv2.DIST_L2, 0, 0.01, 0.01)
    orbit_a = asin(orbit_line[1][0])
    nose_points = np.array([[landmark[55, 0], landmark[55, 1]], [landmark[69, 0], landmark[69, 1]]])
    nose_line = cv2.fitLine(nose_points, cv2.DIST_L2, 0, 0.01, 0.01)
    nose_a = asin(nose_line[1][0])
    return (orbit_a + nose_a) * (180.0 / (2 * pi))
