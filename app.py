import gradio as gr
import onnxruntime
from face_judgement_align import IDphotos_create
from hivisionai.hycv.vision import add_background
import pathlib
import numpy as np

def set_example_image(example: list) -> dict:
    return gr.Image.update(value=example[0])


def idphoto_inference(input_image,
                      size_option,
                      color_option,
                      id_height=413,
                      id_width=295,
                      head_measure_ratio=0.2,
                      head_height_ratio=0.45,
                      top_distance_max=0.12,
                      top_distance_min=0.10):

    colors_bgr = {"蓝色": (86, 140, 212), "白色": (255, 255, 255), "红色": (233, 51, 35)}

    if size_option == "一寸":
        id_height = 413
        id_width = 295
    elif size_option == "二寸":
        id_height = 626
        id_width = 413

    result_image_hd, result_image_standard, typography_arr, typography_rotate, \
    _, _, _, _, id_temp_info = IDphotos_create(input_image,
                                               size=(id_height, id_width),
                                               head_measure_ratio=head_measure_ratio,
                                               head_height_ratio=head_height_ratio,
                                               align=False,
                                               beauty=False,
                                               fd68=None,
                                               human_sess=sess,
                                               oss_image_name="test_tmping.jpg",
                                               user=None,
                                               IS_DEBUG=False,
                                               top_distance_max=top_distance_max,
                                               top_distance_min=top_distance_min)
    result_image_standard = np.uint8(add_background(result_image_standard, bgr=colors_bgr[color_option]))
    result_image_hd = np.uint8(add_background(result_image_hd, bgr=colors_bgr[color_option]))

    return result_image_standard, result_image_hd


if __name__ == "__main__":
    HY_HUMAN_MATTING_WEIGHTS_PATH = "./hivision_modnet.onnx"
    sess = onnxruntime.InferenceSession(HY_HUMAN_MATTING_WEIGHTS_PATH)
    sizes = ["一寸", "二寸", "自定义"]
    colors = ["蓝色", "白色", "红色"]

    title = "<h1 id='title'>焕影一新-证件照制作</h1>"
    css = '''
    h1#title {
      text-align: center;
    }
    '''

    demo = gr.Blocks(css=css)

    with demo:
        gr.Markdown(title)
        with gr.Row():
            with gr.Column():
                # 上传图片
                img_input = gr.Image().style(height=350)
                size_options = gr.Radio(choices=sizes, label="证件照尺寸", value="一寸", elem_id="size")
                color_options = gr.Radio(choices=colors, label="背景色", value="蓝色", elem_id="color")

                img_but = gr.Button('开始制作')
                # 案例图片
                example_images = gr.Dataset(components=[img_input],
                                            samples=[[path.as_posix()]
                                                     for path in sorted(pathlib.Path('images').rglob('*.jpg'))])
            with gr.Column():
                img_output_standard = gr.Image(label="标准照").style(height=350)
                img_output_standard_hd = gr.Image(label="高清照").style(height=350)

        img_but.click(idphoto_inference, inputs=[img_input, size_options, color_options],
                      outputs=[img_output_standard, img_output_standard_hd], queue=True)
        example_images.click(fn=set_example_image, inputs=[example_images], outputs=[img_input])

    demo.launch(server_name="0.0.0.0", enable_queue=True)
