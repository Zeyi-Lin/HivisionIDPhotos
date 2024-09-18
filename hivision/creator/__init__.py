#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
@DATE: 2024/9/5 16:45
@File: __init__.py
@IDE: pycharm
@Description:
    创建证件照
"""
import numpy as np
from typing import Tuple
import hivision.creator.utils as U
from .context import Context, ContextHandler, Params, Result
from .human_matting import extract_human
from .face_detector import detect_face_mtcnn
from hivision.plugin.beauty.handler import beauty_face
from .photo_adjuster import adjust_photo
import cv2


class IDCreator:
    """
    证件照创建类，包含完整的证件照流程
    """

    def __init__(self):
        # 回调时机
        self.before_all: ContextHandler = None
        """
        在所有处理之前，此时图像已经被 resize 到最大边长为 2000
        """
        self.after_matting: ContextHandler = None
        """
        在抠图之后，ctx.matting_image 被赋值
        """
        self.after_detect: ContextHandler = None
        """
        在人脸检测之后，ctx.face 被赋值，如果为仅换底，则不会执行此回调
        """
        self.after_all: ContextHandler = None
        """
        在所有处理之后，此时 ctx.result 被赋值
        """
        # 处理者
        self.matting_handler: ContextHandler = extract_human
        self.detection_handler: ContextHandler = detect_face_mtcnn
        self.beauty_handler: ContextHandler = beauty_face
        # 上下文
        self.ctx = None

    def __call__(
        self,
        image: np.ndarray,
        size: Tuple[int, int] = (413, 295),
        change_bg_only: bool = False,
        crop_only: bool = False,
        head_measure_ratio: float = 0.2,
        head_height_ratio: float = 0.45,
        head_top_range: float = (0.12, 0.1),
        face: Tuple[int, int, int, int] = None,
        whitening_strength: int = 0,
        brightness_strength: int = 0,
        contrast_strength: int = 0,
        sharpen_strength: int = 0,
        saturation_strength: int = 0,
        face_alignment: bool = False,
    ) -> Result:
        """
        证件照处理函数
        :param image: 输入图像
        :param change_bg_only: 是否只需要抠图
        :param crop_only: 是否只需要裁剪
        :param size: 输出的图像大小（h,w)
        :param head_measure_ratio: 人脸面积与全图面积的期望比值
        :param head_height_ratio: 人脸中心处在全图高度的比例期望值
        :param head_top_range: 头距离顶部的比例（max,min)
        :param face: 人脸坐标
        :param whitening_strength: 美白强度
        :param brightness_strength: 亮度强度
        :param contrast_strength: 对比度强度
        :param sharpen_strength: 锐化强度
        :param align_face: 是否需要人脸矫正

        :return: 返回处理后的证件照和一系列参数
        """
        # 0.初始化上下文
        params = Params(
            size=size,
            change_bg_only=change_bg_only,
            head_measure_ratio=head_measure_ratio,
            head_height_ratio=head_height_ratio,
            head_top_range=head_top_range,
            crop_only=crop_only,
            face=face,
            whitening_strength=whitening_strength,
            brightness_strength=brightness_strength,
            contrast_strength=contrast_strength,
            sharpen_strength=sharpen_strength,
            saturation_strength=saturation_strength,
            face_alignment=face_alignment,
        )

        self.ctx = Context(params)
        ctx = self.ctx
        ctx.processing_image = image
        ctx.processing_image = U.resize_image_esp(
            ctx.processing_image, 2000
        )  # 将输入图片 resize 到最大边长为 2000
        ctx.origin_image = ctx.processing_image.copy()
        self.before_all and self.before_all(ctx)

        # 1. ------------------人像抠图------------------
        if not ctx.params.crop_only:
            # 调用抠图工作流
            self.matting_handler(ctx)
            self.after_matting and self.after_matting(ctx)
        else:
            ctx.matting_image = ctx.processing_image

        # 2. ------------------美颜------------------
        self.beauty_handler(ctx)

        # 如果仅换底，则直接返回抠图结果
        if ctx.params.change_bg_only:
            ctx.result = Result(
                standard=ctx.matting_image,
                hd=ctx.matting_image,
                matting=ctx.matting_image,
                clothing_params=None,
                typography_params=None,
                face=None,
            )
            self.after_all and self.after_all(ctx)
            return ctx.result

        # 3. ------------------人脸检测------------------
        self.detection_handler(ctx)
        self.after_detect and self.after_detect(ctx)

        # 3.1 ------------------人脸对齐------------------
        if ctx.params.face_alignment and abs(ctx.face["roll_angle"]) > 2:
            from hivision.creator.rotation_adjust import rotate_bound_4channels

            print("执行人脸对齐")
            print("旋转角度：", ctx.face["roll_angle"])
            # 根据角度旋转原图和抠图
            b, g, r, a = cv2.split(ctx.matting_image)
            ctx.origin_image, ctx.matting_image, _, _, _, _ = rotate_bound_4channels(
                cv2.merge((b, g, r)),
                a,
                -1 * ctx.face["roll_angle"],
            )

            # 旋转后再执行一遍人脸检测
            self.detection_handler(ctx)
            self.after_detect and self.after_detect(ctx)

        # 4. ------------------图像调整------------------
        result_image_hd, result_image_standard, clothing_params, typography_params = (
            adjust_photo(ctx)
        )

        # 5. ------------------返回结果------------------
        ctx.result = Result(
            standard=result_image_standard,
            hd=result_image_hd,
            matting=ctx.matting_image,
            clothing_params=clothing_params,
            typography_params=typography_params,
            face=ctx.face,
        )
        self.after_all and self.after_all(ctx)

        return ctx.result
