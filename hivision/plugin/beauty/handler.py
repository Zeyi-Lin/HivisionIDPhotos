import cv2
import numpy as np
from hivision.creator.context import Context
from hivision.plugin.beauty.whitening import make_whitening


def beauty_face(ctx: Context):
    """
    对人脸进行美颜处理

    :param ctx: Context对象，包含处理参数和图像
    """
    # 目前只实现了美白功能，可以在这里添加其他美颜处理
    if ctx.params.whitening_strength > 0:
        _, _, _, alpha = cv2.split(ctx.matting_image)
        b, g, r = cv2.split(
            make_whitening(ctx.origin_image, ctx.params.whitening_strength)
        )
        ctx.matting_image = cv2.merge((b, g, r, alpha))
