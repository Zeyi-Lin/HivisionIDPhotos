"""
亮度、对比度、锐化调整模块
"""

import cv2
import numpy as np


def adjust_brightness_contrast_sharpen(
    image,
    brightness_factor=0,
    contrast_factor=0,
    sharpen_strength=0,
):
    """
    调整图像的亮度和对比度。

    参数:
    image (numpy.ndarray): 输入的图像数组。
    brightness_factor (float): 亮度调整因子。大于0增加亮度，小于0降低亮度。
    contrast_factor (float): 对比度调整因子。大于0增加对比度，小于0降低对比度。

    返回:
    numpy.ndarray: 调整亮度和对比度后的图像。
    """
    if brightness_factor == 0 and contrast_factor == 0 and sharpen_strength == 0:
        return image.copy()

    adjusted_image = image.copy()

    # 将亮度因子转换为调整值
    alpha = 1.0 + (contrast_factor / 100.0)
    beta = brightness_factor

    # 使用 cv2.convertScaleAbs 函数调整亮度和对比度
    adjusted_image = cv2.convertScaleAbs(adjusted_image, alpha=alpha, beta=beta)

    # 增强锐化
    adjusted_image = sharpen_image(adjusted_image, sharpen_strength)

    return adjusted_image


def sharpen_image(image, strength=0):
    """
    对图像进行锐化处理。

    参数:
    image (numpy.ndarray): 输入的图像数组。
    strength (float): 锐化强度，范围建议为0-5。0表示不进行锐化。

    返回:
    numpy.ndarray: 锐化后的图像。
    """
    print(f"Shapen strength: {strength}")
    if strength == 0:
        return image.copy()

    strength = strength * 20
    # 将强度转换为适合kernel的值，但减小影响
    kernel_strength = 1 + (strength / 500)  # 将除数从100改为500，减小锐化效果

    # 创建更温和的锐化kernel
    kernel = (
        np.array([[-0.5, -0.5, -0.5], [-0.5, 5, -0.5], [-0.5, -0.5, -0.5]])
        * kernel_strength
    )

    # 应用锐化kernel
    sharpened = cv2.filter2D(image, -1, kernel)

    # 确保结果在0-255范围内
    sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)

    # 混合原图和锐化后的图像，进一步减小锐化效果
    alpha = strength / 200  # 混合比例，最大为0.5
    blended = cv2.addWeighted(image, 1 - alpha, sharpened, alpha, 0)

    return blended


# Gradio接口
def base_adjustment(image, brightness, contrast, sharpen):
    adjusted = adjust_brightness_contrast_sharpen(image, brightness, contrast, sharpen)
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
                value=0,  # Changed from 'default' to 'value'
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
        ],
        outputs=gr.Image(label="Adjusted Image"),
        title="Image Brightness Adjustment",
        description="Adjust the brightness of an image using a slider.",
    )
    iface.launch()
