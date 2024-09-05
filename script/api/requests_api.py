import requests
import base64
import argparse
import os


def base64_save(_base64_image_data, save_path):
    # 解码 Base64 数据并保存为 PNG 文件
    img_data = base64.b64decode(_base64_image_data)
    with open(save_path, "wb") as file:
        file.write(img_data)


# 读取本地图像文件并转换为Base64编码
def file_2_base64(file_path):
    with open(file_path, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode("utf-8")
    return encoded_string


# 发送请求到 /idphoto 接口
def request_idphoto(file_path, height, width):
    files = {"input_image": open(file_path, "rb")}
    data = {"height": int(height), "width": int(width)}
    response = requests.post(url, files=files, data=data)
    return response.json()


# 发送请求到 /add_background 接口
def request_add_background(file_path, color, kb=None):
    files = {"input_image": open(file_path, "rb")}
    data = {"color": str(color), "kb": kb}
    response = requests.post(url, files=files, data=data)
    return response.json()


# 发送请求到 /generate_layout_photos 接口
def request_generate_layout_photos(file_path, height, width, kb=None):
    files = {"input_image": open(file_path, "rb")}
    data = {"height": height, "width": width, "kb": kb}
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
    parser.add_argument("--height", help="证件照尺寸-高", default=413)
    parser.add_argument("--width", help="证件照尺寸-宽", default=295)
    parser.add_argument("-c", "--color", help="证件照背景色", default="638cce")
    parser.add_argument(
        "-k", "--kb", help="输出照片的 KB 值，仅对换底和制作排版照生效", default=None
    )
    args = parser.parse_args()

    url = f"{args.url}/{args.type}"  # 替换为实际的接口 URL
    # color = hex_to_rgb(args.color)
    # color = (color[2], color[1], color[0])

    if args.type == "idphoto":
        # 调用 /idphoto 接口
        idphoto_response = request_idphoto(
            args.input_image_dir, int(args.height), int(args.width)
        )

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

            print(f"请求{args.type}接口成功，已保存图像。")
        else:
            print("人脸数量不等于 1，请上传单张人脸的图像。")

    elif args.type == "add_background":
        # 调用 /add_background 接口
        add_background_response = request_add_background(
            args.input_image_dir, args.color, kb=args.kb
        )
        base64_image_data = add_background_response["image_base64"]
        base64_save(base64_image_data, args.output_image_dir)

        print(f"请求{args.type}接口成功，已保存图像。")

    elif args.type == "generate_layout_photos":
        # 调用 /generate_layout_photos 接口
        generate_layout_response = request_generate_layout_photos(
            args.input_image_dir, int(args.height), int(args.width), args.kb
        )
        base64_image_data = generate_layout_response["image_base64"]
        base64_save(base64_image_data, args.output_image_dir)

        print(f"请求{args.type}接口成功，已保存图像。")

    else:
        print("不支持的 API 类型，请检查输入参数。")
