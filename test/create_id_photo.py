#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
@DATE: 2024/9/5 21:39
@File: create_id_photo.py
@IDE: pycharm
@Description:
    用于测试创建证件照
"""
from hivision.creator import IDCreator
import cv2
import os

now_dir = os.path.dirname(__file__)
image_path = os.path.join(os.path.dirname(now_dir), "app", "images", "test.jpg")
output_dir = os.path.join(now_dir, "temp")

image = cv2.imread(image_path)
creator = IDCreator()
result = creator(image)
cv2.imwrite(os.path.join(output_dir, "result.png"), result.standard)
cv2.imwrite(os.path.join(output_dir, "result_hd.png"), result.hd)
