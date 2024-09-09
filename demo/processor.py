import numpy as np
from hivision import IDCreator
from hivision.error import FaceError, APIError
from hivision.utils import add_background, resize_image_to_kb
from hivision.creator.layout_calculator import (
    generate_layout_photo,
    generate_layout_image,
)
from hivision.creator.choose_handler import choose_handler
from demo.utils import add_watermark, range_check
import gradio as gr
import os
import time


class IDPhotoProcessor:
    def __init__(
        self,
        size_list_dict_CN,
        size_list_dict_EN,
        color_list_dict_CN,
        color_list_dict_EN,
    ):
        self.size_list_dict_CN = size_list_dict_CN
        self.size_list_dict_EN = size_list_dict_EN
        self.color_list_dict_CN = color_list_dict_CN
        self.color_list_dict_EN = color_list_dict_EN

    def process(
        self,
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
        watermark_option,
        watermark_text,
        watermark_text_color,
        watermark_text_size,
        watermark_text_opacity,
        watermark_text_angle,
        watermark_text_space,
        face_detect_option,
        head_measure_ratio=0.2,
        top_distance_max=0.12,
        top_distance_min=0.10,
    ):
        top_distance_min = top_distance_max - 0.02

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
                "The number of faces is not equal to 1, please upload an image with a single face. If the actual number of faces is 1, it may be an issue with the accuracy of the detection model. Please switch to a different face detection model on the left or raise a Github Issue to notify the author.": "人脸数量不等于 1，请上传单张人脸的图像。如果实际人脸数量为 1，可能是检测模型精度的问题，请在左边更换人脸检测模型或给作者提Github Issue。",
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
                "The number of faces is not equal to 1, please upload an image with a single face. If the actual number of faces is 1, it may be an issue with the accuracy of the detection model. Please switch to a different face detection model on the left or raise a Github Issue to notify the author.": "The number of faces is not equal to 1, please upload an image with a single face. If the actual number of faces is 1, it may be an issue with the accuracy of the detection model. Please switch to a different face detection model on the left or raise a Github Issue to notify the author.",
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
                idphoto_json["size"] = self.size_list_dict_CN[size_list_option]
            else:
                idphoto_json["size"] = self.size_list_dict_EN[size_list_option]
        # 如果尺寸模式选择的是自定义尺寸
        elif idphoto_json["size_mode"] == text_lang_map[language]["Custom Size"]:
            id_height = int(custom_size_height)
            id_width = int(custom_size_width)
            if (
                id_height < id_width
                or min(id_height, id_width) < 100
                or max(id_height, id_width) > 1800
            ):
                return [
                    gr.update(value=None),  # img_output_standard
                    gr.update(value=None),  # img_output_standard_hd
                    None,  # img_output_layout (assuming it should be None or not updated)
                    gr.update(  # notification
                        value=text_lang_map[language][
                            "The width should not be greater than the length; the length and width should not be less than 100, and no more than 1800."
                        ],
                        visible=True,
                    ),
                    None,  # file_download (assuming it should be None or not updated)
                ]

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
                idphoto_json["color_bgr"] = self.color_list_dict_CN[color_option]
            else:
                idphoto_json["color_bgr"] = self.color_list_dict_EN[color_option]

        # 如果输出 KB 大小选择的是自定义
        if idphoto_json["image_kb_mode"] == text_lang_map[language]["Custom"]:
            idphoto_json["custom_image_kb"] = custom_image_kb
        else:
            idphoto_json["custom_image_kb"] = None

        creator = IDCreator()
        choose_handler(creator, matting_model_option, face_detect_option)

        change_bg_only = idphoto_json["size_mode"] in [
            "只换底",
            "Only Change Background",
        ]

        try:
            result = creator(
                input_image,
                change_bg_only=change_bg_only,
                size=idphoto_json["size"],
                head_measure_ratio=head_measure_ratio,
                head_top_range=(top_distance_max, top_distance_min),
            )
        except FaceError:
            return [
                gr.update(value=None),  # img_output_standard
                gr.update(value=None),  # img_output_standard_hd
                gr.update(visible=False),  # img_output_layout
                gr.update(  # notification
                    value=text_lang_map[language][
                        "The number of faces is not equal to 1, please upload an image with a single face. If the actual number of faces is 1, it may be an issue with the accuracy of the detection model. Please switch to a different face detection model on the left or raise a Github Issue to notify the author."
                    ],
                    visible=True,
                ),
                None,  # file_download (assuming it should be None or have no update)
            ]

        except APIError as e:
            return [
                gr.update(value=None),  # img_output_standard
                gr.update(value=None),  # img_output_standard_hd
                gr.update(visible=False),  # img_output_layout
                gr.update(  # notification
                    value=f"Please make sure you have correctly set up the Face++ API Key and Secret.\nAPI Error\nStatus Code is {e.status_code}\nPossible errors are: {e}\n",
                    visible=True,
                ),
                None,  # file_download (assuming it should be None or have no update)
            ]

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

            # 如果只换底，就不生成排版照
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

                if watermark_option == "添加" or watermark_option == "Add":
                    result_layout_image = gr.update(
                        value=generate_layout_image(
                            add_watermark(
                                image=result_image_standard,
                                text=watermark_text,
                                size=watermark_text_size,
                                opacity=watermark_text_opacity,
                                angle=watermark_text_angle,
                                space=watermark_text_space,
                                color=watermark_text_color,
                            ),
                            typography_arr,
                            typography_rotate,
                            height=idphoto_json["size"][0],
                            width=idphoto_json["size"][1],
                        ),
                        visible=True,
                    )
                else:
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

            if idphoto_json["custom_image_kb"]:
                print("调整 kb 大小到", idphoto_json["custom_image_kb"], "kb")
                output_image_path = f"{os.path.join(os.path.dirname(__file__), 'demo/kb_output')}/{int(time.time())}.jpg"
                resize_image_to_kb(
                    result_image_standard,
                    output_image_path,
                    idphoto_json["custom_image_kb"],
                )
            else:
                output_image_path = None

            if watermark_option == "添加" or watermark_option == "Add":
                result_image_standard = add_watermark(
                    image=result_image_standard,
                    text=watermark_text,
                    size=watermark_text_size,
                    opacity=watermark_text_opacity,
                    angle=watermark_text_angle,
                    space=watermark_text_space,
                    color=watermark_text_color,
                )
                result_image_hd = add_watermark(
                    image=result_image_hd,
                    text=watermark_text,
                    size=watermark_text_size,
                    opacity=watermark_text_opacity,
                    angle=watermark_text_angle,
                    space=watermark_text_space,
                    color=watermark_text_color,
                )

            if output_image_path:
                return [
                    result_image_standard,  # img_output_standard
                    result_image_hd,  # img_output_standard_hd
                    result_layout_image,  # img_output_layout
                    gr.update(visible=False),  # notification
                    gr.update(visible=True, value=output_image_path),  # file_download
                ]
            else:
                return [
                    result_image_standard,  # img_output_standard
                    result_image_hd,  # img_output_standard_hd
                    result_layout_image,  # img_output_layout
                    gr.update(visible=False),  # notification
                    gr.update(visible=False),  # file_download
                ]
