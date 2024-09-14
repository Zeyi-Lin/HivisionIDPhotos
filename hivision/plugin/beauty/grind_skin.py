# Required Libraries
import cv2
import numpy as np
import gradio as gr


def annotate_image(image, grind_degree, detail_degree, strength):
    """Annotates the image with parameters in the lower-left corner."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    color = (0, 0, 255)
    thickness = 1
    line_type = cv2.LINE_AA

    # Text positions
    y_offset = 20
    x_offset = 10
    y_base = image.shape[0] - 10

    # Define each line of the annotation
    lines = [
        f"Grind Degree: {grind_degree}",
        f"Detail Degree: {detail_degree}",
        f"Strength: {strength}",
    ]

    # Draw the text lines on the image
    for i, line in enumerate(lines):
        y_position = y_base - (i * y_offset)
        cv2.putText(
            image,
            line,
            (x_offset, y_position),
            font,
            font_scale,
            color,
            thickness,
            line_type,
        )

    return image


def grindSkin(src, grindDegree: int = 3, detailDegree: int = 1, strength: int = 9):
    """
    Dest =(Src * (100 - Opacity) + (Src + 2 * GaussBlur(EPFFilter(Src) - Src)) * Opacity) / 100
    人像磨皮方案
    Args:
        src: 原图
        grindDegree: 磨皮程度调节参数
        detailDegree: 细节程度调节参数
        strength: 融合程度，作为磨皮强度（0 - 10）

    Returns:
        磨皮后的图像
    """
    if strength <= 0:
        return src
    dst = src.copy()
    opacity = min(10.0, strength) / 10.0
    dx = grindDegree * 5
    fc = grindDegree * 12.5
    temp1 = cv2.bilateralFilter(src[:, :, :3], dx, fc, fc)
    temp2 = cv2.subtract(temp1, src[:, :, :3])
    temp3 = cv2.GaussianBlur(temp2, (2 * detailDegree - 1, 2 * detailDegree - 1), 0)
    temp4 = cv2.add(cv2.add(temp3, temp3), src[:, :, :3])
    dst[:, :, :3] = cv2.addWeighted(temp4, opacity, src[:, :, :3], 1 - opacity, 0.0)
    return dst


def process_image(input_img, grind_degree, detail_degree, strength):
    # Reading the image using OpenCV
    img = cv2.cvtColor(input_img, cv2.COLOR_RGB2BGR)
    # Processing the image
    output_img = grindSkin(img, grind_degree, detail_degree, strength)
    # Annotating the processed image with parameters
    output_img_annotated = annotate_image(
        output_img.copy(), grind_degree, detail_degree, strength
    )
    # Horizontal stacking of input and processed images
    combined_img = cv2.hconcat([img, output_img_annotated])
    # Convert the combined image back to RGB for display
    combined_img_rgb = cv2.cvtColor(combined_img, cv2.COLOR_BGR2RGB)
    return combined_img_rgb


with gr.Blocks(title="Skin Grinding") as iface:
    gr.Markdown("## Skin Grinding Application")

    with gr.Row():
        image_input = gr.Image(type="numpy", label="Input Image")
        image_output = gr.Image(label="Output Image")

    grind_degree_slider = gr.Slider(
        minimum=1, maximum=10, value=3, step=1, label="Grind Degree"
    )
    detail_degree_slider = gr.Slider(
        minimum=1, maximum=10, value=1, step=1, label="Detail Degree"
    )
    strength_slider = gr.Slider(
        minimum=0, maximum=10, value=9, step=1, label="Strength"
    )

    gr.Button("Process Image").click(
        fn=process_image,
        inputs=[
            image_input,
            grind_degree_slider,
            detail_degree_slider,
            strength_slider,
        ],
        outputs=image_output,
    )

if __name__ == "__main__":
    iface.launch()
