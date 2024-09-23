#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
@DATE: 2024/9/5 20:02
@File: photo_adjuster.py
@IDE: pycharm
@Description:
    证件照调整
"""
from .context import Context
from .layout_calculator import generate_layout_array
import hivision.creator.utils as U
import numpy as np
import math
import cv2


def adjust_photo(ctx: Context):
    # Step1. 准备人脸参数
    face_rect = ctx.face["rectangle"]
    standard_size = ctx.params.size
    params = ctx.params
    x, y = face_rect[0], face_rect[1]
    w, h = face_rect[2], face_rect[3]
    height, width = ctx.matting_image.shape[:2]
    width_height_ratio = standard_size[0] / standard_size[1]
    # Step2. 计算高级参数
    face_center = (x + w / 2, y + h / 2)  # 面部中心坐标
    face_measure = w * h  # 面部面积
    crop_measure = (
        face_measure / params.head_measure_ratio
    )  # 裁剪框面积：为面部面积的 5 倍
    resize_ratio = crop_measure / (standard_size[0] * standard_size[1])  # 裁剪框缩放率
    resize_ratio_single = math.sqrt(
        resize_ratio
    )  # 长和宽的缩放率（resize_ratio 的开方）
    crop_size = (
        int(standard_size[0] * resize_ratio_single),
        int(standard_size[1] * resize_ratio_single),
    )  # 裁剪框大小

    # 裁剪框的定位信息
    x1 = int(face_center[0] - crop_size[1] / 2)
    y1 = int(face_center[1] - crop_size[0] * params.head_height_ratio)
    y2 = y1 + crop_size[0]
    x2 = x1 + crop_size[1]

    # Step3, 裁剪框的调整
    cut_image = IDphotos_cut(x1, y1, x2, y2, ctx.matting_image)
    cut_image = cv2.resize(cut_image, (crop_size[1], crop_size[0]))
    y_top, y_bottom, x_left, x_right = U.get_box(
        cut_image.astype(np.uint8), model=2, correction_factor=0
    )  # 得到 cut_image 中人像的上下左右距离信息

    # Step5. 判定 cut_image 中的人像是否处于合理的位置，若不合理，则处理数据以便之后调整位置
    # 检测人像与裁剪框左边或右边是否存在空隙
    if x_left > 0 or x_right > 0:
        status_left_right = 1
        cut_value_top = int(
            ((x_left + x_right) * width_height_ratio) / 2
        )  # 减去左右，为了保持比例，上下也要相应减少 cut_value_top
    else:
        status_left_right = 0
        cut_value_top = 0

    """
        检测人头顶与照片的顶部是否在合适的距离内：
        - status==0: 距离合适，无需移动
        - status=1: 距离过大，人像应向上移动
        - status=2: 距离过小，人像应向下移动
    """
    status_top, move_value = U.detect_distance(
        y_top - cut_value_top,
        crop_size[0],
        max=params.head_top_range[0],
        min=params.head_top_range[1],
    )

    # Step6. 对照片的第二轮裁剪
    if status_left_right == 0 and status_top == 0:
        result_image = cut_image
    else:
        result_image = IDphotos_cut(
            x1 + x_left,
            y1 + cut_value_top + status_top * move_value,
            x2 - x_right,
            y2 - cut_value_top + status_top * move_value,
            ctx.matting_image,
        )

    # 换装参数准备
    relative_x = x - (x1 + x_left)
    relative_y = y - (y1 + cut_value_top + status_top * move_value)

    # Step7. 当照片底部存在空隙时，下拉至底部
    result_image, y_high = move(result_image.astype(np.uint8))
    relative_y = relative_y + y_high  # 更新换装参数

    # Step8. 标准照与高清照转换
    result_image_standard = standard_photo_resize(result_image, standard_size)
    result_image_hd, resize_ratio_max = resize_image_by_min(
        result_image, esp=max(600, standard_size[1])
    )

    # Step9. 参数准备 - 为换装服务
    clothing_params = {
        "relative_x": relative_x * resize_ratio_max,
        "relative_y": relative_y * resize_ratio_max,
        "w": w * resize_ratio_max,
        "h": h * resize_ratio_max,
    }

    # Step7. 排版照参数获取
    typography_arr, typography_rotate = generate_layout_array(
        input_height=standard_size[0], input_width=standard_size[1]
    )

    return (
        result_image_hd,
        result_image_standard,
        clothing_params,
        {
            "arr": typography_arr,
            "rotate": typography_rotate,
        },
    )


def IDphotos_cut(x1, y1, x2, y2, img):
    """
    在图片上进行滑动裁剪，输入输出为
    输入：一张图片 img，和裁剪框信息 (x1,x2,y1,y2)
    输出：裁剪好的图片，然后裁剪框超出了图像范围，那么将用 0 矩阵补位
    ------------------------------------
    x:裁剪框左上的横坐标
    y:裁剪框左上的纵坐标
    x2:裁剪框右下的横坐标
    y2:裁剪框右下的纵坐标
    crop_size:裁剪框大小
    img:裁剪图像（numpy.array）
    output_path:裁剪图片的输出路径
    ------------------------------------
    """

    crop_size = (y2 - y1, x2 - x1)
    """
    ------------------------------------
    temp_x_1:裁剪框左边超出图像部分
    temp_y_1:裁剪框上边超出图像部分
    temp_x_2:裁剪框右边超出图像部分
    temp_y_2:裁剪框下边超出图像部分
    ------------------------------------
    """
    temp_x_1 = 0
    temp_y_1 = 0
    temp_x_2 = 0
    temp_y_2 = 0

    if y1 < 0:
        temp_y_1 = abs(y1)
        y1 = 0
    if y2 > img.shape[0]:
        temp_y_2 = y2
        y2 = img.shape[0]
        temp_y_2 = temp_y_2 - y2

    if x1 < 0:
        temp_x_1 = abs(x1)
        x1 = 0
    if x2 > img.shape[1]:
        temp_x_2 = x2
        x2 = img.shape[1]
        temp_x_2 = temp_x_2 - x2

    # 生成一张全透明背景
    background_bgr = np.full((crop_size[0], crop_size[1]), 255, dtype=np.uint8)
    background_a = np.full((crop_size[0], crop_size[1]), 0, dtype=np.uint8)
    background = cv2.merge(
        (background_bgr, background_bgr, background_bgr, background_a)
    )

    background[
        temp_y_1 : crop_size[0] - temp_y_2, temp_x_1 : crop_size[1] - temp_x_2
    ] = img[y1:y2, x1:x2]

    return background


def move(input_image):
    """
    裁剪主函数，输入一张 png 图像，该图像周围是透明的
    """
    png_img = input_image  # 获取图像

    height, width, channels = png_img.shape  # 高 y、宽 x
    y_low, y_high, _, _ = U.get_box(png_img, model=2)  # for 循环
    base = np.zeros((y_high, width, channels), dtype=np.uint8)  # for 循环
    png_img = png_img[0 : height - y_high, :, :]  # for 循环
    png_img = np.concatenate((base, png_img), axis=0)
    return png_img, y_high


def standard_photo_resize(input_image: np.array, size):
    """
    input_image: 输入图像，即高清照
    size: 标准照的尺寸
    """
    resize_ratio = input_image.shape[0] / size[0]
    resize_item = int(round(input_image.shape[0] / size[0]))
    if resize_ratio >= 2:
        for i in range(resize_item - 1):
            if i == 0:
                result_image = cv2.resize(
                    input_image,
                    (size[1] * (resize_item - i - 1), size[0] * (resize_item - i - 1)),
                    interpolation=cv2.INTER_AREA,
                )
            else:
                result_image = cv2.resize(
                    result_image,
                    (size[1] * (resize_item - i - 1), size[0] * (resize_item - i - 1)),
                    interpolation=cv2.INTER_AREA,
                )
    else:
        result_image = cv2.resize(
            input_image, (size[1], size[0]), interpolation=cv2.INTER_AREA
        )

    return result_image


def resize_image_by_min(input_image, esp=600):
    """
    将图像缩放为最短边至少为 esp 的图像。
    :param input_image: 输入图像（OpenCV 矩阵）
    :param esp: 缩放后的最短边长
    :return: 缩放后的图像，缩放倍率
    """
    height, width = input_image.shape[0], input_image.shape[1]
    min_border = min(height, width)
    if min_border < esp:
        if height >= width:
            new_width = esp
            new_height = height * esp // width
        else:
            new_height = esp
            new_width = width * esp // height

        return (
            cv2.resize(
                input_image, (new_width, new_height), interpolation=cv2.INTER_AREA
            ),
            new_height / height,
        )

    else:
        return input_image, 1
