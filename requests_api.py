import requests
import base64
from PIL import Image
from io import BytesIO
import argparse
import os

def base64_save(base64_image_data, save_path):
    # 解码Base64数据并保存为PNG文件
    img_data = base64.b64decode(base64_image_data)
    img = Image.open(BytesIO(img_data))
    # 保存为本地PNG文件
    img.save(save_path, "PNG")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HivisionIDPhotos证件照制作推理程序。")

    parser.add_argument("-u", "--url", help="API服务的URL", default="http://127.0.0.1:8080")
    parser.add_argument("-t", "--type", help="请求API的种类，有idphoto、add_background和generate_layout_photos可选",
                        default="idphoto")
    parser.add_argument("-i", "--input_image_dir", help="输入图像路径", required=True)
    parser.add_argument("-o", "--output_image_dir", help="保存图像路径", required=True)
    parser.add_argument("-s", "--size", help="证件照尺寸", default="(413,295)")
    parser.add_argument("-c", "--color", help="证件照背景色", default="(255,255,255)")

    args = parser.parse_args()

    url = f"{args.url}/{args.type}"  # 替换为实际的接口URL
    files = {'input_image': (open(args.input_image_dir, 'rb'))}  # 替换为实际的文件路径和文件名
    data = {"size": args.size, "color": args.color}

    response = requests.post(url, data=data, files=files)

    if response.status_code == 200:
        # 获取Base64编码的图像数据
        if args.type == "idphoto":
            response_json = response.json()

            status = response_json["status"]
            if status:

                base64_image_data_standard = response_json["img_output_standard"]
                base64_image_data_standard_hd = response_json["img_output_standard_hd"]

                # 解码Base64数据并保存为PNG文件
                base64_save(base64_image_data_standard, args.output_image_dir)

                file_name, file_extension = os.path.splitext(args.output_image_dir)
                # 定义新的文件路径（在原有的文件名后添加"_hd"）
                new_file_name = file_name + "_hd" + file_extension

                base64_save(base64_image_data_standard_hd, new_file_name)


                print(f"标准照保存至'{args.output_image_dir}'，高清照保存至'{new_file_name}'")

            else:
                print('人脸数量不等于1，请上传单张人脸的图像。')

        elif args.type == "add_background":
            response_json = response.json()

            status = response_json["status"]

            if status:
                base64_image_data = response_json["image"]
                base64_save(base64_image_data, args.output_image_dir)
                print(f"增加背景后的照片保存至'{args.output_image_dir}'。")
            else:
                print(f'遇到了一些问题，报错为{response_json["error"]}')

        elif args.type == "generate_layout_photos":
            response_json = response.json()

            status = response_json["status"]

            if status:
                base64_image_data = response_json["image"]
                base64_save(base64_image_data, args.output_image_dir)
                print(f"排版照保存至'{args.output_image_dir}'。")
            else:
                print(f'遇到了一些问题，报错为{response_json["error"]}')

    else:
        print("请求失败")
