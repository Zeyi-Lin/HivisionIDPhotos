import os
import requests

# 获取当前脚本所在目录的上一级目录
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def download_file(url, save_path):
    try:
        print(f"Begin downloading: {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Download completed. Save to: {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Download failed: {e}")


def download_matting_model():
    # 模型权重的下载链接
    model_urls = [
        "https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/download/pretrained-model/hivision_modnet.onnx",
        "https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/download/pretrained-model/modnet_photographic_portrait_matting.onnx",
    ]

    # 指定下载保存的目录
    save_dir = "hivision/creator/weights"

    # 创建目录（如果不存在的话）
    os.makedirs(os.path.join(base_path, save_dir), exist_ok=True)

    # 下载每个模型
    for url in model_urls:
        # 从 URL 中提取文件名
        file_name = url.split("/")[-1]
        save_path = os.path.join(base_path, save_dir, file_name)

        # 检查文件是否已经存在
        if os.path.exists(save_path):
            print(f"File already exists, skipping download: {save_path}")
            continue

        # 下载文件
        download_file(url, save_path)


if __name__ == "__main__":
    download_matting_model()
