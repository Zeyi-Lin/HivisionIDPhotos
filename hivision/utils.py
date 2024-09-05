#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
@DATE: 2024/9/5 21:52
@File: utils.py
@IDE: pycharm
@Description:
    hivision提供的工具函数
"""
from PIL import Image
import io
import numpy as np
import cv2
import base64


def resize_image_to_kb(input_image, output_image_path, target_size_kb):
    """
    Resize an image to a target size in KB.
    将图像调整大小至目标文件大小（KB）。

    :param input_image_path: Path to the input image. 输入图像的路径。
    :param output_image_path: Path to save the resized image. 保存调整大小后的图像的路径。
    :param target_size_kb: Target size in KB. 目标文件大小（KB）。

    Example:
    resize_image_to_kb('input_image.jpg', 'output_image.jpg', 50)
    """

    if isinstance(input_image, np.ndarray):
        img = Image.fromarray(input_image)
    elif isinstance(input_image, Image.Image):
        img = input_image
    else:
        raise ValueError("input_image must be a NumPy array or PIL Image.")

    # Convert image to RGB mode if it's not
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Initial quality value
    quality = 95

    while True:
        # Create a BytesIO object to hold the image data in memory
        img_byte_arr = io.BytesIO()

        # Save the image to the BytesIO object with the current quality
        img.save(img_byte_arr, format="JPEG", quality=quality)

        # Get the size of the image in KB
        img_size_kb = len(img_byte_arr.getvalue()) / 1024

        # Check if the image size is within the target size
        if img_size_kb <= target_size_kb or quality == 1:
            # If the image is smaller than the target size, add padding
            if img_size_kb < target_size_kb:
                padding_size = int(
                    (target_size_kb * 1024) - len(img_byte_arr.getvalue())
                )
                padding = b"\x00" * padding_size
                img_byte_arr.write(padding)

            # Save the image to the output path
            with open(output_image_path, "wb") as f:
                f.write(img_byte_arr.getvalue())
            break

        # Reduce the quality if the image is still too large
        quality -= 5

        # Ensure quality does not go below 1
        if quality < 1:
            quality = 1


def resize_image_to_kb_base64(input_image, target_size_kb):
    """
    Resize an image to a target size in KB and return it as a base64 encoded string.
    将图像调整大小至目标文件大小（KB）并返回base64编码的字符串。

    :param input_image: Input image as a NumPy array or PIL Image. 输入图像，可以是NumPy数组或PIL图像。
    :param target_size_kb: Target size in KB. 目标文件大小（KB）。

    :return: Base64 encoded string of the resized image. 调整大小后的图像的base64编码字符串。
    """

    if isinstance(input_image, np.ndarray):
        img = Image.fromarray(input_image)
    elif isinstance(input_image, Image.Image):
        img = input_image
    else:
        raise ValueError("input_image must be a NumPy array or PIL Image.")

    # Convert image to RGB mode if it's not
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Initial quality value
    quality = 95

    while True:
        # Create a BytesIO object to hold the image data in memory
        img_byte_arr = io.BytesIO()

        # Save the image to the BytesIO object with the current quality
        img.save(img_byte_arr, format="JPEG", quality=quality)

        # Get the size of the image in KB
        img_size_kb = len(img_byte_arr.getvalue()) / 1024

        # Check if the image size is within the target size
        if img_size_kb <= target_size_kb or quality == 1:
            # If the image is smaller than the target size, add padding
            if img_size_kb < target_size_kb:
                padding_size = int(
                    (target_size_kb * 1024) - len(img_byte_arr.getvalue())
                )
                padding = b"\x00" * padding_size
                img_byte_arr.write(padding)

            # Encode the image data to base64
            img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
            return img_base64

        # Reduce the quality if the image is still too large
        quality -= 5

        # Ensure quality does not go below 1
        if quality < 1:
            quality = 1


def numpy_2_base64(img: np.ndarray):
    _, buffer = cv2.imencode(".png", img)
    base64_image = base64.b64encode(buffer).decode("utf-8")

    return base64_image


def save_numpy_image(numpy_img, file_path):
    # 检查数组的形状
    if numpy_img.shape[2] == 4:
        # 将 BGR 转换为 RGB，并保留透明通道
        rgb_img = np.concatenate(
            (np.flip(numpy_img[:, :, :3], axis=-1), numpy_img[:, :, 3:]), axis=-1
        ).astype(np.uint8)
        img = Image.fromarray(rgb_img, mode="RGBA")
    else:
        # 将 BGR 转换为 RGB
        rgb_img = np.flip(numpy_img, axis=-1).astype(np.uint8)
        img = Image.fromarray(rgb_img, mode="RGB")

    img.save(file_path)


def numpy_to_bytes(numpy_img):
    img = Image.fromarray(numpy_img)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return img_byte_arr


def hex_to_rgb(value):
    value = value.lstrip("#")
    length = len(value)
    return tuple(
        int(value[i : i + length // 3], 16) for i in range(0, length, length // 3)
    )


def generate_gradient(start_color, width, height, mode="updown"):
    # 定义背景颜色
    end_color = (255, 255, 255)  # 白色

    # 创建一个空白图像
    r_out = np.zeros((height, width), dtype=int)
    g_out = np.zeros((height, width), dtype=int)
    b_out = np.zeros((height, width), dtype=int)

    if mode == "updown":
        # 生成上下渐变色
        for y in range(height):
            r = int(
                (y / height) * end_color[0] + ((height - y) / height) * start_color[0]
            )
            g = int(
                (y / height) * end_color[1] + ((height - y) / height) * start_color[1]
            )
            b = int(
                (y / height) * end_color[2] + ((height - y) / height) * start_color[2]
            )
            r_out[y, :] = r
            g_out[y, :] = g
            b_out[y, :] = b

    else:
        # 生成中心渐变色
        img = np.zeros((height, width, 3))
        # 定义椭圆中心和半径
        center = (width // 2, height // 2)
        end_axies = max(height, width)
        # 定义渐变色
        end_color = (255, 255, 255)
        # 绘制椭圆
        for y in range(end_axies):
            axes = (end_axies - y, end_axies - y)
            r = int(
                (y / end_axies) * end_color[0]
                + ((end_axies - y) / end_axies) * start_color[0]
            )
            g = int(
                (y / end_axies) * end_color[1]
                + ((end_axies - y) / end_axies) * start_color[1]
            )
            b = int(
                (y / end_axies) * end_color[2]
                + ((end_axies - y) / end_axies) * start_color[2]
            )

            cv2.ellipse(img, center, axes, 0, 0, 360, (b, g, r), -1)
        b_out, g_out, r_out = cv2.split(np.uint64(img))

    return r_out, g_out, b_out


def add_background(input_image, bgr=(0, 0, 0), mode="pure_color"):
    """
    本函数的功能为为透明图像加上背景。
    :param input_image: numpy.array(4 channels), 透明图像
    :param bgr: tuple, 合成纯色底时的 BGR 值
    :param new_background: numpy.array(3 channels)，合成自定义图像底时的背景图
    :return: output: 合成好的输出图像
    """
    height, width = input_image.shape[0], input_image.shape[1]
    b, g, r, a = cv2.split(input_image)
    a_cal = a / 255
    if mode == "pure_color":
        # 纯色填充
        b2 = np.full([height, width], bgr[0], dtype=int)
        g2 = np.full([height, width], bgr[1], dtype=int)
        r2 = np.full([height, width], bgr[2], dtype=int)
    elif mode == "updown_gradient":
        b2, g2, r2 = generate_gradient(bgr, width, height, mode="updown")
    else:
        b2, g2, r2 = generate_gradient(bgr, width, height, mode="center")

    output = cv2.merge(
        ((b - b2) * a_cal + b2, (g - g2) * a_cal + g2, (r - r2) * a_cal + r2)
    )

    return output
