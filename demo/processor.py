import numpy as np
from hivision import IDCreator
from hivision.error import FaceError, APIError
from hivision.utils import (
    add_background,
    add_background_with_image,
    resize_image_to_kb,
    add_watermark,
    save_image_dpi_to_bytes,
)
from hivision.creator.layout_calculator import (
    generate_layout_array,
    generate_layout_image,
)
from hivision.creator.choose_handler import choose_handler
from hivision.plugin.template.template_calculator import generte_template_photo
from demo.utils import range_check
import gradio as gr
import os
import cv2
import time
from demo.locales import LOCALES


base_path = os.path.dirname(os.path.abspath(__file__))

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
        custom_color_hex_value,
        custom_size_height,
        custom_size_width,
        custom_size_height_mm,
        custom_size_width_mm,
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
        plugin_option=[],
    ):        
        # 初始化参数
        top_distance_min = top_distance_max - 0.02
        # 得到render_option在LOCALES["render_mode"][language]["choices"]中的索引
        render_option_index = LOCALES["render_mode"][language]["choices"].index(
            render_option
        )
        # 读取插件选项
        # 人脸对齐选项
        if LOCALES["plugin"][language]["choices"][0] in plugin_option:
            face_alignment_option = True
        else:
            face_alignment_option = False
        # 排版裁剪线选项
        if LOCALES["plugin"][language]["choices"][1] in plugin_option:
            layout_photo_crop_line_option = True
        else:
            layout_photo_crop_line_option = False
        # JPEG格式选项
        if LOCALES["plugin"][language]["choices"][2] in plugin_option:
            jpeg_format_option = True
        else:
            jpeg_format_option = False
        # 五寸相纸选项
        if LOCALES["plugin"][language]["choices"][3] in plugin_option:
            five_inch_option = True
        else:
            five_inch_option = False
        
        idphoto_json = self._initialize_idphoto_json(
            mode_option, color_option, render_option_index, image_kb_options, layout_photo_crop_line_option, jpeg_format_option, five_inch_option
        )

        # 处理尺寸模式
        size_result = self._process_size_mode(
            idphoto_json,
            language,
            size_list_option,
            custom_size_height,
            custom_size_width,
            custom_size_height_mm,
            custom_size_width_mm,
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
            custom_color_hex_value,
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
                face_alignment_option,
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

    # 初始化idphoto_json字典
    def _initialize_idphoto_json(
        self,
        mode_option,
        color_option,
        render_option,
        image_kb_options,
        layout_photo_crop_line_option,
        jpeg_format_option,
        five_inch_option,
    ):
        """初始化idphoto_json字典"""
        return {
            "size_mode": mode_option,
            "color_mode": color_option,
            "render_mode": render_option,
            "image_kb_mode": image_kb_options,
            "custom_image_kb": None,
            "custom_image_dpi": None,
            "layout_photo_crop_line_option": layout_photo_crop_line_option,
            "jpeg_format_option": jpeg_format_option,
            "five_inch_option": five_inch_option,
        }

    # 处理尺寸模式
    def _process_size_mode(
        self,
        idphoto_json,
        language,
        size_list_option,
        custom_size_height,
        custom_size_width,
        custom_size_height_mm,
        custom_size_width_mm,
    ):
        """处理尺寸模式"""
        # 如果选择了尺寸列表
        if idphoto_json["size_mode"] == LOCALES["size_mode"][language]["choices"][0]:
            idphoto_json["size"] = LOCALES["size_list"][language]["develop"][
                size_list_option
            ]
        # 如果选择了自定义尺寸(px或mm)
        elif (
            idphoto_json["size_mode"] == LOCALES["size_mode"][language]["choices"][2]
            or idphoto_json["size_mode"] == LOCALES["size_mode"][language]["choices"][3]
        ):
            # 如果选择了自定义尺寸(px)
            if (
                idphoto_json["size_mode"]
                == LOCALES["size_mode"][language]["choices"][2]
            ):
                id_height, id_width = int(custom_size_height), int(custom_size_width)
            # 如果选择了自定义尺寸(mm)
            else:
                # 将mm转换为px
                id_height = int(custom_size_height_mm / 25.4 * 300)
                id_width = int(custom_size_width_mm / 25.4 * 300)
            # 检查尺寸像素是否在100到1800之间
            if (
                id_height < id_width
                or min(id_height, id_width) < 100
                or max(id_height, id_width) > 1800
            ):
                return self._create_error_response(language)
            idphoto_json["size"] = (id_height, id_width)
        # 如果选择了只换底
        else:
            idphoto_json["size"] = (None, None)

    # 处理颜色模式
    def _process_color_mode(
        self,
        idphoto_json,
        language,
        color_option,
        custom_color_R,
        custom_color_G,
        custom_color_B,
        custom_color_hex_value,
    ):
        """处理颜色模式"""
        # 如果选择了自定义颜色BGR
        if idphoto_json["color_mode"] == LOCALES["bg_color"][language]["choices"][-2]:
            idphoto_json["color_bgr"] = tuple(
                map(range_check, [custom_color_R, custom_color_G, custom_color_B])
            )
        # 如果选择了自定义颜色HEX
        elif idphoto_json["color_mode"] == LOCALES["bg_color"][language]["choices"][-1]:
            hex_color = custom_color_hex_value
            # 将十六进制颜色转换为RGB颜色，如果长度为6，则直接转换，如果长度为7，则去掉#号再转换
            if len(hex_color) == 6:
                idphoto_json["color_bgr"] = tuple(
                    int(hex_color[i : i + 2], 16) for i in (0, 2, 4)
                )
            elif len(hex_color) == 7:
                hex_color = hex_color[1:]
                idphoto_json["color_bgr"] = tuple(
                    int(hex_color[i : i + 2], 16) for i in (0, 2, 4)
                )
            else:
                raise ValueError(
                    "Invalid hex color. You can only use 6 or 7 characters. For example: #FFFFFF or FFFFFF"
                )
        # 如果选择了美式证件照
        elif idphoto_json["color_mode"] == LOCALES["bg_color"][language]["choices"][-3]:
            idphoto_json["color_bgr"] = (255, 255, 255)
        else:
            hex_color = LOCALES["bg_color"][language]["develop"][color_option]
            idphoto_json["color_bgr"] = tuple(
                int(hex_color[i : i + 2], 16) for i in (0, 2, 4)
            )

    # 生成证件照
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
        face_alignment_option,
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
            face_alignment=face_alignment_option,
        )

    # 处理照片生成错误
    def _handle_photo_generation_error(self, language):
        """处理照片生成错误"""
        return [gr.update(value=None) for _ in range(4)] + [
            gr.update(visible=False),
            gr.update(
                value=LOCALES["notification"][language]["face_error"], visible=True
            ),
            None,
        ]

    # 处理生成的照片
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
            result_image_standard, result_image_hd, idphoto_json, language
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
        
        # 生成排版照片
        result_image_layout, result_image_layout_visible = self._generate_image_layout(
            idphoto_json,
            result_image_standard,
            language,
        )
        
        # 生成模板照片
        result_image_template, result_image_template_visible = self._generate_image_template(
            idphoto_json,
            result_image_hd,
            language,
        )

        # 调整图片大小
        output_image_path_dict = self._save_image(
            result_image_standard,
            result_image_hd,
            result_image_layout,
            idphoto_json,
            format="jpeg" if idphoto_json["jpeg_format_option"] else "png",
        )
        
        # 返回
        if result_image_layout is not None:
            result_image_layout = output_image_path_dict["layout"]["path"]
            
        return self._create_response(
            output_image_path_dict["standard"]["path"],
            output_image_path_dict["hd"]["path"],
            result_image_standard_png,
            result_image_hd_png,
            gr.update(value=result_image_layout, visible=result_image_layout_visible),
            gr.update(value=result_image_template, visible=result_image_template_visible),
            gr.update(visible = result_image_template_visible),
        )

    # 渲染背景
    def _render_background(self, result_image_standard, result_image_hd, idphoto_json, language):
        """渲染背景"""
        render_modes = {0: "pure_color", 1: "updown_gradient", 2: "center_gradient"}
        render_mode = render_modes[idphoto_json["render_mode"]]

        if idphoto_json["color_mode"] != LOCALES["bg_color"][language]["choices"][-3]:
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
        # 如果选择了美式证件照
        else:
            result_image_standard = np.uint8(
                add_background_with_image(
                    result_image_standard, 
                    background_image=cv2.imread(os.path.join(base_path, "assets", "american-style.png"))
                )
            )
            result_image_hd = np.uint8(
                add_background_with_image(
                    result_image_hd, 
                    background_image=cv2.imread(os.path.join(base_path, "assets", "american-style.png"))
                )
            )
        return result_image_standard, result_image_hd

    # 生成排版照片
    def _generate_image_layout(
        self,
        idphoto_json,
        result_image_standard,
        language,
    ):
        """生成排版照片"""
        # 如果选择了只换底，则不生成排版照片
        if idphoto_json["size_mode"] in LOCALES["size_mode"][language]["choices"][1]:
            return None, False

        typography_arr, typography_rotate = generate_layout_array(
            input_height=idphoto_json["size"][0],
            input_width=idphoto_json["size"][1],
            LAYOUT_HEIGHT= 1205 if not idphoto_json["five_inch_option"] else 1051,
            LAYOUT_WIDTH= 1795 if not idphoto_json["five_inch_option"] else 1500,
        )
        
        result_image_layout = generate_layout_image(
            result_image_standard,
            typography_arr,
            typography_rotate,
            height=idphoto_json["size"][0],
            width=idphoto_json["size"][1],
            crop_line=idphoto_json["layout_photo_crop_line_option"],
            LAYOUT_HEIGHT=1205 if not idphoto_json["five_inch_option"] else 1051,
            LAYOUT_WIDTH=1795 if not idphoto_json["five_inch_option"] else 1500,
        )

        return result_image_layout, True
    
    # 生成模板照片
    def _generate_image_template(
        self,
        idphoto_json,
        result_image_hd,
        language,
    ):
        # 如果选择了只换底，则不生成模板照片
        if idphoto_json["size_mode"] in LOCALES["size_mode"][language]["choices"][1]:
            return None, False
        
        TEMPLATE_NAME_LIST = ["template_1", "template_2"]
        """生成模板照片"""
        result_image_template_list = []
        for template_name in TEMPLATE_NAME_LIST:
            result_image_template = generte_template_photo(
                template_name=template_name,
                input_image=result_image_hd,
            )
            result_image_template_list.append(result_image_template)
        return result_image_template_list, True

    # 添加水印
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

    def _save_image(
        self,
        result_image_standard,
        result_image_hd,
        result_image_layout,
        idphoto_json,
        format="png",
    ):
        # 设置输出路径（临时目录）
        import tempfile
        base_path = tempfile.mkdtemp()
        timestamp = int(time.time())
        output_paths = {
            "standard": {
                "path": f"{base_path}/{timestamp}_standard",
                "processed": False,
            },
            "hd": {"path": f"{base_path}/{timestamp}_hd", "processed": False},
            "layout": {"path": f"{base_path}/{timestamp}_layout", "processed": False},
        }

        # 获取自定义的KB和DPI值
        custom_kb = idphoto_json.get("custom_image_kb")
        custom_dpi = idphoto_json.get("custom_image_dpi", 300)

        # 处理同时有自定义KB和DPI的情况
        if custom_kb and custom_dpi:
            # 为所有输出路径添加DPI信息
            for key in output_paths:
                output_paths[key]["path"] += f"_{custom_dpi}dpi.{format}"
            # 为标准图像添加KB信息
            output_paths["standard"]["path"] = output_paths["standard"]["path"].replace(
                f".{format}", f"_{custom_kb}kb.{format}"
            )

            # 调整标准图像大小并保存
            resize_image_to_kb(
                result_image_standard,
                output_paths["standard"]["path"],
                custom_kb,
                dpi=custom_dpi,
            )
            # 保存高清图像和排版图像
            save_image_dpi_to_bytes(
                result_image_hd, output_paths["hd"]["path"], dpi=custom_dpi
            )
            if result_image_layout is not None:
                save_image_dpi_to_bytes(
                    result_image_layout, output_paths["layout"]["path"], dpi=custom_dpi
                )

            return output_paths

        # 只有自定义DPI的情况
        elif custom_dpi:
            for key in output_paths:
                # 保存所有图像，使用自定义DPI
                # 如果只换底，则不保存排版图像
                if key == "layout" and result_image_layout is None:
                    continue
                output_paths[key]["path"] += f"_{custom_dpi}dpi.{format}"
                save_image_dpi_to_bytes(
                    locals()[f"result_image_{key}"],
                    output_paths[key]["path"],
                    dpi=custom_dpi,
                )

            return output_paths

        # 只有自定义KB的情况
        elif custom_kb:
            output_paths["standard"]["path"] += f"_{custom_kb}kb.{format}"
            output_paths["hd"]["path"] += f".{format}"
            if not (key == "layout" and result_image_layout is None):
                output_paths[key]["path"] += f".{format}"
            
            # 只调整标准图像大小
            resize_image_to_kb(
                result_image_standard,
                output_paths["standard"]["path"],
                custom_kb,
                dpi=300,
            )
            
            # 保存高清图像和排版图像
            save_image_dpi_to_bytes(
                result_image_hd, output_paths["hd"]["path"], dpi=300
            )
            if result_image_layout is not None:
                save_image_dpi_to_bytes(
                    result_image_layout, output_paths["layout"]["path"], dpi=300
                )

            return output_paths
        # 没有自定义设置
        else: 
            output_paths["standard"]["path"] += f".{format}"
            output_paths["hd"]["path"] += f".{format}"
            output_paths["layout"]["path"] += f".{format}"
            
            # 保存所有图像
            save_image_dpi_to_bytes(
                result_image_standard, output_paths["standard"]["path"], dpi=300
            )
            save_image_dpi_to_bytes(
                result_image_hd, output_paths["hd"]["path"], dpi=300
            )
            if result_image_layout is not None:
                save_image_dpi_to_bytes(
                    result_image_layout, output_paths["layout"]["path"], dpi=300
                )
                
            return output_paths
            

    def _create_response(
        self,
        result_image_standard,
        result_image_hd,
        result_image_standard_png,
        result_image_hd_png,
        result_layout_image_gr,
        result_image_template_gr,
        result_image_template_accordion_gr,
    ):    
        """创建响应"""
        response = [
            result_image_standard,
            result_image_hd,
            result_image_standard_png,
            result_image_hd_png,
            result_layout_image_gr,
            result_image_template_gr,
            result_image_template_accordion_gr,
            gr.update(visible=False),
        ]

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
