"""
亮度、对比度、锐化、饱和度调整模块
"""

import cv2
import numpy as np


def adjust_brightness_contrast_sharpen_saturation(
    image,
    brightness_factor=0,
    contrast_factor=0,
    sharpen_strength=0,
    saturation_factor=0,
):
    """
    调整图像的亮度、对比度、锐度和饱和度。

    参数:
    image (numpy.ndarray): 输入的图像数组。
    brightness_factor (float): 亮度调整因子。大于0增加亮度，小于0降低亮度。
    contrast_factor (float): 对比度调整因子。大于0增加对比度，小于0降低对比度。
    sharpen_strength (float): 锐化强度。
    saturation_factor (float): 饱和度调整因子。大于0增加饱和度，小于0降低饱和度。

    返回:
    numpy.ndarray: 调整后的图像。
    """
    if (
        brightness_factor == 0
        and contrast_factor == 0
        and sharpen_strength == 0
        and saturation_factor == 0
    ):
        return image.copy()

    adjusted_image = image.copy()

    # 调整饱和度
    if saturation_factor != 0:
        adjusted_image = adjust_saturation(adjusted_image, saturation_factor)

    # 调整亮度和对比度
    alpha = 1.0 + (contrast_factor / 100.0)
    beta = brightness_factor
    adjusted_image = cv2.convertScaleAbs(adjusted_image, alpha=alpha, beta=beta)

    # 增强锐化
    adjusted_image = sharpen_image(adjusted_image, sharpen_strength)

    return adjusted_image


def adjust_saturation(image, saturation_factor):
    """
    调整图像的饱和度。

    参数:
    image (numpy.ndarray): 输入的图像数组。
    saturation_factor (float): 饱和度调整因子。大于0增加饱和度，小于0降低饱和度。

    返回:
    numpy.ndarray: 调整后的图像。
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    s = s.astype(np.float32)
    s = s + s * (saturation_factor / 100.0)
    s = np.clip(s, 0, 255).astype(np.uint8)
    hsv = cv2.merge([h, s, v])
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def sharpen_image(image, strength=0):
    """
    对图像进行锐化处理。

    参数:
    image (numpy.ndarray): 输入的图像数组。
    strength (float): 锐化强度，范围建议为0-5。0表示不进行锐化。

    返回:
    numpy.ndarray: 锐化后的图像。
    """
    print(f"Sharpen strength: {strength}")
    if strength == 0:
        return image.copy()

    strength = strength * 20
    kernel_strength = 1 + (strength / 500)

    kernel = (
        np.array([[-0.5, -0.5, -0.5], [-0.5, 5, -0.5], [-0.5, -0.5, -0.5]])
        * kernel_strength
    )

    sharpened = cv2.filter2D(image, -1, kernel)
    sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)

    alpha = strength / 200
    blended = cv2.addWeighted(image, 1 - alpha, sharpened, alpha, 0)

    return blended


# Gradio接口
def base_adjustment(image, brightness, contrast, sharpen, saturation):
    adjusted = adjust_brightness_contrast_sharpen_saturation(
        image, brightness, contrast, sharpen, saturation
    )
    return adjusted


if __name__ == "__main__":
    import gradio as gr

    iface = gr.Interface(
        fn=base_adjustment,
        inputs=[
            gr.Image(label="Input Image", height=400),
            gr.Slider(
                minimum=-20,
                maximum=20,
                value=0,
                step=1,
                label="Brightness",
            ),
            gr.Slider(
                minimum=-100,
                maximum=100,
                value=0,
                step=1,
                label="Contrast",
            ),
            gr.Slider(
                minimum=0,
                maximum=5,
                value=0,
                step=1,
                label="Sharpen",
            ),
            gr.Slider(
                minimum=-100,
                maximum=100,
                value=0,
                step=1,
                label="Saturation",
            ),
        ],
        outputs=gr.Image(label="Adjusted Image"),
        title="Image Adjustment",
        description="Adjust the brightness, contrast, sharpness, and saturation of an image using sliders.",
    )
    iface.launch()
