import numpy as np
from hivision import IDCreator
from hivision.error import FaceError, APIError
from hivision.utils import (
    add_background,
    resize_image_to_kb,
    add_watermark,
    save_image_dpi_to_bytes,
)
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
        whitening_strength=0,
        image_dpi_option=False,
        custom_image_dpi=None,
        brightness_strength=0,
        contrast_strength=0,
        sharpen_strength=0,
        saturation_strength=0,
    ):
        # 初始化参数
        top_distance_min = top_distance_max - 0.02
        # 得到render_option在LOCALES["render_mode"][language]["choices"]中的索引
        render_option_index = LOCALES["render_mode"][language]["choices"].index(
            render_option
        )
        idphoto_json = self._initialize_idphoto_json(
            mode_option, color_option, render_option_index, image_kb_options
        )

        # 处理尺寸模式
        size_result = self._process_size_mode(
            idphoto_json,
            language,
            size_list_option,
            custom_size_height,
            custom_size_width,
        )
        if isinstance(size_result, list):
            return size_result  # 返回错误信息

        # 处理颜色模式
        self._process_color_mode(
            idphoto_json,
            language,
            color_option,
            custom_color_R,
            custom_color_G,
            custom_color_B,
        )

        # 如果设置了自定义KB大小
        if (
            idphoto_json["image_kb_mode"]
            == LOCALES["image_kb"][language]["choices"][-1]
        ):
            idphoto_json["custom_image_kb"] = custom_image_kb

        # 如果设置了自定义DPI大小
        if image_dpi_option == LOCALES["image_dpi"][language]["choices"][-1]:
            idphoto_json["custom_image_dpi"] = custom_image_dpi

        # 创建IDCreator实例并设置处理器
        creator = IDCreator()
        choose_handler(creator, matting_model_option, face_detect_option)

        # 生成证件照
        try:
            result = self._generate_id_photo(
                creator,
                input_image,
                idphoto_json,
                language,
                head_measure_ratio,
                top_distance_max,
                top_distance_min,
                whitening_strength,
                brightness_strength,
                contrast_strength,
                sharpen_strength,
                saturation_strength,
            )
        except (FaceError, APIError):
            return self._handle_photo_generation_error(language)

        # 后处理生成的照片
        return self._process_generated_photo(
            result,
            idphoto_json,
            language,
            watermark_option,
            watermark_text,
            watermark_text_size,
            watermark_text_opacity,
            watermark_text_angle,
            watermark_text_space,
            watermark_text_color,
        )

    def _initialize_idphoto_json(
        self,
        mode_option,
        color_option,
        render_option,
        image_kb_options,
    ):
        """初始化idphoto_json字典"""
        return {
            "size_mode": mode_option,
            "color_mode": color_option,
            "render_mode": render_option,
            "image_kb_mode": image_kb_options,
            "custom_image_kb": None,
            "custom_image_dpi": None,
        }

    def _process_size_mode(
        self,
        idphoto_json,
        language,
        size_list_option,
        custom_size_height,
        custom_size_width,
    ):
        """处理尺寸模式"""
        if idphoto_json["size_mode"] == LOCALES["size_mode"][language]["choices"][0]:
            idphoto_json["size"] = LOCALES["size_list"][language]["develop"][
                size_list_option
            ]
        elif idphoto_json["size_mode"] == LOCALES["size_mode"][language]["choices"][2]:
            id_height, id_width = int(custom_size_height), int(custom_size_width)
            if (
                id_height < id_width
                or min(id_height, id_width) < 100
                or max(id_height, id_width) > 1800
            ):
                return self._create_error_response(language)
            idphoto_json["size"] = (id_height, id_width)
        else:
            idphoto_json["size"] = (None, None)

    def _process_color_mode(
        self,
        idphoto_json,
        language,
        color_option,
        custom_color_R,
        custom_color_G,
        custom_color_B,
    ):
        """处理颜色模式"""
        if idphoto_json["color_mode"] == LOCALES["bg_color"][language]["choices"][-1]:
            idphoto_json["color_bgr"] = tuple(
                map(range_check, [custom_color_R, custom_color_G, custom_color_B])
            )
        else:
            hex_color = LOCALES["bg_color"][language]["develop"][color_option]
            idphoto_json["color_bgr"] = tuple(
                int(hex_color[i : i + 2], 16) for i in (0, 2, 4)
            )

    def _generate_id_photo(
        self,
        creator: IDCreator,
        input_image,
        idphoto_json,
        language,
        head_measure_ratio,
        top_distance_max,
        top_distance_min,
        whitening_strength,
        brightness_strength,
        contrast_strength,
        sharpen_strength,
        saturation_strength,
    ):
        """生成证件照"""
        change_bg_only = (
            idphoto_json["size_mode"] in LOCALES["size_mode"][language]["choices"][1]
        )
        return creator(
            input_image,
            change_bg_only=change_bg_only,
            size=idphoto_json["size"],
            head_measure_ratio=head_measure_ratio,
            head_top_range=(top_distance_max, top_distance_min),
            whitening_strength=whitening_strength,
            brightness_strength=brightness_strength,
            contrast_strength=contrast_strength,
            sharpen_strength=sharpen_strength,
            saturation_strength=saturation_strength,
        )

    def _handle_photo_generation_error(self, language):
        """处理照片生成错误"""
        return [gr.update(value=None) for _ in range(4)] + [
            gr.update(visible=False),
            gr.update(
                value=LOCALES["notification"][language]["face_error"], visible=True
            ),
            None,
        ]

    def _process_generated_photo(
        self,
        result,
        idphoto_json,
        language,
        watermark_option,
        watermark_text,
        watermark_text_size,
        watermark_text_opacity,
        watermark_text_angle,
        watermark_text_space,
        watermark_text_color,
    ):
        """处理生成的照片"""
        result_image_standard, result_image_hd, _, _, _, _ = result
        result_image_standard_png = np.uint8(result_image_standard)
        result_image_hd_png = np.uint8(result_image_hd)

        # 渲染背景
        result_image_standard, result_image_hd = self._render_background(
            result_image_standard, result_image_hd, idphoto_json
        )

        # 生成排版照片
        result_layout_image = self._generate_layout_image(
            idphoto_json,
            result_image_standard,
            language,
            watermark_option,
            watermark_text,
            watermark_text_size,
            watermark_text_opacity,
            watermark_text_angle,
            watermark_text_space,
            watermark_text_color,
        )

        # 添加水印
        if watermark_option == LOCALES["watermark_switch"][language]["choices"][1]:
            result_image_standard, result_image_hd = self._add_watermark(
                result_image_standard,
                result_image_hd,
                watermark_text,
                watermark_text_size,
                watermark_text_opacity,
                watermark_text_angle,
                watermark_text_space,
                watermark_text_color,
            )

        # 调整图片大小
        output_image_path = self._resize_image_if_needed(
            result_image_standard, idphoto_json
        )

        return self._create_response(
            result_image_standard,
            result_image_hd,
            result_image_standard_png,
            result_image_hd_png,
            result_layout_image,
            output_image_path,
        )

    def _render_background(self, result_image_standard, result_image_hd, idphoto_json):
        """渲染背景"""
        render_modes = {0: "pure_color", 1: "updown_gradient", 2: "center_gradient"}
        render_mode = render_modes[idphoto_json["render_mode"]]

        result_image_standard = np.uint8(
            add_background(
                result_image_standard, bgr=idphoto_json["color_bgr"], mode=render_mode
            )
        )
        result_image_hd = np.uint8(
            add_background(
                result_image_hd, bgr=idphoto_json["color_bgr"], mode=render_mode
            )
        )

        return result_image_standard, result_image_hd

    def _generate_layout_image(
        self,
        idphoto_json,
        result_image_standard,
        language,
        watermark_option,
        watermark_text,
        watermark_text_size,
        watermark_text_opacity,
        watermark_text_angle,
        watermark_text_space,
        watermark_text_color,
    ):
        """生成排版照片"""
        if idphoto_json["size_mode"] in LOCALES["size_mode"][language]["choices"][1]:
            return gr.update(visible=False)

        typography_arr, typography_rotate = generate_layout_photo(
            input_height=idphoto_json["size"][0],
            input_width=idphoto_json["size"][1],
        )

        image = result_image_standard
        if watermark_option == LOCALES["watermark_switch"][language]["choices"][1]:
            image = add_watermark(
                image=image,
                text=watermark_text,
                size=watermark_text_size,
                opacity=watermark_text_opacity,
                angle=watermark_text_angle,
                space=watermark_text_space,
                color=watermark_text_color,
            )

        return gr.update(
            value=generate_layout_image(
                image,
                typography_arr,
                typography_rotate,
                height=idphoto_json["size"][0],
                width=idphoto_json["size"][1],
            ),
            visible=True,
        )

    def _add_watermark(
        self,
        result_image_standard,
        result_image_hd,
        watermark_text,
        watermark_text_size,
        watermark_text_opacity,
        watermark_text_angle,
        watermark_text_space,
        watermark_text_color,
    ):
        """添加水印"""
        watermark_params = {
            "text": watermark_text,
            "size": watermark_text_size,
            "opacity": watermark_text_opacity,
            "angle": watermark_text_angle,
            "space": watermark_text_space,
            "color": watermark_text_color,
        }
        result_image_standard = add_watermark(
            image=result_image_standard, **watermark_params
        )
        result_image_hd = add_watermark(image=result_image_hd, **watermark_params)
        return result_image_standard, result_image_hd

    def _resize_image_if_needed(self, result_image_standard, idphoto_json):
        """如果需要，调整图片大小"""
        output_image_path = f"{os.path.join(os.path.dirname(os.path.dirname(__file__)), 'demo/kb_output')}/{int(time.time())}.jpg"
        # 如果设置了自定义KB大小
        if idphoto_json["custom_image_kb"]:
            resize_image_to_kb(
                result_image_standard,
                output_image_path,
                idphoto_json["custom_image_kb"],
                dpi=(
                    idphoto_json["custom_image_dpi"]
                    if idphoto_json["custom_image_dpi"]
                    else 300
                ),
            )
            return output_image_path
        # 如果只设置了dpi
        elif idphoto_json["custom_image_dpi"]:
            save_image_dpi_to_bytes(
                result_image_standard,
                output_image_path,
                dpi=idphoto_json["custom_image_dpi"],
            )
            return output_image_path

        return None

    def _create_response(
        self,
        result_image_standard,
        result_image_hd,
        result_image_standard_png,
        result_image_hd_png,
        result_layout_image,
        output_image_path,
    ):
        """创建响应"""
        response = [
            result_image_standard,
            result_image_hd,
            result_image_standard_png,
            result_image_hd_png,
            result_layout_image,
            gr.update(visible=False),
        ]
        if output_image_path:
            response.append(gr.update(visible=True, value=output_image_path))
        else:
            response.append(gr.update(visible=False))
        return response

    def _create_error_response(self, language):
        """创建错误响应"""
        return [gr.update(value=None) for _ in range(4)] + [
            None,
            gr.update(
                value=LOCALES["size_mode"][language]["custom_size_eror"], visible=True
            ),
            None,
        ]
