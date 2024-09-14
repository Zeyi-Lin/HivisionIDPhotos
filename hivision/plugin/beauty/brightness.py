"""
亮度调整模块
"""

import cv2


def adjust_brightness(image, brightness_factor=0):
    """
    调整图像的亮度。

    参数:
    image (numpy.ndarray): 输入的图像数组。
    brightness_factor (float): 亮度调整因子。大于0增加亮度，小于0降低亮度。

    返回:
    numpy.ndarray: 调整亮度后的图像。
    """
    if brightness_factor == 0:
        return image.copy()

    # 将亮度因子转换为调整值
    alpha = 1.0 + (brightness_factor / 100.0)
    beta = 0

    # 使用 cv2.convertScaleAbs 函数调整亮度
    bright_image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

    return bright_image


# Gradio接口
def brightness_adjustment(image, brightness):
    adjusted = adjust_brightness(image, brightness)
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
        ],
        outputs=gr.Image(label="Adjusted Image"),
        title="Image Brightness Adjustment",
        description="Adjust the brightness of an image using a slider.",
    )
    iface.launch()
