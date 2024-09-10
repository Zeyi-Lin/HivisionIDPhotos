# Copyright 2024 the LlamaFactory team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from demo.utils import csv_to_size_list
from demo.config import load_configuration
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
size_list_dict_CN = csv_to_size_list(os.path.join(base_dir, "assets/size_list_CN.csv"))
size_list_dict_EN = csv_to_size_list(os.path.join(base_dir, "assets/size_list_EN.csv"))
(
    size_list_config_CN,
    size_list_config_EN,
    color_list_dict_CN,
    color_list_dict_EN,
) = load_configuration(base_dir)


LOCALES = {
    "face_model": {
        "en": {
            "label": "Face detection model",
        },
        "zh": {
            "label": "人脸检测模型",
        },
    },
    "matting_model": {
        "en": {
            "label": "Matting model",
        },
        "zh": {
            "label": "抠图模型",
        },
    },
    "key_param": {
        "en": {
            "label": "Key Parameters",
        },
        "zh": {
            "label": "核心参数",
        },
    },
    "advance_param": {
        "en": {
            "label": "Advance Parameters",
        },
        "zh": {
            "label": "高级参数",
        },
    },
    "size_mode": {
        "en": {
            "label": "ID photo size options",
            "choices": ["Size List", "Only Change Background", "Custom Size"],
            "custom_size_eror": "The width should not be greater than the length; the length and width should not be less than 100, and no more than 1800.",
        },
        "zh": {
            "label": "证件照尺寸选项",
            "choices": ["尺寸列表", "只换底", "自定义尺寸"],
            "custom_size_eror": "宽度不应大于长度；长度和宽度不应小于100，不大于1800。",
        },
    },
    "size_list": {
        "en": {
            "label": "Size list",
            "choices": list(size_list_dict_EN.keys()),
            "develop": size_list_config_EN,
        },
        "zh": {
            "label": "预设尺寸",
            "choices": list(size_list_dict_CN.keys()),
            "develop": size_list_config_CN,
        },
    },
    "bg_color": {
        "en": {
            "label": "Background color",
            "choices": list(color_list_dict_EN.keys()) + ["Custom"],
            "develop": color_list_dict_EN,
        },
        "zh": {
            "label": "背景颜色",
            "choices": list(color_list_dict_CN.keys()) + ["自定义底色"],
            "develop": color_list_dict_CN,
        },
    },
    "button": {
        "en": {
            "label": "Start",
        },
        "zh": {
            "label": "开始制作",
        },
    },
    "head_measure_ratio": {
        "en": {
            "label": "Head ratio",
        },
        "zh": {
            "label": "面部比例",
        },
    },
    "top_distance": {
        "en": {
            "label": "Top distance",
        },
        "zh": {
            "label": "头距顶距离",
        },
    },
    "image_kb": {
        "en": {
            "label": "Set KB size",
            "choices": ["Not Set", "Custom"],
        },
        "zh": {
            "label": "设置 KB 大小",
            "choices": ["不设置", "自定义"],
        },
    },
    "image_kb_size": {
        "en": {
            "label": "KB size",
        },
        "zh": {
            "label": "KB 大小",
        },
    },
    "render_mode": {
        "en": {
            "label": "Render mode",
            "choices": [
                "Solid Color",
                "Up-Down Gradient (White)",
                "Center Gradient (White)",
            ],
        },
        "zh": {
            "label": "渲染方式",
            "choices": ["纯色", "上下渐变（白色）", "中心渐变（白色）"],
        },
    },
    # Tab3 - 水印工作台
    "watermark_tab": {
        "en": {
            "label": "Watermark",
        },
        "zh": {
            "label": "水印",
        },
    },
    "watermark_text": {
        "en": {
            "label": "Text",
            "value": "Hello",
            "placeholder": "up to 20 characters",
        },
        "zh": {
            "label": "水印文字",
            "value": "Hello",
            "placeholder": "最多20个字符",
        },
    },
    "watermark_color": {
        "en": {
            "label": "Color",
        },
        "zh": {
            "label": "水印颜色",
        },
    },
    "watermark_size": {
        "en": {
            "label": "Size",
        },
        "zh": {
            "label": "文字大小",
        },
    },
    "watermark_opacity": {
        "en": {
            "label": "Opacity",
        },
        "zh": {
            "label": "水印透明度",
        },
    },
    "watermark_angle": {
        "en": {
            "label": "Angle",
        },
        "zh": {
            "label": "水印角度",
        },
    },
    "watermark_space": {
        "en": {
            "label": "Space",
        },
        "zh": {
            "label": "水印间距",
        },
    },
    "watermark_switch": {
        "en": {
            "label": "Watermark",
            "value": "Not Add",
            "choices": ["Not Add", "Add"],
        },
        "zh": {
            "label": "水印",
            "value": "不添加",
            "choices": ["不添加", "添加"],
        },
    },
    # 输出结果
    "notification": {
        "en": {
            "label": "notification",
            "face_error": "The number of faces is not equal to 1, please upload an image with a single face. If the actual number of faces is 1, it may be an issue with the accuracy of the detection model. Please switch to a different face detection model on the left or raise a Github Issue to notify the author.",
        },
        "zh": {
            "label": "通知",
            "face_error": "人脸数不等于1，请上传单人照片。如果实际人脸数为1，可能是检测模型的准确度问题，请切换左侧不同的人脸检测模型或提出Github Issue通知作者。",
        },
    },
    "standard_photo": {
        "en": {
            "label": "Standard photo",
        },
        "zh": {
            "label": "标准照",
        },
    },
    "hd_photo": {
        "en": {
            "label": "HD photo",
        },
        "zh": {
            "label": "高清照",
        },
    },
    "standard_photo_png": {
        "en": {
            "label": "Matting Standard photo",
        },
        "zh": {
            "label": "透明标准照",
        },
    },
    "hd_photo_png": {
        "en": {
            "label": "Matting HD photo",
        },
        "zh": {
            "label": "透明高清照",
        },
    },
    "layout_photo": {
        "en": {
            "label": "Layout photo",
        },
        "zh": {
            "label": "六寸排版照",
        },
    },
    "download": {
        "en": {
            "label": "Download the photo after adjusting the KB size",
        },
        "zh": {
            "label": "下载调整 KB 大小后的照片",
        },
    },
    "matting_image": {
        "en": {
            "label": "Matting image",
        },
        "zh": {
            "label": "抠图图像",
        },
    },
}
