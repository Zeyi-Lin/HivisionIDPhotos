<div align="center">

<img alt="hivision_logo" src="assets/hivision_logo.png" width=120 height=120>
<h1>HivisionIDPhoto</h1>

English / [中文](README.md) / [日本語](README_JP.md) / [한국어](README_KO.md)

[![][release-shield]][release-link]
[![][dockerhub-shield]][dockerhub-link]
[![][github-stars-shield]][github-stars-link]
[![][github-issues-shield]][github-issues-link]
[![][github-contributors-shield]][github-contributors-link]
[![][github-forks-shield]][github-forks-link]
[![][license-shield]][license-link]  
[![][wechat-shield]][wechat-link]
[![][spaces-shield]][spaces-link]
[![][swanhub-demo-shield]][swanhub-demo-link]

[![][trendshift-shield]][trendshift-link]

<img src="assets/demoImage.png" width=900>

</div>

<br>

> **Related Projects**:
>
> - [SwanLab](https://github.com/SwanHubX/SwanLab): Used for analyzing, monitoring, and collaborating with lab colleagues throughout the training of portrait matting models, significantly improving training efficiency.

<br>

# Table of Contents

- [Project Updates](#-project-updates)
- [Overview](#overview)
- [Preparation](#-preparation)
- [Community]()
- [Running Demo](#-running-gradio-demo)
- [Python Inference](#-python-inference)
- [API Service Deployment](#️-deploying-api-service)
- [Docker Deployment](#-docker-deployment)
- [Contact Us](#-contact-us)
- [Contributors](#contributors)

<br>

# 🤩 Project Updates

- Online Experience: [![SwanHub Demo](https://img.shields.io/static/v1?label=Demo&message=SwanHub%20Demo&color=blue)](https://swanhub.co/ZeYiLin/HivisionIDPhotos/demo)、[![Spaces](https://img.shields.io/badge/🤗-Open%20in%20Spaces-blue)](https://huggingface.co/spaces/TheEeeeLin/HivisionIDPhotos)

- 2024.09.08: Added a new background removal model [RMBG-1.4](https://huggingface.co/briaai/RMBG-1.4) | ComfyUI Workflow - [HivisionIDPhotos-ComfyUI](https://github.com/AIFSH/HivisionIDPhotos-ComfyUI) contributed by [AIFSH](https://github.com/AIFSH/HivisionIDPhotos-ComfyUI)
- 2024.09.07: Added **Face Detection API Option** [Face++](docs/face++_EN.md) for higher accuracy face detection
- 2024.09.06: Added new matting model [modnet_photographic_portrait_matting.onnx](https://github.com/ZHKKKe/MODNet)
- 2024.09.05: Updated [Restful API Documentation](docs/api_EN.md)
- 2024.09.02: Updated **Photo Size Adjustment**
- 2023.12.01: Updated **API Deployment (based on fastapi)**
- 2023.06.20: Updated **Preset Size Menu**

# Overview

> 🚀 Thank you for your interest in our work. You may also want to check out our other achievements in the field of image processing. Feel free to contact us at: zeyi.lin@swanhub.co.

HivisionIDPhoto aims to develop a practical and systematic algorithm for intelligent ID photo creation.

It utilizes a complete AI model workflow to recognize various user photo scenarios, perform matting, and generate ID photos.

**HivisionIDPhoto can achieve:**

1. Lightweight matting (purely offline, fast inference with just **CPU**)
2. Generating standard ID photos of different sizes and six-inch layout photos
3. Supporting pure offline or edge-cloud inference
4. Beauty enhancement (waiting)
5. Intelligent formal wear swapping (waiting)

<div align="center">
<img src="assets/harry.png" width=900>
</div>

---

If HivisionIDPhoto is helpful to you, please star this repo or recommend it to your friends to solve urgent ID photo creation issues!

<br>

# 🏠 Community

We share some interesting applications and extensions of HivisionIDPhotos built by the community:

- [HivisionIDPhotos-windows-GUI](https://github.com/zhaoyun0071/HivisionIDPhotos-windows-GUI): A Windows client application built by [zhaoyun0071](https://github.com/zhaoyun0071)
- [HivisionIDPhotos-ComfyUI](https://github.com/AIFSH/HivisionIDPhotos-ComfyUI): ComfyUI workflow for ID photo processing, built by [AIFSH](https://github.com/AIFSH/HivisionIDPhotos-ComfyUI)

[![](assets/comfyui.png)](https://github.com/AIFSH/HivisionIDPhotos-ComfyUI)

<br>

# 🔧 Preparation

Environment installation and dependencies:
- Python >= 3.7 (mainly tested on Python 3.10)
- OS: Linux, Windows, MacOS

## 1. Clone the Project

```bash
git clone https://github.com/Zeyi-Lin/HivisionIDPhotos.git
cd  HivisionIDPhotos
```

## 2. Install Dependencies

> It is recommended to create a python3.10 virtual environment using conda, then execute the following commands:

```bash
pip install -r requirements.txt
pip install -r requirements-app.txt
```

## 3. Download Weight Files

**Option 1: Script Download**

```bash
python scripts/download_model.py --models all
```

**Option 2: Direct Download**

Save in the project's `hivision/creator/weights` directory:
- `modnet_photographic_portrait_matting.onnx` (24.7MB): Official weights from [MODNet](https://github.com/ZHKKKe/MODNet), [Download](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/download/pretrained-model/modnet_photographic_portrait_matting.onnx)
- `hivision_modnet.onnx` (24.7MB): A matting model better suited for solid background swapping, [Download](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/download/pretrained-model/hivision_modnet.onnx)
- `mnn_hivision_modnet.mnn` (24.7MB): MNN converted matting model by [zjkhahah](https://github.com/zjkhahah), [Download](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/download/pretrained-model/mnn_hivision_modnet.mnn)
- `rmbg-1.4.onnx` (176.2MB): Open source matting model from [BRIA AI](https://huggingface.co/briaai/RMBG-1.4), [download](https://huggingface.co/briaai/RMBG-1.4/resolve/main/onnx/model.onnx?download=true) it and rename it to `rmbg-1.4.onnx`.

## 4. Face Detection Model Configuration

> This is an optional step.

| Extended Face Detection Model | Description | Documentation |
| -- | -- | -- |
| MTCNN | **Offline** face detection model, high-performance CPU inference, default model with lower detection accuracy | Directly use after cloning this project |
| Face++ | An online face detection API launched by Megvii, with higher detection accuracy, [Official Documentation](https://console.faceplusplus.com.cn/documents/4888373) | [Usage Documentation](docs/face++_EN.md)|

<br>

# 🚀 Running Gradio Demo

```bash
python app.py
```

Running the program will generate a local web page where you can interact with and perform ID photo operations.

<br>

# 🚀 Python Inference

Core parameters:

- `-i`: Input image path
- `-o`: Output image path
- `-t`: Inference type, options include idphoto, human_matting, add_background, generate_layout_photos
- `--matting_model`: Selection of portrait matting model weights, options are `hivision_modnet`, `modnet_photographic_portrait_matting`

For more parameters, you can check using `python inference.py --help`.

## 1. ID Photo Creation

Input 1 photo to obtain 1 standard ID photo and 1 high-definition ID photo in 4-channel transparent PNG format.

```python
python inference.py -i demo/images/test.jpg -o ./idphoto.png --height 413 --width 295
```

## 2. Portrait Matting

```python
python inference.py -t human_matting -i demo/images/test.jpg -o ./idphoto_matting.png --matting_model hivision_modnet
```

## 3. Adding Background Color to Transparent Image

Input 1 4-channel transparent PNG to obtain 1 image with added background color.

```python
python inference.py -t add_background -i ./idphoto.png -o ./idhoto_ab.jpg  -c 4f83ce -k 30 -r 1
```

## 4. Obtain Six-Inch Layout Photo

Input 1 3-channel photo to obtain 1 six-inch layout photo.

```python
python inference.py -t generate_layout_photos -i ./idhoto_ab.jpg -o ./idhoto_layout.jpg  --height 413 --width 295 -k 200
```

<br>

# ⚡️ Deploying API Service

## Start Backend

```
python deploy_api.py
```

## Request API Service - Python Request

> For request methods, please refer to the [API Documentation](docs/api_EN.md), including [cURL](docs/api_EN.md#curl-request-examples), [Python](docs/api_EN.md#python-request-example), [Java](docs/api_EN.md#java-request-example), [Javascript](docs/api_EN.md#javascript-request-examples) request examples.

### 1. ID Photo Creation

Input 1 photo to obtain 1 standard ID photo and 1 high-definition ID photo in 4-channel transparent PNG format.

```python
import requests

url = "http://127.0.0.1:8080/idphoto"
input_image_path = "demo/images/test.jpg"

files = {"input_image": open(input_image_path, "rb")}
data = {"height": 413, "width": 295}

response = requests.post(url, files=files, data=data).json()

# response is a json-formatted dictionary containing status, image_base64_standard, and image_base64_hd
print(response)

```

### 2. Adding Background Color

Input 1 4-channel transparent PNG to obtain 1 image with added background color.

```python
import requests

url = "http://127.0.0.1:8080/add_background"
input_image_path = "test.png"

files = {"input_image": open(input_image_path, "rb")}
data = {"color": '638cce', 'kb': None}

response = requests.post(url, files=files, data=data).json()

# response is a json-formatted dictionary containing status and image_base64
print(response)
```

### 3. Obtain Six-Inch Layout Photo

Input 1 3-channel photo to obtain 1 six-inch layout photo.

```python
import requests

url = "http://127.0.0.1:8080/generate_layout_photos"
input_image_path = "test.jpg"

files = {"input_image": open(input_image_path, "rb")}
data = {"height": 413, "width": 295, "kb": 200}

response = requests.post(url, files=files, data=data).json()

# response is a json-formatted dictionary containing status and image_base64
print(response)
```

<br>

# 🐳 Docker Deployment

## 1. Pull or Build the Image

> Choose one of the following three methods.

**Option 1: Pull the latest image:**

```bash
docker pull linzeyi/hivision_idphotos
```

**Option 2: Directly build the image from Dockerfile:**

After ensuring that the model weight file [hivision_modnet.onnx](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/tag/pretrained-model) is placed in `hivision/creator/weights`, execute the following in the project root directory:

```bash
docker build -t linzeyi/hivision_idphotos .
```

**Option 3: Build using Docker Compose:**

After ensuring that the model weight file [hivision_modnet.onnx](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/tag/pretrained-model) is placed in `hivision/creator/weights`, execute the following in the project root directory:

```bash
docker compose build
```

## 2. Run the Service

**Start Gradio Demo Service**

Run the following command, and you can access it locally at [http://127.0.0.1:7860](http://127.0.0.1:7860/).

```bash
docker run -d -p 7860:7860 linzeyi/hivision_idphotos
```

**Start API Backend Service**

```bash
docker run -d -p 8080:8080 linzeyi/hivision_idphotos python3 deploy_api.py
```

**Start Both Services Simultaneously**

```bash
docker compose up -d
```

## Environment Variables

This project provides some additional configuration options that can be set using environment variables:

| Environment Variable | Type | Description | Example |
| -- | -- | -- | -- |
| FACE_PLUS_API_KEY | Optional | This is the API key you applied for in the Face++ console | `7-fZStDJ····` |
| FACE_PLUS_API_SECRET | Optional | The Secret corresponding to the Face++ API key | `VTee824E····` |

Example of using environment variables with Docker:
```bash
docker run  -d -p 7860:7860 \
    -e FACE_PLUS_API_KEY=7-fZStDJ···· \
    -e FACE_PLUS_API_SECRET=VTee824E···· \
    linzeyi/hivision_idphotos 
```

<br>

# 📖 Citations

1. MTCNN:

```bibtex
@software{ipazc_mtcnn_2021,
    author = {ipazc},
    title = {{MTCNN}},
    url = {https://github.com/ipazc/mtcnn},
    year = {2021},
    publisher = {GitHub}
}
```

2. ModNet:

```bibtex
@software{zhkkke_modnet_2021,
    author = {ZHKKKe},
    title = {{ModNet}},
    url = {https://github.com/ZHKKKe/MODNet},
    year = {2021},
    publisher = {GitHub}
}
```

<br>

# 💻 Development Tips

**1. How to Modify Preset Sizes?**

Modify [size_list_CN.csv](demo/size_list_CN.csv) and run app.py again, where the first column is the size name, the second column is height, and the third column is width.

<br>

# 📧 Contact Us

If you have any questions, please email zeyi.lin@swanhub.co.

<br>

# Contributors

<a href="https://github.com/Zeyi-Lin/HivisionIDPhotos/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Zeyi-Lin/HivisionIDPhotos" />
</a>

[Zeyi-Lin](https://github.com/Zeyi-Lin)、[SAKURA-CAT](https://github.com/SAKURA-CAT)、[Feudalman](https://github.com/Feudalman)、[swpfY](https://github.com/swpfY)、[Kaikaikaifang](https://github.com/Kaikaikaifang)、[ShaohonChen](https://github.com/ShaohonChen)、[KashiwaByte](https://github.com/KashiwaByte)

<br>

# StarHistory

[![Star History Chart](https://api.star-history.com/svg?repos=Zeyi-Lin/HivisionIDPhotos&type=Date)](https://star-history.com/#Zeyi-Lin/HivisionIDPhotos&Date)

[github-stars-shield]: https://img.shields.io/github/stars/zeyi-lin/hivisionidphotos?color=ffcb47&labelColor=black&style=flat-square
[github-stars-link]: https://github.com/zeyi-lin/hivisionidphotos/stargazers

[swanhub-demo-shield]: https://swanhub.co/git/repo/SwanHub%2FAuto-README/file/preview?ref=main&path=swanhub.svg
[swanhub-demo-link]: https://swanhub.co/ZeYiLin/HivisionIDPhotos/demo

[spaces-shield]: https://img.shields.io/badge/🤗-Open%20in%20Spaces-blue
[spaces-link]: https://huggingface.co/spaces/TheEeeeLin/HivisionIDPhotos

<!-- WeChat group link -->
[wechat-shield]: https://img.shields.io/badge/WeChat-微信-4cb55e
[wechat-link]: https://docs.qq.com/doc/DUkpBdk90eWZFS2JW

<!-- Github Release -->
[release-shield]: https://img.shields.io/github/v/release/zeyi-lin/hivisionidphotos?color=369eff&labelColor=black&logo=github&style=flat-square
[release-link]: https://github.com/zeyi-lin/hivisionidphotos/releases

[license-shield]: https://img.shields.io/badge/license-apache%202.0-white?labelColor=black&style=flat-square
[license-link]: https://github.com/Zeyi-Lin/HivisionIDPhotos/blob/master/LICENSE

[github-issues-shield]: https://img.shields.io/github/issues/zeyi-lin/hivisionidphotos?color=ff80eb&labelColor=black&style=flat-square
[github-issues-link]: https://github.com/zeyi-lin/hivisionidphotos/issues

[dockerhub-shield]: https://img.shields.io/docker/v/linzeyi/hivision_idphotos?color=369eff&label=docker&labelColor=black&logoColor=white&style=flat-square
[dockerhub-link]: https://hub.docker.com/r/linzeyi/hivision_idphotos/tags

[trendshift-shield]: https://trendshift.io/api/badge/repositories/11622
[trendshift-link]: https://trendshift.io/repositories/11622

[hellogithub-shield]: https://abroad.hellogithub.com/v1/widgets/recommend.svg?rid=8ea1457289fb4062ba661e5299e733d6&claim_uid=Oh5UaGjfrblg0yZ
[hellogithub-link]: https://hellogithub.com/repository/8ea1457289fb4062ba661e5299e733d6

[github-contributors-shield]: https://img.shields.io/github/contributors/zeyi-lin/hivisionidphotos?color=c4f042&labelColor=black&style=flat-square
[github-contributors-link]: https://github.com/zeyi-lin/hivisionidphotos/graphs/contributors

[github-forks-shield]: https://img.shields.io/github/forks/zeyi-lin/hivisionidphotos?color=8ae8ff&labelColor=black&style=flat-square
[github-forks-link]: https://github.com/zeyi-lin/hivisionidphotos/network/members