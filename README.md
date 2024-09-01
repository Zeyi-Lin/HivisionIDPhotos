<div align="center">
<h1>HivisionIDPhoto</h1>

[English](README_EN.md) / 中文 / [日本語](README_JP.md)

[![GitHub](https://img.shields.io/static/v1?label=GitHub&message=GitHub&color=black)](https://github.com/xiaolin199912/HivisionIDPhotos)
[![SwanHub Demo](https://swanhub.co/git/repo/SwanHub%2FAuto-README/file/preview?ref=main&path=swanhub.svg)](https://swanhub.co/ZeYiLin/HivisionIDPhotos/demo)
[![zhihu](https://img.shields.io/static/v1?label=知乎&message=知乎&color=blue)](https://zhuanlan.zhihu.com/p/638254028)
[![Spaces](https://img.shields.io/badge/🤗-Open%20in%20Spaces-blue)](https://huggingface.co/spaces/TheEeeeLin/HivisionIDPhotos)


<img src="assets/demoImage.png" width=900>
</div>

<br>

> **相关项目**：  
> - [SwanLab](https://github.com/SwanHubX/SwanLab)：训练人像抠图模型全程用它来分析和监控，以及和实验室同学协作交流，大幅提升了训练效率。

<br>

# 🤩项目更新
- 在线体验: [![SwanHub Demo](https://img.shields.io/static/v1?label=Demo&message=SwanHub%20Demo&color=blue)](https://swanhub.co/ZeYiLin/HivisionIDPhotos/demo)
- 2023.12.1: 更新**API部署（基于fastapi）**
- 2023.6.20: 更新**预设尺寸菜单**
- 2023.6.19: 更新**排版照**
- 2023.6.13: 更新**中心渐变色**
- 2023.6.11: 更新**上下渐变色**
- 2023.6.8: 更新**自定义尺寸**
- 2023.6.4: 更新**自定义底色、人脸检测Bug通知**
- 2023.5.10: 更新**不改尺寸只换底**

# Overview

> 🚀谢谢你对我们的工作感兴趣。您可能还想查看我们在图像领域的其他成果，欢迎来信:zeyi.lin@swanhub.co.

HivisionIDPhoto旨在开发一种实用的证件照智能制作算法。

它利用一套完善的模型工作流程，实现对多种用户拍照场景的识别、抠图与证件照生成。


**HivisionIDPhoto可以做到:**

1. 轻量级抠图
2. 根据不同尺寸规格生成不同的标准证件照、六寸排版照
3. 美颜（waiting）
4. 智能换正装（waiting）

<div align="center">
<img src="assets/gradio-image.jpeg" width=900>
</div>


---

如果HivisionIDPhoto对你有帮助，请star这个repo或推荐给你的朋友，解决证件照应急制作问题！

<br>

# 🔧环境安装与依赖

- Python >= 3.7（项目主要测试在python 3.10）
- onnxruntime
- OpenCV
- Option: Linux, Windows, MacOS

**1. 克隆项目**

```bash
git clone https://github.com/Zeyi-Lin/HivisionIDPhotos.git
cd  HivisionIDPhotos
```

**2. 安装依赖环境**

```bash
pip install -r requirements.txt
```

**3. 下载权重文件**

在我们的[Release](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/tag/pretrained-model)下载权重文件`hivision_modnet.onnx`，存到根目录下。

<br>

# 运行Gradio Demo

```bash
python app.py
```

运行程序将生成一个本地Web页面，在页面中可完成证件照的操作与交互。

<br>

# 部署API服务

```
python deploy_api.py
```


**请求API服务（Python）**

用Python给服务发送请求：

证件照制作（输入1张照片，获得1张标准证件照和1张高清证件照的4通道透明png）：

```bash
python requests_api.py -u http://127.0.0.1:8080 -i test.jpg -o ./idphoto.png -s '(413,295)'
```

增加底色（输入1张4通道透明png，获得1张增加了底色的图像）：

```bash
python requests_api.py -u http://127.0.0.1:8080 -t add_background -i ./idphoto.png -o ./idhoto_ab.jpg  -c '(0,0,0)'
```

得到六寸排版照（输入1张3通道照片，获得1张六寸排版照）：

```bash
python requests_api.py -u http://127.0.0.1:8080 -t generate_layout_photos -i ./idhoto_ab.jpg -o ./idhoto_layout.jpg  -s '(413,295)'
```

<br>

# 🐳Docker部署

在确保将模型权重文件[hivision_modnet.onnx](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/tag/pretrained-model)放到根目录下后，在根目录执行：

```bash
docker build -t hivision_idphotos .
```

等待镜像封装完毕后，运行以下指令，即可开启API服务：

```bash
docker run -p 8080:8080 hivision_idphotos
```

<br>


# 引用项目

1. MTCNN: https://github.com/ipazc/mtcnn
2. ModNet: https://github.com/ZHKKKe/MODNet

<br>


# 📧联系我们

如果您有任何问题，请发邮件至 zeyi.lin@swanhub.co
