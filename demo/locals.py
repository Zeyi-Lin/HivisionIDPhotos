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
        "ru": {
            "label": "Модель обнаружения лица",
        },
        "ko": {
            "label": "얼굴 감지 모델",
        },
    },
    "matting_model": {
        "en": {
            "label": "Matting model",
        },
        "zh": {
            "label": "抠图模型",
        },
        "ru": {
            "label": "Модель матирования",
        },
        "ko": {
            "label": "매팅 모델",
        },
    },
    "key_param": {
        "en": {
            "label": "Key Parameters",
        },
        "zh": {
            "label": "核心参数",
        },
        "ru": {
            "label": "Основные параметры",
        },
        "ko": {
            "label": "주요 매개변수",
        },
    },
    "advance_param": {
        "en": {
            "label": "Advance Parameters",
        },
        "zh": {
            "label": "高级参数",
        },
        "ru": {
            "label": "Расширенные параметры",
        },
        "ko": {
            "label": "고급 매개변수",
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
        "ru": {
            "label": "Размеры",
            "choices": [
                "Размер списка",
                "Только изменить фон",
                "Пользовательский размер",
            ],
            "custom_size_eror": "Ширина не должна быть больше длины; длина и ширина не должны быть меньше 100, и не более 1800.",
        },
        "ko": {
            "label": "증명사진 크기 옵션",
            "choices": ["크기 목록", "배경만 변경", "사용자 지정 크기"],
            "custom_size_eror": "너비는 길이보다 크지 않아야 합니다; 길이와 너비는 100 이상 1800 이하여야 합니다.",
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
        "ru": {
            "label": "Размеры",
            "choices": list(size_list_dict_EN.keys()),
            "develop": size_list_config_EN,
        },
        "ko": {
            "label": "크기 목록",
            "choices": list(size_list_dict_EN.keys()),
            "develop": size_list_config_EN,
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
        "ru": {
            "label": "Цвет фона",
            "choices": list(color_list_dict_EN.keys()) + ["Custom"],
            "develop": color_list_dict_EN,
        },
        "ko": {
            "label": "배경색",
            "choices": list(color_list_dict_EN.keys()) + ["사용자 지정"],
            "develop": color_list_dict_EN,
        },
    },
    "button": {
        "en": {
            "label": "Start",
        },
        "zh": {
            "label": "开始制作",
        },
        "ru": {
            "label": "Начать",
        },
        "ko": {
            "label": "시작",
        },
    },
    "head_measure_ratio": {
        "en": {
            "label": "Head ratio",
        },
        "zh": {
            "label": "面部比例",
        },
        "ru": {
            "label": "Соотношение головы",
        },
        "ko": {
            "label": "머리 비율",
        },
    },
    "top_distance": {
        "en": {
            "label": "Top distance",
        },
        "zh": {
            "label": "头距顶距离",
        },
        "ru": {
            "label": "Расстояние от верха",
        },
        "ko": {
            "label": "상단 거리",
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
        "ru": {
            "label": "Установить размер KB",
            "choices": ["Не установлен", "Custom"],
        },
        "ko": {
            "label": "KB 크기 설정",
            "choices": ["설정 안 함", "사용자 지정"],
        },
    },
    "image_kb_size": {
        "en": {
            "label": "KB size",
        },
        "zh": {
            "label": "KB 大小",
        },
        "ru": {
            "label": "Размер KB",
        },
        "ko": {
            "label": "KB 크기",
        },
    },
    "image_dpi": {
        "en": {
            "label": "Set DPI",
            "choices": ["Not Set", "Custom"],
        },
        "zh": {
            "label": "设置 DPI 大小",
            "choices": ["不设置", "自定义"],
        },
        "ru": {
            "label": "Установить размер DPI",
            "choices": ["Не установлен", "Custom"],
        },
        "ko": {
            "label": "DPI 설정",
            "choices": ["설정 안 함", "사용자 지정"],
        },
    },
    "image_dpi_size": {
        "en": {
            "label": "DPI size",
        },
        "zh": {
            "label": "DPI 大小",
        },
        "ru": {
            "label": "Размер DPI",
        },
        "ko": {
            "label": "DPI 크기",
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
        "ru": {
            "label": "Режим рендеринга",
            "choices": [
                "Solid Color",
                "Up-Down Gradient (White)",
                "Center Gradient (White)",
            ],
        },
        "ko": {
            "label": "렌더링 모드",
            "choices": [
                "단색",
                "위-아래 그라데이션 (흰색)",
                "중앙 그라데이션 (흰색)",
            ],
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
        "ru": {
            "label": "Водяной знак",
        },
        "ko": {
            "label": "워터마크",
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
        "ru": {
            "label": "Текст",
            "value": "Hello",
            "placeholder": "до 20 символов",
        },
        "ko": {
            "label": "텍스트",
            "value": "Hello",
            "placeholder": "최대 20자",
        },
    },
    "watermark_color": {
        "en": {
            "label": "Color",
        },
        "zh": {
            "label": "水印颜色",
        },
        "ru": {
            "label": "Цвет",
        },
        "ko": {
            "label": "색상",
        },
    },
    "watermark_size": {
        "en": {
            "label": "Size",
        },
        "zh": {
            "label": "文字大小",
        },
        "ru": {
            "label": "Размер",
        },
        "ko": {
            "label": "크기",
        },
    },
    "watermark_opacity": {
        "en": {
            "label": "Opacity",
        },
        "zh": {
            "label": "水印透明度",
        },
        "ru": {
            "label": "Прозрачность",
        },
        "ko": {
            "label": "불투명도",
        },
    },
    "watermark_angle": {
        "en": {
            "label": "Angle",
        },
        "zh": {
            "label": "水印角度",
        },
        "ru": {
            "label": "Угол",
        },
        "ko": {
            "label": "각도",
        },
    },
    "watermark_space": {
        "en": {
            "label": "Space",
        },
        "zh": {
            "label": "水印间距",
        },
        "ru": {
            "label": "Расстояние",
        },
        "ko": {
            "label": "간격",
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
        "ru": {
            "label": "Водяной знак",
            "value": "Не добавлять",
            "choices": ["Не добавлять", "Добавить"],
        },
        "ko": {
            "label": "워터마크",
            "value": "추가하지 않음",
            "choices": ["추가하지 않음", "추가"],
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
        "ru": {
            "label": "Уведомление",
            "face_error": "Количество лиц не равно 1, пожалуйста, загрузите изображение с одним лицом. Если фактическое количество лиц равно 1, это может быть проблемой точности модели распознавания. Пожалуйста, переключитесь на другой модель распознавания лица на левом или создайте проблему на Github, чтобы уведомить автора.",
        },
        "ko": {
            "label": "알림",
            "face_error": "얼굴 수가 1이 아닙니다. 단일 얼굴이 있는 이미지를 업로드해 주세요. 실제 얼굴 수가 1인 경우 감지 모델의 정확도 문제일 수 있습니다. 왼쪽에서 다른 얼굴 감지 모델로 전환하거나 Github Issue를 제기하여 작성자에게 알려주세요.",
        },
    },
    "standard_photo": {
        "en": {
            "label": "Standard photo",
        },
        "zh": {
            "label": "标准照",
        },
        "ru": {
            "label": "Стандартная фотография",
        },
        "ko": {
            "label": "표준 사진",
        },
    },
    "hd_photo": {
        "en": {
            "label": "HD photo",
        },
        "zh": {
            "label": "高清照",
        },
        "ru": {
            "label": "Высококачественная фотография",
        },
        "ko": {
            "label": "HD 사진",
        },
    },
    "standard_photo_png": {
        "en": {
            "label": "Matting Standard photo",
        },
        "zh": {
            "label": "透明标准照",
        },
        "ru": {
            "label": "Стандартная фотография с прозрачным фоном",
        },
        "ko": {
            "label": "매팅 표준 사진",
        },
    },
    "hd_photo_png": {
        "en": {
            "label": "Matting HD photo",
        },
        "zh": {
            "label": "透明高清照",
        },
        "ru": {
            "label": "Стандартная фотография с прозрачным фоном",
        },
        "ko": {
            "label": "매팅 HD 사진",
        },
    },
    "layout_photo": {
        "en": {
            "label": "Layout photo",
        },
        "zh": {
            "label": "六寸排版照",
        },
        "ru": {
            "label": "Фотография с расположением",
        },
        "ko": {
            "label": "레이아웃 사진",
        },
    },
    "download": {
        "en": {
            "label": "Download the photo after adjusting the DPI or KB size",
        },
        "zh": {
            "label": "下载调整 DPI 或 KB 大小后的照片",
        },
        "ru": {
            "label": "Скачать фото после настройки размера DPI или KB",
        },
        "ko": {
            "label": "DPI 또는 KB 크기 조정 후 사진 다운로드",
        },
    },
    "matting_image": {
        "en": {
            "label": "Matting image",
        },
        "zh": {
            "label": "抠图图像",
        },
        "ru": {
            "label": "Изображение с прозрачным фоном",
        },
        "ko": {
            "label": "매팅 이미지",
        },
    },
    "beauty_tab": {
        "en": {
            "label": "Beauty",
        },
        "zh": {
            "label": "美颜",
        },
        "ru": {
            "label": "Красота",
        },
        "ko": {
            "label": "뷰티",
        },
    },
    "whitening_strength": {
        "en": {
            "label": "whitening strength",
        },
        "zh": {
            "label": "美白强度",
        },
        "ru": {
            "label": "Степень белизны",
        },
        "ko": {
            "label": "미백 강도",
        },
    },
}
