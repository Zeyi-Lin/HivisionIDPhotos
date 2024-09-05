#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
@DATE: 2024/9/5 19:32
@File: face_detector.py
@IDE: pycharm
@Description:
    人脸检测器
"""
from mtcnnruntime import MTCNN
from .context import Context
from hivision.error import FaceError
import cv2

mtcnn = None


def detect_face(ctx: Context, scale: int = 2):
    """
    人脸检测处理者，只进行人脸数量的检测
    :param ctx: 上下文，此时已获取到原始图和抠图结果，但是我们只需要原始图
    :param scale: 最大边长缩放比例，原图:缩放图 = 1:scale
    :raise FaceError: 人脸检测错误，多个人脸或者没有人脸
    """
    global mtcnn
    if mtcnn is None:
        mtcnn = MTCNN()
    image = cv2.resize(
        ctx.origin_image,
        (ctx.origin_image.shape[1] // scale, ctx.origin_image.shape[0] // scale),
        interpolation=cv2.INTER_AREA,
    )
    faces, _ = mtcnn.detect(image)
    if len(faces) != 1:
        # 保险措施，如果检测到多个人脸或者没有人脸，用原图再检测一次
        faces, _ = mtcnn.detect(ctx.origin_image)
    else:
        for item, param in enumerate(faces[0]):
            faces[0][item] = param * 2
    if len(faces) != 1:
        raise FaceError("Expected 1 face, but got {}".format(len(faces)), len(faces))
    ctx.face = (faces[0][0], faces[0][1], faces[0][2], faces[0][3], faces[0][4])
