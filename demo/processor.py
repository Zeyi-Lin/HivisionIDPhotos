import numpy as np
from hivision import IDCreator
from hivision.error import FaceError, APIError
from hivision.utils import add_background, resize_image_to_kb, add_watermark
from hivision.creator.layout_calculator import (
    generate_layout_photo,
    generate_layout_image,
)
from hivision.creator.choose_handler import choose_handler
from demo.utils import range_check
import gradio as gr
import os
import time
from demo.locals import LOCALES


class IDPhotoProcessor:
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
            "custom_image_kb": None,
        }

        # 如果尺寸模式选择的是尺寸列表
        if idphoto_json["size_mode"] == LOCALES["size_mode"][language]["choices"][0]:
            idphoto_json["size"] = LOCALES["size_list"][language]["develop"][
                size_list_option
            ]
        # 如果尺寸模式选择的是自定义尺寸
        elif idphoto_json["size_mode"] == LOCALES["size_mode"][language]["choices"][2]:
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
                    gr.update(value=None),  # img_output_standard_png
                    gr.update(value=None),  # img_output_standard_hd_png
                    None,  # img_output_layout (assuming it should be None or not updated)
                    gr.update(  # notification
                        value=LOCALES["size_mode"][language]["custom_size_eror"],
                        visible=True,
                    ),
                    None,  # file_download (assuming it should be None or not updated)
                ]

            idphoto_json["size"] = (id_height, id_width)
        else:
            idphoto_json["size"] = (None, None)

        # 如果颜色模式选择的是自定义底色
        if idphoto_json["color_mode"] == LOCALES["bg_color"][language]["choices"][-1]:
            idphoto_json["color_bgr"] = (
                range_check(custom_color_R),
                range_check(custom_color_G),
                range_check(custom_color_B),
            )
        else:
            hex_color = idphoto_json["color_bgr"] = LOCALES["bg_color"][language][
                "develop"
            ][color_option]
            # 转为 RGB
            idphoto_json["color_bgr"] = tuple(
                int(hex_color[i : i + 2], 16) for i in (0, 2, 4)
            )

        # 如果输出 KB 大小选择的是自定义
        if (
            idphoto_json["image_kb_mode"]
            == LOCALES["image_kb"][language]["choices"][-1]
        ):
            idphoto_json["custom_image_kb"] = custom_image_kb

        creator = IDCreator()
        choose_handler(creator, matting_model_option, face_detect_option)

        # 是否只换底
        change_bg_only = (
            idphoto_json["size_mode"] in LOCALES["size_mode"][language]["choices"][1]
        )

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
                gr.update(value=None),  # img_output_standard_png
                gr.update(value=None),  # img_output_standard_hd_png
                gr.update(visible=False),  # img_output_layout
                gr.update(  # notification
                    value=LOCALES["notification"][language]["face_error"],
                    visible=True,
                ),
                None,  # file_download (assuming it should be None or have no update)
            ]

        except APIError as e:
            return [
                gr.update(value=None),  # img_output_standard
                gr.update(value=None),  # img_output_standard_hd
                gr.update(value=None),  # img_output_standard_png
                gr.update(value=None),  # img_output_standard_hd_png
                gr.update(visible=False),  # img_output_layout
                gr.update(  # notification
                    value=LOCALES["notification"][language]["face_error"],
                    visible=True,
                ),
                None,  # file_download (assuming it should be None or have no update)
            ]

        else:
            (result_image_standard, result_image_hd, _, _, _, _) = result

            result_image_standard_png = np.uint8(result_image_standard)
            result_image_hd_png = np.uint8(result_image_hd)

            if (
                idphoto_json["render_mode"]
                == LOCALES["render_mode"][language]["choices"][0]
            ):
                result_image_standard = np.uint8(
                    add_background(result_image_standard, bgr=idphoto_json["color_bgr"])
                )
                result_image_hd = np.uint8(
                    add_background(result_image_hd, bgr=idphoto_json["color_bgr"])
                )
            elif (
                idphoto_json["render_mode"]
                == LOCALES["render_mode"][language]["choices"][1]
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
            if change_bg_only:
                result_layout_image = gr.update(visible=False)
            else:
                typography_arr, typography_rotate = generate_layout_photo(
                    input_height=idphoto_json["size"][0],
                    input_width=idphoto_json["size"][1],
                )

                if (
                    watermark_option
                    == LOCALES["watermark_switch"][language]["choices"][1]
                ):
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

            # 如果添加水印
            if watermark_option == LOCALES["watermark_switch"][language]["choices"][1]:
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

            # 如果输出 KB 大小选择的是自定义
            if idphoto_json["custom_image_kb"]:
                print("调整 kb 大小到", idphoto_json["custom_image_kb"], "kb")
                output_image_path = f"{os.path.join(os.path.dirname(os.path.dirname(__file__)), 'demo/kb_output')}/{int(time.time())}.jpg"
                resize_image_to_kb(
                    result_image_standard,
                    output_image_path,
                    idphoto_json["custom_image_kb"],
                )
            else:
                output_image_path = None

            # 返回结果
            if output_image_path:
                return [
                    result_image_standard,  # img_output_standard
                    result_image_hd,  # img_output_standard_hd
                    result_image_standard_png,  # img_output_standard_png
                    result_image_hd_png,  # img_output_standard_hd_png
                    result_layout_image,  # img_output_layout
                    gr.update(visible=False),  # notification
                    gr.update(visible=True, value=output_image_path),  # file_download
                ]
            else:
                return [
                    result_image_standard,  # img_output_standard
                    result_image_hd,  # img_output_standard_hd
                    result_image_standard_png,  # img_output_standard_png
                    result_image_hd_png,  # img_output_standard_hd_png
                    result_layout_image,  # img_output_layout
                    gr.update(visible=False),  # notification
                    gr.update(visible=False),  # file_download
                ]
