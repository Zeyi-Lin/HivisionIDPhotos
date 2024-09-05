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
from .face_detector import detect_face
from .photo_adjuster import adjust_photo


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
        self.detection_handler: ContextHandler = detect_face
        # 上下文
        self.ctx = None

    def __call__(
        self,
        image: np.ndarray,
        size: Tuple[int, int] = (413, 295),
        change_bg_only: bool = False,
        head_measure_ratio: float = 0.2,
        head_height_ratio: float = 0.45,
        head_top_range: float = (0.12, 0.1),
    ) -> Result:
        """
        证件照处理函数
        :param image: 输入图像
        :param change_bg_only: 是否只需要换底
        :param size: 输出的图像大小（h,w)
        :param head_measure_ratio: 人脸面积与全图面积的期望比值
        :param head_height_ratio: 人脸中心处在全图高度的比例期望值
        :param head_top_range: 头距离顶部的比例（max,min)

        :return: 返回处理后的证件照和一系列参数
        """
        # 0.初始化上下文
        params = Params(
            size=size,
            change_bg_only=change_bg_only,
            head_measure_ratio=head_measure_ratio,
            head_height_ratio=head_height_ratio,
            head_top_range=head_top_range,
        )
        self.ctx = Context(params)
        ctx = self.ctx
        ctx.processing_image = image
        ctx.processing_image = U.resize_image_esp(
            ctx.processing_image, 2000
        )  # 将输入图片 resize 到最大边长为 2000
        ctx.origin_image = ctx.processing_image.copy()
        self.before_all and self.before_all(ctx)
        # 1. 人像抠图
        self.matting_handler(ctx)
        self.after_matting and self.after_matting(ctx)
        if ctx.params.change_bg_only:
            ctx.result = Result(
                standard=ctx.matting_image,
                hd=ctx.matting_image,
                clothing_params=None,
                typography_params=None,
            )
            self.after_all and self.after_all(ctx)
            return ctx.result
        # 2. 人脸检测
        self.detection_handler(ctx)
        self.after_detect and self.after_detect(ctx)
        # 3. 图像调整
        result_image_hd, result_image_standard, clothing_params, typography_params = (
            adjust_photo(ctx)
        )
        ctx.result = Result(
            standard=result_image_standard,
            hd=result_image_hd,
            clothing_params=clothing_params,
            typography_params=typography_params,
        )
        self.after_all and self.after_all(ctx)
        return ctx.result
