<div align="center">

<img alt="hivision_logo" src="assets/hivision_logo.png" width=120 height=120>
<h1>HivisionIDPhoto</h1>

[English](README_EN.md) / 中文 / [日本語](README_JP.md) / [한국어](README_KO.md)

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
[![][hellogithub-shield]][hellogithub-link]

<img src="assets/demoImage.png" width=900>

</div>

<br>

> **相关项目**：
>
> - [SwanLab](https://github.com/SwanHubX/SwanLab)：训练人像抠图模型全程用它来分析和监控，以及和实验室同学协作交流，大幅提升了训练效率。

<br>

# 目录

- [项目更新](#-项目更新)
- [Overview](#overview)
- [准备工作](#-准备工作)
- [Demo启动](#-运行-gradio-demo)
- [Python推理](#-python-推理)
- [API服务部署](#️-部署-api-服务)
- [Docker部署](#-docker-部署)
- [友情链接](#-友情链接)
- [联系我们](#-联系我们)
- [贡献者](#贡献者)

<br>

# 🤩 项目更新

- 在线体验： [![SwanHub Demo](https://img.shields.io/static/v1?label=Demo&message=SwanHub%20Demo&color=blue)](https://swanhub.co/ZeYiLin/HivisionIDPhotos/demo)、[![Spaces](https://img.shields.io/badge/🤗-Open%20in%20Spaces-blue)](https://huggingface.co/spaces/TheEeeeLin/HivisionIDPhotos)

- 2024.09.08: 增加新的抠图模型 [RMBG-1.4](https://huggingface.co/briaai/RMBG-1.4)
- 2024.09.07: 增加**人脸检测API选项** [Face++](docs/face++_CN.md)，实现更高精度的人脸检测
- 2024.09.06: 增加新的抠图模型 [modnet_photographic_portrait_matting.onnx](https://github.com/ZHKKKe/MODNet)
- 2024.09.05: 更新 [Restful API 文档](docs/api_CN.md)
- 2024.09.02: 更新**调整照片 KB 大小**，[DockerHub](https://hub.docker.com/r/linzeyi/hivision_idphotos/tags)
- 2023.12.01: 更新**API 部署（基于 fastapi）**
- 2023.06.20: 更新**预设尺寸菜单**

# Overview

> 🚀 谢谢你对我们的工作感兴趣。您可能还想查看我们在图像领域的其他成果，欢迎来信:zeyi.lin@swanhub.co.

HivisionIDPhoto 旨在开发一种实用、系统性的证件照智能制作算法。

它利用一套完善的AI模型工作流程，实现对多种用户拍照场景的识别、抠图与证件照生成。

**HivisionIDPhoto 可以做到：**

1. 轻量级抠图（纯离线，仅需 **CPU** 即可快速推理）
2. 根据不同尺寸规格生成不同的标准证件照、六寸排版照
3. 支持 纯离线 或 端云 推理
4. 美颜（waiting）
5. 智能换正装（waiting）

<div align="center">
<img src="assets/harry.png" width=900>
</div>

<!-- <div align="center">
<img src="assets/gradio-image.jpeg" width=900>
</div> -->

---

如果 HivisionIDPhoto 对你有帮助，请 star 这个 repo 或推荐给你的朋友，解决证件照应急制作问题！

<br>

# 🔧 准备工作

环境安装与依赖：
- Python >= 3.7（项目主要测试在 python 3.10）
- OS: Linux, Windows, MacOS

## 1. 克隆项目

```bash
git clone https://github.com/Zeyi-Lin/HivisionIDPhotos.git
cd  HivisionIDPhotos
```

## 2. 安装依赖环境

> 建议 conda 创建一个 python3.10 虚拟环境后，执行以下命令

```bash
pip install -r requirements.txt
pip install -r requirements-app.txt
```

## 3. 下载权重文件

**方式一：脚本下载**

```bash
python scripts/download_model.py
```

**方式二：直接下载**

存到项目的`hivision/creator/weights`目录下：
- `modnet_photographic_portrait_matting.onnx` (24.7MB): [MODNet](https://github.com/ZHKKKe/MODNet)官方权重，[下载](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/download/pretrained-model/modnet_photographic_portrait_matting.onnx)
- `hivision_modnet.onnx` (24.7MB): 对纯色换底适配性更好的抠图模型，[下载](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/download/pretrained-model/hivision_modnet.onnx)
- `mnn_hivision_modnet.mnn` (24.7MB): mnn转换后的抠图模型 by [zjkhahah](https://github.com/zjkhahah)，[下载](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/download/pretrained-model/mnn_hivision_modnet.mnn)
- `rmbg-1.4.onnx` (176.2MB): [BRIA AI](https://huggingface.co/briaai/RMBG-1.4) 开源的抠图模型，[下载](https://huggingface.co/briaai/RMBG-1.4/resolve/main/model.pth?download=true)后重命名为`rmbg-1.4.onnx`


## 4. 人脸检测模型配置

> 这是一个可选项

| 拓展人脸检测模型 | 介绍 | 使用文档 |
| -- | -- | -- |
| MTCNN | **离线**人脸检测模型，高性能CPU推理，为默认模型，检测精度较低 | Clone此项目后直接使用 |
| Face++ | 旷视推出的在线人脸检测API，检测精度较高，[官方文档](https://console.faceplusplus.com.cn/documents/4888373) | [使用文档](docs/face++_CN.md)|

<br>

# 🚀 运行 Gradio Demo

```bash
python app.py
```

运行程序将生成一个本地 Web 页面，在页面中可完成证件照的操作与交互。

<br>

# 🚀 Python 推理

核心参数：

- `-i`: 输入图像路径
- `-o`: 保存图像路径
- `-t`: 推理类型，有idphoto、human_matting、add_background、generate_layout_photos可选
- `--matting_model`: 人像抠图模型权重选择，可选`hivision_modnet`、`modnet_photographic_portrait_matting`
- `--face_detect_model`: 人脸检测模型选择，可选`mtcnn`、`face_plusplus`

更多参数可通过`python inference.py --help`查看

## 1. 证件照制作

输入 1 张照片，获得 1 张标准证件照和 1 张高清证件照的 4 通道透明 png

```python
python inference.py -i demo/images/test.jpg -o ./idphoto.png --height 413 --width 295
```

## 2. 人像抠图

```python
python inference.py -t human_matting -i demo/images/test.jpg -o ./idphoto_matting.png --matting_model hivision_modnet
```

## 3. 透明图增加底色

输入 1 张 4 通道透明 png，获得 1 张增加了底色的图像）

```python
python inference.py -t add_background -i ./idphoto.png -o ./idphoto_ab.jpg  -c 4f83ce -k 30 -r 1
```

## 4. 得到六寸排版照

输入 1 张 3 通道照片，获得 1 张六寸排版照

```python
python inference.py -t generate_layout_photos -i ./idphoto_ab.jpg -o ./idphoto_layout.jpg  --height 413 --width 295 -k 200
```

<br>

# ⚡️ 部署 API 服务

## 启动后端

```
python deploy_api.py
```

## 请求 API 服务

详细请求方式请参考 [API 文档](docs/api_CN.md)，包含以下请求示例：
- [cURL](docs/api_CN.md#curl-请求示例)
- [Python](docs/api_CN.md#python-请求示例)
- [Java](docs/api_CN.md#java-请求示例)
- [Javascript](docs/api_CN.md#javascript-请求示例)

<br>

# 🐳 Docker 部署

## 1. 拉取或构建镜像

> 以下方式三选一

**方式一：拉取最新镜像：**

```bash
docker pull linzeyi/hivision_idphotos
```

**方式二：Dockrfile 直接构建镜像：**

在确保将模型权重文件[hivision_modnet.onnx](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/tag/pretrained-model)放到`hivision/creator/weights`下后，在项目根目录执行：

```bash
docker build -t linzeyi/hivision_idphotos .
```

**方式三：Docker compose 构建：**

确保将模型权重文件 [hivision_modnet.onnx](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/tag/pretrained-model) 放在`hivision/creator/weights`下后，在项目根目录下执行：

```bash
docker compose build
```

## 2. 运行服务

**启动 Gradio Demo 服务**

运行下面的命令，在你的本地访问 [http://127.0.0.1:7860](http://127.0.0.1:7860/) 即可使用。

```bash
docker run -d -p 7860:7860 linzeyi/hivision_idphotos
```

**启动 API 后端服务**

```bash
docker run -d -p 8080:8080 linzeyi/hivision_idphotos python3 deploy_api.py
```

**两个服务同时启动**

```bash
docker compose up -d
```

## 环境变量

本项目提供了一些额外的配置项，使用环境变量进行设置：

| 环境变量 | 类型	| 描述 | 示例 |
|--|--|--|--|
| FACE_PLUS_API_KEY	 | 可选	| 这是你在 Face++ 控制台申请的 API 密钥	 | `7-fZStDJ····` |
| FACE_PLUS_API_SECRET	 | 可选	| Face++ API密钥对应的Secret | `VTee824E····` |

docker使用环境变量示例：
```bash
docker run  -d -p 7860:7860 \
    -e FACE_PLUS_API_KEY=7-fZStDJ···· \
    -e FACE_PLUS_API_SECRET=VTee824E···· \
    linzeyi/hivision_idphotos 
```

<br>

# 🌲 友情链接

- [HivisionIDPhotos-windows-GUI](https://github.com/zhaoyun0071/HivisionIDPhotos-windows-GUI)

<br>

# 📖 引用项目

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

# 💻 开发小贴士

**1. 如何修改预设尺寸？**

修改[size_list_CN.csv](demo/size_list_CN.csv)后再次运行 `app.py` 即可，其中第一列为尺寸名，第二列为高度，第三列为宽度。

<br>

# 📧 联系我们

如果您有任何问题，请发邮件至 zeyi.lin@swanhub.co

<br>

# 贡献者

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

<!-- 微信群链接 -->
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