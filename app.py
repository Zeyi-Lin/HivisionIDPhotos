import os
import gradio as gr
from hivision import IDCreator
from hivision.error import FaceError
from hivision.utils import add_background, resize_image_to_kb
from hivision.creator.layout_calculator import (
    generate_layout_photo,
    generate_layout_image,
)
from hivision.creator.human_matting import (
    extract_human_modnet_photographic_portrait_matting,
    extract_human,
)
import pathlib
import numpy as np
from demo.utils import csv_to_size_list
import argparse

# 获取尺寸列表
root_dir = os.path.dirname(os.path.abspath(__file__))
size_list_dict_CN = csv_to_size_list(os.path.join(root_dir, "demo/size_list_CN.csv"))
size_list_dict_EN = csv_to_size_list(os.path.join(root_dir, "demo/size_list_EN.csv"))

color_list_dict_CN = {
    "蓝色": (86, 140, 212),
    "白色": (255, 255, 255),
    "红色": (233, 51, 35),
}

color_list_dict_EN = {
    "Blue": (86, 140, 212),
    "White": (255, 255, 255),
    "Red": (233, 51, 35),
}


# 检测 RGB 是否超出范围，如果超出则约束到 0～255 之间
def range_check(value, min_value=0, max_value=255):
    value = int(value)
    if value <= min_value:
        value = min_value
    elif value > max_value:
        value = max_value
    return value


