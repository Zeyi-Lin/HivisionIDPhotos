#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
@DATE: 2024/9/5 18:32
@File: error.py
@IDE: pycharm
@Description:
    错误处理
"""


class FaceError(Exception):
    def __init__(self, err, face_num):
        """
        证件照人脸错误，此时人脸检测失败，可能是没有检测到人脸或者检测到多个人脸
        Args:
            err: 错误描述
            face_num: 告诉此时识别到的人像个数
        """
        super().__init__(err)
        self.face_num = face_num
