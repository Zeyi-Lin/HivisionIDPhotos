import requests
import base64
import argparse
import ast
from PIL import Image
from io import BytesIO
from utils.image_utils import resize_image_to_kb
import os


def base64_save(base64_image_data, save_path, kb=None):
    # 解码 Base64 数据并保存为 PNG 文件
    img_data = base64.b64decode(base64_image_data)
    img = Image.open(BytesIO(img_data))

    if kb:
        img = resize_image_to_kb(img, save_path, float(kb))
    else:
        # 保存为本地 PNG 文件
        img.save(save_path, "PNG")


# 读取本地图像文件并转换为Base64编码
def file_2_base64(file_path):
    with open(file_path, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode("utf-8")
    return encoded_string


# 发送请求到 /idphoto 接口
def request_idphoto(file_path, size):
    files = {"input_image": open(file_path, "rb")}
    data = {"size": str(size)}
    response = requests.post(url, files=files, data=data)
    return response.json()


# 发送请求到 /add_background 接口
def request_add_background(file_path, color):
    files = {"input_image": open(file_path, "rb")}
    data = {"color": str(color)}
    response = requests.post(url, files=files, data=data)
    return response.json()


# 发送请求到 /generate_layout_photos 接口
def request_generate_layout_photos(file_path, size):
    files = {"input_image": open(file_path, "rb")}
    data = {"size": str(size)}
    response = requests.post(url, files=files, data=data)
    return response.json()


# 示例调用
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="HivisionIDPhotos 证件照制作推理程序。"
    )
    parser.add_argument(
        "-u", "--url", help="API 服务的 URL", default="http://localhost:8080"
    )

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

    url = f"{args.url}/{args.type}"  # 替换为实际的接口 URL
    size = ast.literal_eval(args.size)
    color = ast.literal_eval(args.color)

    if args.type == "idphoto":
        # 调用 /idphoto 接口
        idphoto_response = request_idphoto(args.input_image_dir, args.size)
        # print("ID Photo Response:", json.dumps(idphoto_response, indent=4))

        if idphoto_response["status"]:
            # 解码 Base64 数据并保存为 PNG 文件
            base64_image_data_standard = idphoto_response["image_base64_standard"]
            base64_image_data_standard_hd = idphoto_response["image_base64_hd"]

            file_name, file_extension = os.path.splitext(args.output_image_dir)
            # 定义新的文件路径（在原有的文件名后添加"_hd"）
            new_file_name = file_name + "_hd" + file_extension

            # 解码 Base64 数据并保存为 PNG 文件
            base64_save(base64_image_data_standard, args.output_image_dir)
            base64_save(base64_image_data_standard_hd, new_file_name)
        else:
            print("人脸数量不等于 1，请上传单张人脸的图像。")

    elif args.type == "add_background":
        # 调用 /add_background 接口
        add_background_response = request_add_background(args.input_image_dir, color)
        base64_image_data = add_background_response["image_base64"]
        base64_save(base64_image_data, args.output_image_dir, kb=args.kb)

    elif args.type == "generate_layout_photos":
        # 调用 /generate_layout_photos 接口
        generate_layout_response = request_generate_layout_photos(
            args.input_image_dir, size
        )
        base64_image_data = generate_layout_response["image_base64"]
        base64_save(base64_image_data, args.output_image_dir, kb=args.kb)

    else:
        print("不支持的 API 类型，请检查输入参数。")
