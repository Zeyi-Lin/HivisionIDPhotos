#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
@DATE: 2024/9/5 19:20
@File: context.py
@IDE: pycharm
@Description:
    证件照创建上下文类，用于同步信息
"""
from typing import Optional, Callable, Tuple
import numpy as np


class Params:
    def __init__(
        self,
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
    ):
        self.__size = size
        self.__change_bg_only = change_bg_only
        self.__crop_only = crop_only
        self.__head_measure_ratio = head_measure_ratio
        self.__head_height_ratio = head_height_ratio
        self.__head_top_range = head_top_range
        self.__face = face
        self.__whitening_strength = whitening_strength
        self.__brightness_strength = brightness_strength
        self.__contrast_strength = contrast_strength
        self.__sharpen_strength = sharpen_strength
        self.__saturation_strength = saturation_strength
        self.__face_alignment = face_alignment

    @property
    def size(self):
        return self.__size

    @property
    def change_bg_only(self):
        return self.__change_bg_only

    @property
    def head_measure_ratio(self):
        return self.__head_measure_ratio

    @property
    def head_height_ratio(self):
        return self.__head_height_ratio

    @property
    def head_top_range(self):
        return self.__head_top_range

    @property
    def crop_only(self):
        return self.__crop_only

    @property
    def face(self):
        return self.__face

    @property
    def whitening_strength(self):
        return self.__whitening_strength

    @property
    def brightness_strength(self):
        return self.__brightness_strength

    @property
    def contrast_strength(self):
        return self.__contrast_strength

    @property
    def sharpen_strength(self):
        return self.__sharpen_strength

    @property
    def saturation_strength(self):
        return self.__saturation_strength

    @property
    def face_alignment(self):
        return self.__face_alignment


class Result:
    def __init__(
        self,
        standard: np.ndarray,
        hd: np.ndarray,
        matting: np.ndarray,
        clothing_params: Optional[dict],
        typography_params: Optional[dict],
        face: Optional[Tuple[int, int, int, int, float]],
    ):
        self.standard = standard
        self.hd = hd
        self.matting = matting
        self.clothing_params = clothing_params
        """
        服装参数，仅换底时为 None
        """
        self.typography_params = typography_params
        """
        排版参数，仅换底时为 None
        """
        self.face = face

    def __iter__(self):
        return iter(
            [
                self.standard,
                self.hd,
                self.matting,
                self.clothing_params,
                self.typography_params,
                self.face,
            ]
        )


class Context:
    def __init__(self, params: Params):
        self.params: Params = params
        """
        证件照处理参数
        """
        self.origin_image: Optional[np.ndarray] = None
        """
        输入的原始图像，处理时会进行resize，长宽不一定等于输入图像
        """
        self.processing_image: Optional[np.ndarray] = None
        """
        当前正在处理的图像
        """
        self.matting_image: Optional[np.ndarray] = None
        """
        人像抠图结果
        """
        self.face: dict = dict(rectangle=None, roll_angle=None)
        """
        人脸检测结果，大于一个人脸时已在上层抛出异常
        rectangle: 人脸矩形框，包含 x1, y1, width, height 的坐标, x1, y1 为左上角坐标, width, height 为矩形框的宽度和高度
        roll_angle: 人脸偏转角度，以眼睛为标准，计算的人脸偏转角度，用于人脸矫正
        """
        self.result: Optional[Result] = None
        """
        证件照处理结果
        """
        self.align_info: Optional[dict] = None
        """
        人脸矫正信息，仅当 align_face 为 True 时存在
        """


ContextHandler = Optional[Callable[[Context], None]]
