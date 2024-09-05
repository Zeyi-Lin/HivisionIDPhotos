#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
@DATE: 2024/9/5 19:25
@File: utils.py
@IDE: pycharm
@Description:
    通用图像处理工具
"""
import cv2
import numpy as np


def resize_image_esp(input_image, esp=2000):
    """
    输入：
    input_path：numpy 图片
    esp：限制的最大边长
    """
    # resize 函数=>可以让原图压缩到最大边为 esp 的尺寸 (不改变比例)
    width = input_image.shape[0]

    length = input_image.shape[1]
    max_num = max(width, length)

    if max_num > esp:
        print("Image resizing...")
        if width == max_num:
            length = int((esp / width) * length)
            width = esp

        else:
            width = int((esp / length) * width)
            length = esp
        print(length, width)
        im_resize = cv2.resize(
            input_image, (length, width), interpolation=cv2.INTER_AREA
        )
        return im_resize
    else:
        return input_image


def get_box(
    image: np.ndarray,
    model: int = 1,
    correction_factor=None,
    thresh: int = 127,
):
    """
    本函数能够实现输入一张四通道图像，返回图像中最大连续非透明面积的区域的矩形坐标
    本函数将采用 opencv 内置函数来解析整个图像的 mask，并提供一些参数，用于读取图像的位置信息
    Args:
        image: 四通道矩阵图像
        model: 返回值模式
        correction_factor: 提供一些边缘扩张接口，输入格式为 list 或者 int:[up, down, left, right]。
                    举个例子，假设我们希望剪切出的矩形框左边能够偏左 1 个像素，则输入 [0, 0, 1, 0]；
                        如果希望右边偏右 1 个像素，则输入 [0, 0, 0, 1]
                    如果输入为 int，则默认只会对左右两边做拓展，比如输入 2，则和 [0, 0, 2, 2] 是等效的
        thresh: 二值化阈值，为了保持一些羽化效果，thresh 必须要小
    Returns:
        model 为 1 时，将会返回切割出的矩形框的四个坐标点信息
        model 为 2 时，将会返回矩形框四边相距于原图四边的距离
    """
    # ------------ 数据格式规范部分 -------------- #
    # 输入必须为四通道
    if correction_factor is None:
        correction_factor = [0, 0, 0, 0]
    if not isinstance(image, np.ndarray) or len(cv2.split(image)) != 4:
        raise TypeError("输入的图像必须为四通道 np.ndarray 类型矩阵！")
    # correction_factor 规范化
    if isinstance(correction_factor, int):
        correction_factor = [0, 0, correction_factor, correction_factor]
    elif not isinstance(correction_factor, list):
        raise TypeError("correction_factor 必须为 int 或者 list 类型！")
    # ------------ 数据格式规范完毕 -------------- #
    # 分离 mask
    _, _, _, mask = cv2.split(image)
    # mask 二值化处理
    _, mask = cv2.threshold(mask, thresh=thresh, maxval=255, type=0)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    temp = np.ones(image.shape, np.uint8) * 255
    cv2.drawContours(temp, contours, -1, (0, 0, 255), -1)
    contours_area = []
    for cnt in contours:
        contours_area.append(cv2.contourArea(cnt))
    idx = contours_area.index(max(contours_area))
    x, y, w, h = cv2.boundingRect(contours[idx])  # 框出图像
    # ------------ 开始输出数据 -------------- #
    height, width, _ = image.shape
    y_up = y - correction_factor[0] if y - correction_factor[0] >= 0 else 0
    y_down = (
        y + h + correction_factor[1]
        if y + h + correction_factor[1] < height
        else height - 1
    )
    x_left = x - correction_factor[2] if x - correction_factor[2] >= 0 else 0
    x_right = (
        x + w + correction_factor[3]
        if x + w + correction_factor[3] < width
        else width - 1
    )
    if model == 1:
        # model=1，将会返回切割出的矩形框的四个坐标点信息
        return [y_up, y_down, x_left, x_right]
    elif model == 2:
        # model=2, 将会返回矩形框四边相距于原图四边的距离
        return [y_up, height - y_down, x_left, width - x_right]
    else:
        raise EOFError("请选择正确的模式！")


def detect_distance(value, crop_height, max=0.06, min=0.04):
    """
    检测人头顶与照片顶部的距离是否在适当范围内。
    输入：与顶部的差值
    输出：(status, move_value)
    status=0 不动
    status=1 人脸应向上移动（裁剪框向下移动）
    status-2 人脸应向下移动（裁剪框向上移动）
    ---------------------------------------
    value：头顶与照片顶部的距离
    crop_height: 裁剪框的高度
    max: 距离的最大值
    min: 距离的最小值
    ---------------------------------------
    """
    value = value / crop_height  # 头顶往上的像素占图像的比例
    if min <= value <= max:
        return 0, 0
    elif value > max:
        # 头顶往上的像素比例高于 max
        move_value = value - max
        move_value = int(move_value * crop_height)
        # print("上移{}".format(move_value))
        return 1, move_value
    else:
        # 头顶往上的像素比例低于 min
        move_value = min - value
        move_value = int(move_value * crop_height)
        # print("下移{}".format(move_value))
        return -1, move_value
