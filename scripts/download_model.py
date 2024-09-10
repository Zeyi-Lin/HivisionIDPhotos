import os
import requests
import argparse
from tqdm import tqdm  # 导入 tqdm 库

# 获取当前脚本所在目录的上一级目录
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def download_file(url, save_path):
    try:
        print(f"Begin downloading: {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功

        # 获取文件总大小
        total_size = int(response.headers.get("content-length", 0))
        # 使用 tqdm 显示进度条
        with open(save_path, "wb") as file, tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc=os.path.basename(save_path),
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                bar.update(len(chunk))  # 更新进度条
        print(f"Download completed. Save to: {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Download failed: {e}")


def download_models(model_urls):
    # 下载每个模型
    for model_name, model_info in model_urls.items():
        # 指定下载保存的目录
        save_dir = model_info["location"]

        # 创建目录（如果不存在的话）
        os.makedirs(os.path.join(base_path, save_dir), exist_ok=True)

        url = model_info["url"]
        file_format = model_info["format"]

        # 特殊处理 rmbg-1.4 模型的文件名
        file_name = f"{model_name}.{file_format}"

        save_path = os.path.join(base_path, save_dir, file_name)

        # 检查文件是否已经存在
        if os.path.exists(save_path):
            print(f"File already exists, skipping download: {save_path}")
            continue

        # 下载文件
        download_file(url, save_path)


def main(models_to_download):
    # 模型权重的下载链接
    model_urls = {
        "hivision_modnet": {
            "url": "https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/download/pretrained-model/hivision_modnet.onnx",
            "format": "onnx",
            "location": "hivision/creator/weights",
        },
        "modnet_photographic_portrait_matting": {
            "url": "https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/download/pretrained-model/modnet_photographic_portrait_matting.onnx",
            "format": "onnx",
            "location": "hivision/creator/weights",
        },
        # "mnn_hivision_modnet": {
        #     "url": "https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/download/pretrained-model/mnn_hivision_modnet.mnn",
        #     "format": "mnn",
        # },
        "rmbg-1.4": {
            "url": "https://huggingface.co/briaai/RMBG-1.4/resolve/main/onnx/model.onnx?download=true",
            "format": "onnx",
            "location": "hivision/creator/weights",
        },
        "birefnet-v1-lite": {
            "url": "https://github.com/ZhengPeng7/BiRefNet/releases/download/v1/BiRefNet-general-bb_swin_v1_tiny-epoch_232.onnx",
            "format": "onnx",
            "location": "hivision/creator/weights",
        },
        "retinaface-resnet50": {
            "url": "https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/download/pretrained-model/retinaface-resnet50.onnx",
            "format": "onnx",
            "location": "hivision/creator/retinaface/weights",
        },
    }

    # 如果选择下载所有模型
    if "all" in models_to_download:
        selected_urls = model_urls
    else:
        selected_urls = {model: model_urls[model] for model in models_to_download}

    if not selected_urls:
        print("No valid models selected for download.")
        return

    download_models(selected_urls)


if __name__ == "__main__":
    MODEL_CHOICES = [
        "hivision_modnet",
        "modnet_photographic_portrait_matting",
        # "mnn_hivision_modnet",
        "rmbg-1.4",
        "birefnet-lite",
        "all",
    ]

    parser = argparse.ArgumentParser(description="Download matting models.")
    parser.add_argument(
        "--models",
        nargs="+",
        required=True,
        choices=MODEL_CHOICES,
        help='Specify which models to download (options: hivision_modnet, modnet_photographic_portrait_matting, mnn_hivision_modnet, rmbg-1.4, all). Only "all" will download all models.',
    )
    args = parser.parse_args()

    models_to_download = args.models if args.models else ["all"]
    main(models_to_download)
