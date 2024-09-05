#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
@DATE: 2024/9/5 21:35
@File: layout_calculator.py
@IDE: pycharm
@Description:
    布局计算器
"""

import cv2.detail
import numpy as np


def judge_layout(
    input_width,
    input_height,
    PHOTO_INTERVAL_W,
    PHOTO_INTERVAL_H,
    LIMIT_BLOCK_W,
    LIMIT_BLOCK_H,
):
    centerBlockHeight_1, centerBlockWidth_1 = (
        input_height,
        input_width,
    )  # 由证件照们组成的一个中心区块（1 代表不转置排列）
    centerBlockHeight_2, centerBlockWidth_2 = (
        input_width,
        input_height,
    )  # 由证件照们组成的一个中心区块（2 代表转置排列）

    # 1.不转置排列的情况下：
    layout_col_no_transpose = 0  # 行
    layout_row_no_transpose = 0  # 列
    for i in range(1, 4):
        centerBlockHeight_temp = input_height * i + PHOTO_INTERVAL_H * (i - 1)
        if centerBlockHeight_temp < LIMIT_BLOCK_H:
            centerBlockHeight_1 = centerBlockHeight_temp
            layout_row_no_transpose = i
        else:
            break
    for j in range(1, 9):
        centerBlockWidth_temp = input_width * j + PHOTO_INTERVAL_W * (j - 1)
        if centerBlockWidth_temp < LIMIT_BLOCK_W:
            centerBlockWidth_1 = centerBlockWidth_temp
            layout_col_no_transpose = j
        else:
            break
    layout_number_no_transpose = layout_row_no_transpose * layout_col_no_transpose

    # 2.转置排列的情况下：
    layout_col_transpose = 0  # 行
    layout_row_transpose = 0  # 列
    for i in range(1, 4):
        centerBlockHeight_temp = input_width * i + PHOTO_INTERVAL_H * (i - 1)
        if centerBlockHeight_temp < LIMIT_BLOCK_H:
            centerBlockHeight_2 = centerBlockHeight_temp
            layout_row_transpose = i
        else:
            break
    for j in range(1, 9):
        centerBlockWidth_temp = input_height * j + PHOTO_INTERVAL_W * (j - 1)
        if centerBlockWidth_temp < LIMIT_BLOCK_W:
            centerBlockWidth_2 = centerBlockWidth_temp
            layout_col_transpose = j
        else:
            break
    layout_number_transpose = layout_row_transpose * layout_col_transpose

    if layout_number_transpose > layout_number_no_transpose:
        layout_mode = (layout_col_transpose, layout_row_transpose, 2)
        return layout_mode, centerBlockWidth_2, centerBlockHeight_2
    else:
        layout_mode = (layout_col_no_transpose, layout_row_no_transpose, 1)
        return layout_mode, centerBlockWidth_1, centerBlockHeight_1


def generate_layout_photo(input_height, input_width):
    # 1.基础参数表
    LAYOUT_WIDTH = 1746
    LAYOUT_HEIGHT = 1180
    PHOTO_INTERVAL_H = 30  # 证件照与证件照之间的垂直距离
    PHOTO_INTERVAL_W = 30  # 证件照与证件照之间的水平距离
    SIDES_INTERVAL_H = 50  # 证件照与画布边缘的垂直距离
    SIDES_INTERVAL_W = 70  # 证件照与画布边缘的水平距离
    LIMIT_BLOCK_W = LAYOUT_WIDTH - 2 * SIDES_INTERVAL_W
    LIMIT_BLOCK_H = LAYOUT_HEIGHT - 2 * SIDES_INTERVAL_H

    # 2.创建一个 1180x1746 的空白画布
    white_background = np.zeros([LAYOUT_HEIGHT, LAYOUT_WIDTH, 3], np.uint8)
    white_background.fill(255)

    # 3.计算照片的 layout（列、行、横竖朝向）,证件照组成的中心区块的分辨率
    layout_mode, centerBlockWidth, centerBlockHeight = judge_layout(
        input_width,
        input_height,
        PHOTO_INTERVAL_W,
        PHOTO_INTERVAL_H,
        LIMIT_BLOCK_W,
        LIMIT_BLOCK_H,
    )
    # 4.开始排列组合
    x11 = (LAYOUT_WIDTH - centerBlockWidth) // 2
    y11 = (LAYOUT_HEIGHT - centerBlockHeight) // 2
    typography_arr = []
    typography_rotate = False
    if layout_mode[2] == 2:
        input_height, input_width = input_width, input_height
        typography_rotate = True

    for j in range(layout_mode[1]):
        for i in range(layout_mode[0]):
            xi = x11 + i * input_width + i * PHOTO_INTERVAL_W
            yi = y11 + j * input_height + j * PHOTO_INTERVAL_H
            typography_arr.append([xi, yi])

    return typography_arr, typography_rotate


def generate_layout_image(
    input_image, typography_arr, typography_rotate, width=295, height=413
):
    LAYOUT_WIDTH = 1746
    LAYOUT_HEIGHT = 1180
    white_background = np.zeros([LAYOUT_HEIGHT, LAYOUT_WIDTH, 3], np.uint8)
    white_background.fill(255)
    if input_image.shape[0] != height:
        input_image = cv2.resize(input_image, (width, height))
    if typography_rotate:
        input_image = cv2.transpose(input_image)
        height, width = width, height
    for arr in typography_arr:
        locate_x, locate_y = arr[0], arr[1]
        white_background[locate_y : locate_y + height, locate_x : locate_x + width] = (
            input_image
        )

    return white_background
