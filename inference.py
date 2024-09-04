import os
import cv2
import ast
import argparse
import numpy as np
import onnxruntime
from utils import resize_image_to_kb
from src.face_judgement_align import IDphotos_create
from hivisionai.hycv.vision import add_background
from src.layoutCreate import generate_layout_photo, generate_layout_image


parser = argparse.ArgumentParser(description="HivisionIDPhotos 证件照制作推理程序。")

parser.add_argument(
    "-t",
    "--type",
    help="请求 API 的种类，有 idphoto、add_background 和 generate_layout_photos 可选",
    default="idphoto",
)
parser.add_argument("-i", "--input_image_dir", help="输入图像路径", required=True)
parser.add_argument("-o", "--output_image_dir", help="保存图像路径", required=True)
parser.add_argument("-s", "--size", help="证件照尺寸", default="(413,295)")
parser.add_argument("-c", "--color", help="证件照背景色", default="(255,255,255)")
parser.add_argument(
    "-k", "--kb", help="输出照片的 KB 值，仅对换底和制作排版照生效", default=None
)

args = parser.parse_args()

root_dir = os.path.dirname(os.path.abspath(__file__))

# 预加载 ONNX 模型
print("正在加载抠图模型...")
HY_HUMAN_MATTING_WEIGHTS_PATH = os.path.join(root_dir, "hivision_modnet.onnx")
sess = onnxruntime.InferenceSession(HY_HUMAN_MATTING_WEIGHTS_PATH)

input_image = cv2.imread(args.input_image_dir, cv2.IMREAD_UNCHANGED)


# 如果模式是生成证件照
if args.type == "idphoto":

    # 将字符串转为元组
    size = ast.literal_eval(args.size)

    (
        result_image_hd,
        result_image_standard,
        typography_arr,
        typography_rotate,
        _,
        _,
        _,
        _,
        status,
    ) = IDphotos_create(
        input_image,
        size=size,
        align=False,
        beauty=False,
        fd68=None,
        human_sess=sess,
        IS_DEBUG=False,
    )

    # 如果检测到人脸数量不等于 1（照片无人脸 or 多人脸）
    if status == 0:
        print("人脸数量不等于 1，请上传单张人脸的图像。")

    # 如果检测到人脸数量等于 1, 则返回标准证和高清照结果（png 4 通道图像）
    else:
        # 保存标准照
        cv2.imwrite(args.output_image_dir, result_image_standard)

        # 保存高清照
        file_name, file_extension = os.path.splitext(args.output_image_dir)
        new_file_name = file_name + "_hd" + file_extension
        cv2.imwrite(new_file_name, result_image_hd)

# 如果模式是添加背景
elif args.type == "add_background":

    # 将字符串转为元组
    color = ast.literal_eval(args.color)
    # 将元祖的 0 和 2 号数字交换
    color = (color[2], color[1], color[0])

    result_image = add_background(input_image, bgr=color)
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

    # 将字符串转为元组
    size = ast.literal_eval(args.size)

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
