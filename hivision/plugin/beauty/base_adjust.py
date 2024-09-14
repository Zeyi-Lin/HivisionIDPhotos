"""
亮度调整模块
"""

import cv2


def adjust_brightness_contrast(image, brightness_factor=0, contrast_factor=0):
    """
    调整图像的亮度和对比度。

    参数:
    image (numpy.ndarray): 输入的图像数组。
    brightness_factor (float): 亮度调整因子。大于0增加亮度，小于0降低亮度。
    contrast_factor (float): 对比度调整因子。大于0增加对比度，小于0降低对比度。

    返回:
    numpy.ndarray: 调整亮度和对比度后的图像。
    """
    if brightness_factor == 0 and contrast_factor == 0:
        return image.copy()

    # 将亮度因子转换为调整值
    alpha = 1.0 + (contrast_factor / 100.0)
    beta = brightness_factor

    # 使用 cv2.convertScaleAbs 函数调整亮度和对比度
    adjusted_image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

    return adjusted_image


# Gradio接口
def brightness_adjustment(image, brightness, contrast_factor):
    adjusted = adjust_brightness_contrast(image, brightness, contrast_factor)
    return adjusted


if __name__ == "__main__":
    import gradio as gr

    iface = gr.Interface(
        fn=brightness_adjustment,
        inputs=[
            gr.Image(label="Input Image"),
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
        ],
        outputs=gr.Image(label="Adjusted Image"),
        title="Image Brightness Adjustment",
        description="Adjust the brightness of an image using a slider.",
    )
    iface.launch()