def idphoto_inference(
    input_image,
    mode_option,
    size_list_option,
    color_option,
    render_option,
    image_kb_options,
    custom_color_R,
    custom_color_G,
    custom_color_B,
    custom_size_height,
    custom_size_width,
    custom_image_kb,
    language,
    matting_model_option,
    head_measure_ratio=0.2,
    head_height_ratio=0.45,
    top_distance_max=0.12,
    top_distance_min=0.10,
):
    idphoto_json = {
        "size_mode": mode_option,
        "color_mode": color_option,
        "render_mode": render_option,
        "image_kb_mode": image_kb_options,
    }

    text_lang_map = {
        "中文": {
            "Size List": "尺寸列表",
            "Custom Size": "自定义尺寸",
            "The width should not be greater than the length; the length and width should not be less than 100, and no more than 1800.": "宽度应不大于长度；长宽不应小于 100，大于 1800",
            "Custom Color": "自定义底色",
            "Custom": "自定义",
            "The number of faces is not equal to 1": "人脸数量不等于 1",
            "Solid Color": "纯色",
            "Up-Down Gradient (White)": "上下渐变 (白)",
            "Center Gradient (White)": "中心渐变 (白)",
            "Set KB size (Download in the bottom right)": "设置 KB 大小（结果在右边最底的组件下载）",
            "Not Set": "不设置",
            "Only Change Background": "只换底",
        },
        "English": {
            "Size List": "Size List",
            "Custom Size": "Custom Size",
            "The width should not be greater than the length; the length and width should not be less than 100, and no more than 1800.": "The width should not be greater than the length; the length and width should not be less than 100, and no more than 1800.",
            "Custom Color": "Custom Color",
            "Custom": "Custom",
            "The number of faces is not equal to 1": "The number of faces is not equal to 1",
            "Solid Color": "Solid Color",
            "Up-Down Gradient (White)": "Up-Down Gradient (White)",
            "Center Gradient (White)": "Center Gradient (White)",
            "Set KB size (Download in the bottom right)": "Set KB size (Download in the bottom right)",
            "Not Set": "Not Set",
            "Only Change Background": "Only Change Background",
        },
    }

    # 如果尺寸模式选择的是尺寸列表
    if idphoto_json["size_mode"] == text_lang_map[language]["Size List"]:
        if language == "中文":
            idphoto_json["size"] = size_list_dict_CN[size_list_option]
        else:
            idphoto_json["size"] = size_list_dict_EN[size_list_option]
    # 如果尺寸模式选择的是自定义尺寸
    elif idphoto_json["size_mode"] == text_lang_map[language]["Custom Size"]:
        id_height = int(custom_size_height)
        id_width = int(custom_size_width)
        if (
            id_height < id_width
            or min(id_height, id_width) < 100
            or max(id_height, id_width) > 1800
        ):
            return {
                img_output_standard: gr.update(value=None),
                img_output_standard_hd: gr.update(value=None),
                notification: gr.update(
                    value=text_lang_map[language][
                        "The width should not be greater than the length; the length and width should not be less than 100, and no more than 1800."
                    ],
                    visible=True,
                ),
            }
        idphoto_json["size"] = (id_height, id_width)
    else:
        idphoto_json["size"] = (None, None)

    # 如果颜色模式选择的是自定义底色
    if idphoto_json["color_mode"] == text_lang_map[language]["Custom Color"]:
        idphoto_json["color_bgr"] = (
            range_check(custom_color_R),
            range_check(custom_color_G),
            range_check(custom_color_B),
        )
    else:
        if language == "中文":
            idphoto_json["color_bgr"] = color_list_dict_CN[color_option]
        else:
            idphoto_json["color_bgr"] = color_list_dict_EN[color_option]

    # 如果输出 KB 大小选择的是自定义
    if idphoto_json["image_kb_mode"] == text_lang_map[language]["Custom"]:
        idphoto_json["custom_image_kb"] = custom_image_kb
    else:
        idphoto_json["custom_image_kb"] = None

    creator = IDCreator()
    if matting_model_option == "modnet_photographic_portrait_matting":
        creator.matting_handler = extract_human_modnet_photographic_portrait_matting
    else:
        creator.matting_handler = extract_human

    change_bg_only = idphoto_json["size_mode"] in ["只换底", "Only Change Background"]
    # 生成证件照
    try:
        result = creator(
            input_image,
            change_bg_only=change_bg_only,
            size=idphoto_json["size"],
            head_measure_ratio=head_measure_ratio,
            head_height_ratio=head_height_ratio,
        )
    except FaceError:
        result_message = {
            img_output_standard: gr.update(value=None),
            img_output_standard_hd: gr.update(value=None),
            notification: gr.update(
                value=text_lang_map[language]["The number of faces is not equal to 1"],
                visible=True,
            ),
        }
    else:
        (result_image_standard, result_image_hd, _, _) = result
        if idphoto_json["render_mode"] == text_lang_map[language]["Solid Color"]:
            result_image_standard = np.uint8(
                add_background(result_image_standard, bgr=idphoto_json["color_bgr"])
            )
            result_image_hd = np.uint8(
                add_background(result_image_hd, bgr=idphoto_json["color_bgr"])
            )
        elif (
            idphoto_json["render_mode"]
            == text_lang_map[language]["Up-Down Gradient (White)"]
        ):
            result_image_standard = np.uint8(
                add_background(
                    result_image_standard,
                    bgr=idphoto_json["color_bgr"],
                    mode="updown_gradient",
                )
            )
            result_image_hd = np.uint8(
                add_background(
                    result_image_hd,
                    bgr=idphoto_json["color_bgr"],
                    mode="updown_gradient",
                )
            )
        else:
            result_image_standard = np.uint8(
                add_background(
                    result_image_standard,
                    bgr=idphoto_json["color_bgr"],
                    mode="center_gradient",
                )
            )
            result_image_hd = np.uint8(
                add_background(
                    result_image_hd,
                    bgr=idphoto_json["color_bgr"],
                    mode="center_gradient",
                )
            )

        if (
            idphoto_json["size_mode"]
            == text_lang_map[language]["Only Change Background"]
        ):
            result_layout_image = gr.update(visible=False)
        else:
            typography_arr, typography_rotate = generate_layout_photo(
                input_height=idphoto_json["size"][0],
                input_width=idphoto_json["size"][1],
            )

            result_layout_image = gr.update(
                value=generate_layout_image(
                    result_image_standard,
                    typography_arr,
                    typography_rotate,
                    height=idphoto_json["size"][0],
                    width=idphoto_json["size"][1],
                ),
                visible=True,
            )

        # 如果输出 KB 大小选择的是自定义
        if idphoto_json["custom_image_kb"]:
            # 将标准照大小调整至目标大小
            print("调整 kb 大小到", idphoto_json["custom_image_kb"], "kb")
            # 输出路径为一个根据时间戳 + 哈希值生成的随机文件名
            import time

            output_image_path = f"{os.path.join(os.path.dirname(__file__), 'demo/kb_output')}/{int(time.time())}.jpg"
            resize_image_to_kb(
                result_image_standard,
                output_image_path,
                idphoto_json["custom_image_kb"],
            )
        else:
            output_image_path = None

        if output_image_path:
            result_message = {
                img_output_standard: result_image_standard,
                img_output_standard_hd: result_image_hd,
                img_output_layout: result_layout_image,
                notification: gr.update(visible=False),
                file_download: gr.update(visible=True, value=output_image_path),
            }
        else:
            result_message = {
                img_output_standard: result_image_standard,
                img_output_standard_hd: result_image_hd,
                img_output_layout: result_layout_image,
                notification: gr.update(visible=False),
                file_download: gr.update(visible=False),
            }

    return result_message


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--port", type=int, default=7860, help="The port number of the server"
    )
    argparser.add_argument(
        "--host", type=str, default="127.0.0.1", help="The host of the server"
    )
    argparser.add_argument(
        "--root_path",
        type=str,
        default=None,
        help="The root path of the server, default is None (='/'), e.g. '/myapp'",
    )

    args = argparser.parse_args()

    language = ["中文", "English"]

    matting_model_list = [
        os.path.splitext(file)[0]
        for file in os.listdir(os.path.join(root_dir, "hivision/creator/weights"))
        if file.endswith(".onnx")
    ]
    DEFAULT_MATTING_MODEL = "modnet_photographic_portrait_matting"
    if DEFAULT_MATTING_MODEL in matting_model_list:
        matting_model_list.remove(DEFAULT_MATTING_MODEL)
        matting_model_list.insert(0, DEFAULT_MATTING_MODEL)

    size_mode_CN = ["尺寸列表", "只换底", "自定义尺寸"]
    size_mode_EN = ["Size List", "Only Change Background", "Custom Size"]

    size_list_CN = list(size_list_dict_CN.keys())
    size_list_EN = list(size_list_dict_EN.keys())

    colors_CN = ["蓝色", "白色", "红色", "自定义底色"]
    colors_EN = ["Blue", "White", "Red", "Custom Color"]

    render_CN = ["纯色", "上下渐变 (白)", "中心渐变 (白)"]
    render_EN = ["Solid Color", "Up-Down Gradient (White)", "Center Gradient (White)"]

    image_kb_CN = ["不设置", "自定义"]
    image_kb_EN = ["Not Set", "Custom"]

    css = """
        #col-left {
            margin: 0 auto;
            max-width: 430px;
        }
        #col-mid {
            margin: 0 auto;
            max-width: 430px;
        }
        #col-right {
            margin: 0 auto;
            max-width: 430px;
        }
        #col-showcase {
            margin: 0 auto;
            max-width: 1100px;
        }
        #button {
            color: blue;
        }
        """

    def load_description(fp):
        with open(fp, "r", encoding="utf-8") as f:
            content = f.read()
        return content

    demo = gr.Blocks(css=css)

    with demo:
        gr.HTML(load_description(os.path.join(root_dir, "assets/title.md")))
        with gr.Row():
            # ------------ 左半边 UI ----------------
            with gr.Column():
                img_input = gr.Image(height=400)

                with gr.Row():
                    language_options = gr.Dropdown(
                        choices=language,
                        label="Language",
                        value="中文",
                        elem_id="language",
                    )
                    matting_model_options = gr.Dropdown(
                        choices=matting_model_list,
                        label="抠图模型",
                        value=matting_model_list[0],
                        elem_id="matting_model",
                    )

                mode_options = gr.Radio(
                    choices=size_mode_CN,
                    label="证件照尺寸选项",
                    value="尺寸列表",
                    elem_id="size",
                )

                # 预设尺寸下拉菜单
                with gr.Row(visible=True) as size_list_row:
                    size_list_options = gr.Dropdown(
                        choices=size_list_CN,
                        label="预设尺寸",
                        value=size_list_CN[0],
                        elem_id="size_list",
                    )

                with gr.Row(visible=False) as custom_size:
                    custom_size_height = gr.Number(
                        value=413, label="height", interactive=True
                    )
                    custom_size_wdith = gr.Number(
                        value=295, label="width", interactive=True
                    )

                # 左：背景色选项
                color_options = gr.Radio(
                    choices=colors_CN, label="背景色", value="蓝色", elem_id="color"
                )

                # 左：如果选择「自定义底色」，显示 RGB 输入框
                with gr.Row(visible=False) as custom_color:
                    custom_color_R = gr.Number(value=0, label="R", interactive=True)
                    custom_color_G = gr.Number(value=0, label="G", interactive=True)
                    custom_color_B = gr.Number(value=0, label="B", interactive=True)

                # 左：渲染方式选项
                render_options = gr.Radio(
                    choices=render_CN,
                    label="渲染方式",
                    value="纯色",
                    elem_id="render",
                )

                # 左：输出 KB 大小选项
                image_kb_options = gr.Radio(
                    choices=image_kb_CN,
                    label="设置 KB 大小（结果在右边最底的组件下载）",
                    value="不设置",
                    elem_id="image_kb",
                )

                # 自定义 KB 大小，滑动条，最小 10KB，最大 200KB
                with gr.Row(visible=False) as custom_image_kb:
                    custom_image_kb_size = gr.Slider(
                        minimum=10,
                        maximum=1000,
                        value=50,
                        label="KB 大小",
                        interactive=True,
                    )

                img_but = gr.Button("开始制作")

                # 案例图片
                example_images = gr.Examples(
                    inputs=[img_input],
                    examples=[
                        [path.as_posix()]
                        for path in sorted(
                            pathlib.Path(os.path.join(root_dir, "demo/images")).rglob(
                                "*.jpg"
                            )
                        )
                    ],
                )

            # ---------------- 右半边 UI ----------------
            with gr.Column():
                notification = gr.Text(label="状态", visible=False)
                with gr.Row():
                    img_output_standard = gr.Image(
                        label="标准照", height=350, format="jpeg"
                    )
                    img_output_standard_hd = gr.Image(
                        label="高清照", height=350, format="jpeg"
                    )
                img_output_layout = gr.Image(
                    label="六寸排版照", height=350, format="jpeg"
                )
                file_download = gr.File(label="下载调整 KB 大小后的照片", visible=False)

            # ---------------- 设置隐藏/显示组件 ----------------
            def change_language(language):
                # 将Gradio组件中的内容改为中文或英文
                if language == "中文":
                    return {
                        size_list_options: gr.update(
                            label="预设尺寸",
                            choices=size_list_CN,
                            value=size_list_CN[0],
                        ),
                        mode_options: gr.update(
                            label="证件照尺寸选项",
                            choices=size_mode_CN,
                            value="尺寸列表",
                        ),
                        color_options: gr.update(
                            label="背景色",
                            choices=colors_CN,
                            value="蓝色",
                        ),
                        img_but: gr.update(value="开始制作"),
                        render_options: gr.update(
                            label="渲染方式",
                            choices=render_CN,
                            value="纯色",
                        ),
                        image_kb_options: gr.update(
                            label="设置 KB 大小（结果在右边最底的组件下载）",
                            choices=image_kb_CN,
                            value="不设置",
                        ),
                        matting_model_options: gr.update(label="抠图模型"),
                        custom_image_kb_size: gr.update(label="KB 大小"),
                        notification: gr.update(label="状态"),
                        img_output_standard: gr.update(label="标准照"),
                        img_output_standard_hd: gr.update(label="高清照"),
                        img_output_layout: gr.update(label="六寸排版照"),
                        file_download: gr.update(label="下载调整 KB 大小后的照片"),
                    }

                elif language == "English":
                    return {
                        size_list_options: gr.update(
                            label="Default size",
                            choices=size_list_EN,
                            value=size_list_EN[0],
                        ),
                        mode_options: gr.update(
                            label="ID photo size options",
                            choices=size_mode_EN,
                            value="Size List",
                        ),
                        color_options: gr.update(
                            label="Background color",
                            choices=colors_EN,
                            value="Blue",
                        ),
                        img_but: gr.update(value="Start"),
                        render_options: gr.update(
                            label="Rendering mode",
                            choices=render_EN,
                            value="Solid Color",
                        ),
                        image_kb_options: gr.update(
                            label="Set KB size (Download in the bottom right)",
                            choices=image_kb_EN,
                            value="Not Set",
                        ),
                        matting_model_options: gr.update(label="Matting model"),
                        custom_image_kb_size: gr.update(label="KB size"),
                        notification: gr.update(label="Status"),
                        img_output_standard: gr.update(label="Standard photo"),
                        img_output_standard_hd: gr.update(label="HD photo"),
                        img_output_layout: gr.update(label="Layout photo"),
                        file_download: gr.update(
                            label="Download the photo after adjusting the KB size"
                        ),
                    }

            def change_color(colors):
                if colors == "自定义底色" or colors == "Custom Color":
                    return {custom_color: gr.update(visible=True)}
                else:
                    return {custom_color: gr.update(visible=False)}

            def change_size_mode(size_option_item):
                if (
                    size_option_item == "自定义尺寸"
                    or size_option_item == "Custom Size"
                ):
                    return {
                        custom_size: gr.update(visible=True),
                        size_list_row: gr.update(visible=False),
                    }
                elif (
                    size_option_item == "只换底"
                    or size_option_item == "Only Change Background"
                ):
                    return {
                        custom_size: gr.update(visible=False),
                        size_list_row: gr.update(visible=False),
                    }
                else:
                    return {
                        custom_size: gr.update(visible=False),
                        size_list_row: gr.update(visible=True),
                    }

            def change_image_kb(image_kb_option):
                if image_kb_option == "自定义" or image_kb_option == "Custom":
                    return {custom_image_kb: gr.update(visible=True)}
                else:
                    return {custom_image_kb: gr.update(visible=False)}

        # ---------------- 绑定事件 ----------------
        language_options.input(
            change_language,
            inputs=[language_options],
            outputs=[
                size_list_options,
                mode_options,
                color_options,
                img_but,
                render_options,
                image_kb_options,
                matting_model_options,
                custom_image_kb_size,
                notification,
                img_output_standard,
                img_output_standard_hd,
                img_output_layout,
                file_download,
            ],
        )

        color_options.input(
            change_color, inputs=[color_options], outputs=[custom_color]
        )

        mode_options.input(
            change_size_mode,
            inputs=[mode_options],
            outputs=[custom_size, size_list_row],
        )

        image_kb_options.input(
            change_image_kb, inputs=[image_kb_options], outputs=[custom_image_kb]
        )

        img_but.click(
            idphoto_inference,
            inputs=[
                img_input,
                mode_options,
                size_list_options,
                color_options,
                render_options,
                image_kb_options,
                custom_color_R,
                custom_color_G,
                custom_color_B,
                custom_size_height,
                custom_size_wdith,
                custom_image_kb_size,
                language_options,
                matting_model_options,
            ],
            outputs=[
                img_output_standard,
                img_output_standard_hd,
                img_output_layout,
                notification,
                file_download,
            ],
        )

    demo.launch(
        server_name=args.host,
        server_port=args.port,
        show_api=False,
        favicon_path=os.path.join(root_dir, "assets/hivision_logo.png"),
        root_path=args.root_path,
    )
