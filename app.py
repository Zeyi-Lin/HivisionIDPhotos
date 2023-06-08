import gradio as gr
import onnxruntime
from face_judgement_align import IDphotos_create
from hivisionai.hycv.vision import add_background
import pathlib
import numpy as np


def set_example_image(example: list) -> dict:
    return gr.Image.update(value=example[0])


if __name__ == "__main__":
    HY_HUMAN_MATTING_WEIGHTS_PATH = "./hivision_modnet.onnx"
    sess = onnxruntime.InferenceSession(HY_HUMAN_MATTING_WEIGHTS_PATH)
    sizes = ["一寸", "二寸", "不改尺寸只换底", "自定义尺寸"]
    colors = ["蓝色", "白色", "红色", "自定义底色"]

    title = "<h1 id='title'>焕影一新-证件照制作</h1>"
    description = "<h3>😎6.8更新：新增自定义尺寸</h3>"
    css = '''
    h1#title, h3 {
      text-align: center;
    }
    '''

    demo = gr.Blocks(css=css)

    with demo:
        gr.Markdown(title)
        gr.Markdown(description)
        with gr.Row():
            with gr.Column():
                # 上传图片
                img_input = gr.Image().style(height=350)
                size_options = gr.Radio(choices=sizes, label="证件照尺寸选项", value="一寸", elem_id="size")
                with gr.Row(visible=False) as custom_size:
                    custom_size_height = gr.Number(value=413, label="height", interactive=True)
                    custom_size_wdith = gr.Number(value=295, label="width", interactive=True)

                color_options = gr.Radio(choices=colors, label="背景色", value="蓝色", elem_id="color")
                with gr.Row(visible=False) as custom_color:
                    custom_color_R = gr.Number(value=0, label="R", interactive=True)
                    custom_color_G = gr.Number(value=0, label="G", interactive=True)
                    custom_color_B = gr.Number(value=0, label="B", interactive=True)

                img_but = gr.Button('开始制作')
                # 案例图片
                example_images = gr.Dataset(components=[img_input],
                                            samples=[[path.as_posix()]
                                                     for path in sorted(pathlib.Path('images').rglob('*.jpg'))])

            with gr.Column():
                notification = gr.Text(label="状态", visible=False)
                img_output_standard = gr.Image(label="标准照").style(height=350)
                img_output_standard_hd = gr.Image(label="高清照").style(height=350)


            def idphoto_inference(input_image,
                                  size_option,
                                  color_option,
                                  custom_color_R,
                                  custom_color_G,
                                  custom_color_B,
                                  custom_size_height,
                                  custom_size_width,
                                  id_height=413,
                                  id_width=295,
                                  head_measure_ratio=0.2,
                                  head_height_ratio=0.45,
                                  top_distance_max=0.12,
                                  top_distance_min=0.10):

                def range_check(value, min_value=0, max_value=255):
                    value = int(value)
                    if value <= min_value:
                        value = min_value
                    elif value > max_value:
                        value = max_value
                    return value

                colors_bgr = {"蓝色": (86, 140, 212), "白色": (255, 255, 255), "红色": (233, 51, 35)}
                if color_option == "自定义底色":
                    colors_bgr["自定义底色"] = (range_check(custom_color_R),
                                           range_check(custom_color_G),
                                           range_check(custom_color_B))

                mode = "ID"
                if size_option == "一寸":
                    id_height = 413
                    id_width = 295
                elif size_option == "二寸":
                    id_height = 626
                    id_width = 413
                elif size_option == "不改尺寸只换底":
                    mode = "Matting"
                elif size_option == "自定义尺寸":
                    id_height = int(custom_size_height)
                    id_width = int(custom_size_width)
                    if id_height < id_width or min(id_height, id_width) < 100 or max(id_height, id_width) > 1800:
                        return {
                            img_output_standard: gr.update(value=None),
                            img_output_standard_hd: gr.update(value=None),
                            notification: gr.update(value="宽度应不大于长度；长宽不应小于100，大于1800", visible=True)}

                result_image_hd, result_image_standard, typography_arr, typography_rotate, \
                _, _, _, _, status = IDphotos_create(input_image,
                                                     mode=mode,
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

                if status == 0:
                    result_messgae = {
                        img_output_standard: gr.update(value=None),
                        img_output_standard_hd: gr.update(value=None),
                        notification: gr.update(value="人脸数量不等于1", visible=True)
                    }

                else:

                    result_image_standard = np.uint8(
                        add_background(result_image_standard, bgr=colors_bgr[color_option]))
                    result_image_hd = np.uint8(add_background(result_image_hd, bgr=colors_bgr[color_option]))

                    result_messgae = {
                        img_output_standard: result_image_standard,
                        img_output_standard_hd: result_image_hd,
                        notification: gr.update(visible=False)}

                return result_messgae


            def change_color(colors):
                if colors == "自定义底色":
                    return {custom_color: gr.update(visible=True)}
                else:
                    return {custom_color: gr.update(visible=False)}

            def change_size(size_option_item):
                if size_option_item == "自定义尺寸":
                    return {custom_size: gr.update(visible=True)}
                else:
                    return {custom_size: gr.update(visible=False)}

        color_options.input(change_color, inputs=[color_options], outputs=[custom_color])
        size_options.input(change_size, inputs=[size_options], outputs=[custom_size])
        img_but.click(idphoto_inference,
                      inputs=[img_input, size_options, color_options,
                              custom_color_R, custom_color_G, custom_color_B,
                              custom_size_height, custom_size_wdith],
                      outputs=[img_output_standard, img_output_standard_hd, notification], queue=True)
        example_images.click(fn=set_example_image, inputs=[example_images], outputs=[img_input])

    demo.launch(enable_queue=True)
