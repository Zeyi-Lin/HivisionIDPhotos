<div align="center">
<h1>HivisionIDPhoto</h1>


English / [中文](README.md) / [日本語](README_JP.md)

[![GitHub](https://img.shields.io/static/v1?label=Github&message=GitHub&color=black)](https://github.com/xiaolin199912/HivisionIDPhotos)
[![SwanHub Demo](https://swanhub.co/git/repo/SwanHub%2FAuto-README/file/preview?ref=main&path=swanhub.svg)](https://swanhub.co/ZeYiLin/HivisionIDPhotos/demo)
[![zhihu](https://img.shields.io/static/v1?label=知乎&message=zhihu&color=blue)](https://zhuanlan.zhihu.com/p/638254028)
[![Spaces](https://img.shields.io/badge/🤗-Open%20in%20Spaces-blue)](https://huggingface.co/spaces/TheEeeeLin/HivisionIDPhotos)


<img src="assets/demoImage.png" width=900>
</div>

</div>


# 🤩Project Update

- Online Demo: [![SwanHub Demo](https://swanhub.co/git/repo/SwanHub%2FAuto-README/file/preview?ref=main&path=swanhub.svg)](https://swanhub.co/ZeYiLin/HivisionIDPhotos/demo)
- 2023.12.1: Update **API deployment (based on fastapi)**
- 2023.6.20: Update **Preset size menu**
- 2023.6.19: Update **Layout photos**
- 2023.6.13: Update **Center gradient color**
- 2023.6.11: Update **Top and bottom gradient color**
- 2023.6.8: Update **Custom size**
- 2023.6.4: Update **Custom background color, face detection bug notification**
- 2023.5.10: Update **Change the background without changing the size**


<br>

# Overview

> 🚀Thank you for your interest in our work. You may also want to check out our other achievements in the field of image processing. Please feel free to contact us at zeyi.lin@swanhub.co.

HivisionIDPhoto aims to develop a practical intelligent algorithm for producing ID photos. It uses a complete set of model workflows to recognize various user photo scenarios, perform image segmentation, and generate ID photos. 

**HivisionIDPhoto can:**

1. Perform lightweight image segmentation
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

- Python >= 3.7（The main test of the project is in Python 3.10.）
- onnxruntime
- OpenCV
- Option: Linux, Windows, MacOS

### Installation

1. Clone repo

```bash
git clone https://github.com/Zeyi-Lin/HivisionIDPhotos.git
cd  HivisionIDPhotos
```

2. Install dependent packages

```
pip install -r requirements.txt
```

**3. Download Pretrain file**

Download the weight file `hivision_modnet.onnx` from our [Release](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/tag/pretrained-model) and save it to the root directory.

<br>

# Gradio Demo

```bash
python app.py
```

Running the program will generate a local web page, where operations and interactions with ID photos can be completed.

<br>

# Deploy API service

```
python deploy_api.py
```

**Request API service (Python)**

Use Python to send a request to the service:

ID photo production (input 1 photo, get 1 standard ID photo and 1 high-definition ID photo 4-channel transparent png):

```bash
python requests_api.py -u http://127.0.0.1:8080 -i test.jpg -o ./idphoto.png -s '(413,295)'
```

Add background color (input 1 4-channel transparent png, get 1 image with added background color):

```bash
python requests_api.py -u http://127.0.0.1:8080 -t add_background -i ./idphoto.png -o ./idhoto_ab.jpg -c '(0,0,0)'
```

Get a six-inch layout photo (input a 3-channel photo, get a six-inch layout photo):

```bash
python requests_api.py -u http://127.0.0.1:8080 -t generate_layout_photos -i ./idhoto_ab.jpg -o ./idhoto_layout.jpg -s '(413,295)'
```

<br>

# 🐳Docker deployment

After ensuring that the model weight file [hivision_modnet.onnx](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/tag/pretrained-model) is placed in the root directory, execute in the root directory:

```bash
docker build -t hivision_idphotos .
```

After the image is packaged, run the following command to start the API service:

```bash
docker run -p 8080:8080 hivision_idphotos
```

<br>

# Reference Projects

1. MTCNN: https://github.com/ipazc/mtcnn
2. ModNet: https://github.com/ZHKKKe/MODNet


<br>

# 📧Contact 

If you have any questions, please email Zeyi.lin@swanhub.co


Copyright © 2023, ZeYiLin. All Rights Reserved.

