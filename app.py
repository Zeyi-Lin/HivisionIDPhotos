import gradio as gr
from paddleocr_v3_inference import inferenceOCR
import cv2
import pathlib


def set_example_image(example: list) -> dict:
    return gr.Image.update(value=example[0])


def inference(input_image):
    result_image, return_json = inferenceOCR(input_image)
    return cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB), return_json


if __name__ == "__main__":

    title = "<h1 id='title'>PaddleOCR</h1>"
    # description = "为了保证Demo的运行体验，对输入图像做了缩放处理（最大边长限定为1024）"
    css = '''
        h1#title {
          text-align: center;
        }
        '''

    demo = gr.Blocks(css=css)
    with demo:
        gr.Markdown(title)
        # gr.Markdown(description)
        with gr.Row():
            with gr.Column():
                # 上传图片
                img_input = gr.Image().style(height=350)
                json_visibility_switch = gr.Radio(choices=["ON", "OFF"], label="是否显示JSON结果", value="OFF")
                img_but = gr.Button('RUN')
                # 案例图片
                example_images = gr.Dataset(components=[img_input],
                                            samples=[[path.as_posix()]
                                                     for path in sorted(pathlib.Path('images').rglob('*.jpg'))])

            with gr.Column():
                img_output = gr.Image(label="Show_Image").style(height=350)
                result_json = gr.JSON(label="Result_json", visible=False).style(height=350)

            def json_visible(json_visibility_switch):
                if json_visibility_switch == "ON":
                    return {result_json: gr.update(visible=True)}
                else:
                    return {result_json: gr.update(visible=False)}

        json_visibility_switch.input(json_visible, inputs=[json_visibility_switch], outputs=[result_json], queue=True)
        img_but.click(inference, inputs=[img_input],
                      outputs=[img_output, result_json], queue=True)
        example_images.click(fn=set_example_image, inputs=[example_images], outputs=[img_input])

    demo.launch(enable_queue=True)