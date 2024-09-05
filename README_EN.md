<div align="center">
<h1>HivisionIDPhoto</h1>

English / [中文](README.md) / [日本語](README_JP.md) / [한국어](README_KO.md)

[![GitHub](https://img.shields.io/static/v1?label=Github&message=GitHub&color=black)](https://github.com/xiaolin199912/HivisionIDPhotos)
[![SwanHub Demo](https://swanhub.co/git/repo/SwanHub%2FAuto-README/file/preview?ref=main&path=swanhub.svg)](https://swanhub.co/ZeYiLin/HivisionIDPhotos/demo)
[![zhihu](https://img.shields.io/static/v1?label=知乎&message=zhihu&color=blue)](https://zhuanlan.zhihu.com/p/638254028)
[![Spaces](https://img.shields.io/badge/🤗-Open%20in%20Spaces-blue)](https://huggingface.co/spaces/TheEeeeLin/HivisionIDPhotos)

<a href="https://trendshift.io/repositories/11622" target="_blank"><img src="https://trendshift.io/api/badge/repositories/11622" alt="Zeyi-Lin%2FHivisionIDPhotos | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

<img src="assets/demoImage.png" width=900>
</div>

</div>

# 🤩Project Update

- Online Demo: [![SwanHub Demo](https://img.shields.io/static/v1?label=Demo&message=SwanHub%20Demo&color=blue)](https://swanhub.co/ZeYiLin/HivisionIDPhotos/demo)、[![Spaces](https://img.shields.io/badge/🤗-Open%20in%20Spaces-blue)](https://huggingface.co/spaces/TheEeeeLin/HivisionIDPhotos)

- 2024.9.2: Update **Adjusted photo KB size**，[DockerHub](https://hub.docker.com/r/linzeyi/hivision_idphotos/tags)
- 2023.12.1: Update **API deployment (based on fastapi)**
- 2023.6.20: Update **Preset size menu**
- 2023.6.19: Update **Layout photos**

<br>

# Overview

> 🚀Thank you for your interest in our work. You may also want to check out our other achievements in the field of image processing. Please feel free to contact us at zeyi.lin@swanhub.co.

HivisionIDPhoto aims to develop a practical intelligent algorithm for producing ID photos. It uses a complete set of model workflows to recognize various user photo scenarios, perform image segmentation, and generate ID photos.

**HivisionIDPhoto can:**

1. Perform lightweight image segmentation (Only CPU is needed for fast inference.)
2. Generate standard ID photos and six-inch layout photos according to different size specifications
3. Provide beauty features (waiting)
4. Provide intelligent formal wear replacement (waiting)

<div align="center">
<img src="assets/gradio-image.jpeg" width=900>
</div>

---

If HivisionIDPhoto is helpful to you, please star this repo or recommend it to your friends to solve the problem of emergency ID photo production!

<br>

# 🔧Environment Dependencies and Installation

- Python >= 3.7 (The main test of the project is in Python 3.10.)
- onnxruntime
- OpenCV
- Option: Linux, Windows, MacOS

### Installation

1. Clone repo

```bash
git clone https://github.com/Zeyi-Lin/HivisionIDPhotos.git
cd  HivisionIDPhotos
```

2. (Important) Install dependent packages

> It is recommended to create a Python 3.10 virtual environment with conda and then execute the following command.

```bash
pip install -r requirements.txt
pip install -r requirements-app.txt
```

**3. Download Pretrain file**

Download the weight file `hivision_modnet.onnx` from our [Release](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/tag/pretrained-model) and save it to the  `hivision/creator/weights` directory.

<br>

# 🚀 Gradio Demo

```bash
python app.py
```

Running the program will generate a local web page, where operations and interactions with ID photos can be completed.

<br>

# 🚀 Python Inference

## 1. ID Photo Production

Input 1 photo, get 1 standard ID photo and 1 HD ID photo in a transparent PNG with 4 channels.

```python
python inference.py -i demo/images/test.jpg -o ./idphoto.png --height 413 --width 295
```

## 2. Add Background Color

Input 1 transparent PNG with 4 channels, get an image with added background color.

```python

python inference.py -t add_background -i ./idphoto.png -o ./idhoto_ab.jpg  -c 000000 -k 30

```

## 3. Obtain Six-Inch Layout Photo

Input 1 photo with 3 channels, obtain one six-inch layout photo.

```python

python inference.py -t generate_layout_photos -i ./idhoto_ab.jpg -o ./idhoto_layout.jpg  --height 413 --width 295 -k 200

```

<br>

# ⚡️ Deploy API service

## Start backend

```
python deploy_api.py
```

## Request API Service - Python Request

### 1. ID Photo Creation

Input 1 photo, receive 1 standard ID photo and 1 high-definition ID photo in 4-channel transparent PNG format.

```bash
import requests

url = "http://127.0.0.1:8080/idphoto"
input_image_path = "images/test.jpg"

files = {"input_image": open(input_image_path, "rb")}
data = {"height": 413, "width": 295}

response = requests.post(url, files=files, data=data).json()

# response is a JSON dictionary containing status, image_base64_standard, and image_base64_hd
print(response)

```

### 2. Add Background Color

Input 1 4-channel transparent PNG, receive 1 image with added background color.

```bash
import requests

url = "http://127.0.0.1:8080/add_background"
input_image_path = "test.png"

files = {"input_image": open(input_image_path, "rb")}
data = {"color": '638cce', 'kb': None}

response = requests.post(url, files=files, data=data).json()

# response is a JSON dictionary containing status and image_base64
print(response)
```

### 3. Get 6-inch Layout Photo

Input 1 3-channel photo, receive 1 6-inch layout photo.

```bash
import requests

url = "http://127.0.0.1:8080/generate_layout_photos"
input_image_path = "test.jpg"

files = {"input_image": open(input_image_path, "rb")}
data = {"height": 413, "width": 295, "kb": 200}

response = requests.post(url, files=files, data=data).json()

# response is a JSON dictionary containing status and image_base64
print(response)
```

For more request methods, please refer to the [API documentation](docs/api_EN.md), including Python script requests, Python Request requests, and Java requests.

<br>

# 🐳 Docker deployment

## 1. Pull or Build Image

> Choose one of the following three methods

**Method 1 - Pull Image from DockerHub:**

```bash
docker pull linzeyi/hivision_idphotos:v1
docker tag linzeyi/hivision_idphotos:v1 hivision_idphotos
```

**Method 2 - Build Image:**

After ensuring that the model weight file [hivision_modnet.onnx](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/tag/pretrained-model) is placed in the `hivision/creator/weights` directory, execute in the root directory:

```bash
docker build -t hivision_idphotos .
```

**Method 3 - Docker Compose:**

After ensuring that the model weight file [hivision_modnet.onnx](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/tag/pretrained-model) is placed in the `hivision/creator/weights` directory, execute in the root directory:

```bash
docker compose build
```

After the image is packaged, run the following command to start the Gradio service:

```bash
docker compose up -d
```

## 2. Run the Gradio Demo

After the image packaging is completed, run the following command to start the Gradio Demo service:

```bash
docker run -p 7860:7860 hivision_idphotos
```

You can access it locally at [http://127.0.0.1:7860](http://127.0.0.1:7860/).

## 3. Run API backend service

```bash
docker run -p 8080:8080 hivision_idphotos python3 deploy_api.py
```

<br>

# 🌲 Friendship link

- [HivisionIDPhotos-windows-GUI](https://github.com/zhaoyun0071/HivisionIDPhotos-windows-GUI)

<br>

# 📖 Reference Projects

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

**1. How to modify the preset size?**

After modifying [demo/size_list_CN.csv](size_list_CN.csv), run app.py again, where the first column is the size name, the second column is height, and the third column is width.

<br>

# 📧 Contact

If you have any questions, please email Zeyi.lin@swanhub.co

Copyright © 2023, ZeYiLin. All Rights Reserved.

<br>

# Contributor

<a href="https://github.com/Zeyi-Lin/HivisionIDPhotos/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Zeyi-Lin/HivisionIDPhotos" />
</a>

[Zeyi-Lin](https://github.com/Zeyi-Lin)、[SAKURA-CAT](https://github.com/SAKURA-CAT)、[Feudalman](https://github.com/Feudalman)、[swpfY](https://github.com/swpfY)、[Kaikaikaifang](https://github.com/Kaikaikaifang)、[ShaohonChen](https://github.com/ShaohonChen)、[KashiwaByte](https://github.com/KashiwaByte)

<br>

# StarHistory

[![Star History Chart](https://api.star-history.com/svg?repos=Zeyi-Lin/HivisionIDPhotos&type=Date)](https://star-history.com/#Zeyi-Lin/HivisionIDPhotos&Date)