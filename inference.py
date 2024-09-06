import os
import cv2
import argparse
import numpy as np
import onnxruntime
from hivision.error import FaceError
from hivision.utils import hex_to_rgb, resize_image_to_kb, add_background
from hivision import IDCreator
from hivision.creator.layout_calculator import (
    generate_layout_photo,
    generate_layout_image,
)
from hivision.creator.human_matting import (
    extract_human_modnet_photographic_portrait_matting,
    extract_human,
)

parser = argparse.ArgumentParser(description="HivisionIDPhotos 证件照制作推理程序。")

creator = IDCreator()

INFERENCE_TYPE = [
    "idphoto",
    "human_matting",
    "add_background",
    "generate_layout_photos",
]
MATTING_MODEL = ["hivision_modnet", "modnet_photographic_portrait_matting"]
RENDER = [0, 1, 2]

parser.add_argument(
    "-t",
    "--type",
    help="请求 API 的种类",
    choices=INFERENCE_TYPE,
    default="idphoto",
)
parser.add_argument("-i", "--input_image_dir", help="输入图像路径", required=True)
parser.add_argument("-o", "--output_image_dir", help="保存图像路径", required=True)
parser.add_argument("--height", help="证件照尺寸-高", default=413)
parser.add_argument("--width", help="证件照尺寸-宽", default=295)
parser.add_argument("-c", "--color", help="证件照背景色", default="638cce")
parser.add_argument(
    "-k", "--kb", help="输出照片的 KB 值，仅对换底和制作排版照生效", default=None
)
parser.add_argument(
    "--matting_model",
    help="抠图模型权重",
    default="hivision_modnet",
    choices=MATTING_MODEL,
)
parser.add_argument(
    "-r",
    "--render",
    type=int,
    help="底色合成的模式，有 0:纯色、1:上下渐变、2:中心渐变 可选",
    choices=RENDER,
    default=0,
)

args = parser.parse_args()

# ------------------- 人像抠图模型选择 -------------------
if args.matting_model == "hivision_modnet":
    creator.matting_handler = extract_human
elif args.matting_model == "modnet_photographic_portrait_matting":
    creator.matting_handler = extract_human_modnet_photographic_portrait_matting

root_dir = os.path.dirname(os.path.abspath(__file__))
input_image = cv2.imread(args.input_image_dir, cv2.IMREAD_UNCHANGED)

# 如果模式是生成证件照
if args.type == "idphoto":
    # 将字符串转为元组
    size = (int(args.height), int(args.width))
    try:
        result = creator(input_image, size=size)
    except FaceError:
        print("人脸数量不等于 1，请上传单张人脸的图像。")
    else:
        # 保存标准照
        cv2.imwrite(args.output_image_dir, result.standard)

        # 保存高清照
        file_name, file_extension = os.path.splitext(args.output_image_dir)
        new_file_name = file_name + "_hd" + file_extension
        cv2.imwrite(new_file_name, result.hd)

# 如果模式是人像抠图
elif args.type == "human_matting":
    result = creator(input_image, change_bg_only=True)
    cv2.imwrite(args.output_image_dir, result.hd)

# 如果模式是添加背景
elif args.type == "add_background":

    render_choice = ["pure_color", "updown_gradient", "center_gradient"]

    # 将字符串转为元组
    color = hex_to_rgb(args.color)
    # 将元祖的 0 和 2 号数字交换
    color = (color[2], color[1], color[0])

    result_image = add_background(
        input_image, bgr=color, mode=render_choice[args.render]
    )
    result_image = result_image.astype(np.uint8)

    if args.kb:
        result_image = cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR)
        result_image = resize_image_to_kb(
            result_image, args.output_image_dir, int(args.kb)
        )
    else:
        cv2.imwrite(args.output_image_dir, result_image)

# 如果模式是生成排版照
elif args.type == "generate_layout_photos":

    size = (int(args.height), int(args.width))

    typography_arr, typography_rotate = generate_layout_photo(
        input_height=size[0], input_width=size[1]
    )

    result_layout_image = generate_layout_image(
        input_image,
        typography_arr,
        typography_rotate,
        height=size[0],
        width=size[1],
    )

    if args.kb:
        result_layout_image = cv2.cvtColor(result_layout_image, cv2.COLOR_RGB2BGR)
        result_layout_image = resize_image_to_kb(
            result_layout_image, args.output_image_dir, int(args.kb)
        )
    else:
        cv2.imwrite(args.output_image_dir, result_layout_image)
