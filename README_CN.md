<div align="center">
<h1><img src="https://linimages.oss-cn-beijing.aliyuncs.com/hivision_photo_logo.png" width=80>HivisionIDPhoto</h1>

[English](README.md) / 中文

[![GitHub](https://img.shields.io/static/v1?label=GitHub&message=GitHub&color=black)](https://github.com/xiaolin199912/HivisionIDPhotos)
[![SwanHub Demo](https://img.shields.io/static/v1?label=在线体验&message=SwanHub%20Demo&color=blue)](https://swanhub.co/ZeYiLin/HivisionIDPhotos/demo)
[![zhihu](https://img.shields.io/static/v1?label=知乎&message=知乎&color=blue)](https://zhuanlan.zhihu.com/p/638254028)

<img src="sources/demoImage.png" width=900>
</div>


# 🤩项目更新
- 在线体验: [![SwanHub Demo](https://img.shields.io/static/v1?label=Demo&message=SwanHub%20Demo&color=blue)](https://swanhub.co/ZeYiLin/HivisionIDPhotos/demo)
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
<img src="sources/gradio-image.jpeg" width=900>
</div>


---

如果HivisionIDPhoto对你有帮助，请star这个repo或推荐给你的朋友，解决证件照应急制作问题！


# 🔧环境安装与依赖

- Python >= 3.7 (Recommend to use [Anaconda](https://www.anaconda.com/download/#linux) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html))
- onnxruntime
- OpenCV
- Option: Linux, Windows, MacOS

### Installation

1. Clone repo

```bash
git lfs install && git clone https://swanhub.co/ZeYiLin/HivisionIDPhotos.git
cd  HivisionIDPhotos
```

2. Install dependent packages

```
pip install numpy
pip install opencv-python
pip install onnxruntime
pip install gradio
```



# ⚡️快速推理

模型与代码通过git-lfs下载。

```
git lfs install
git clone https://swanhub.co/ZeYiLin/HivisionIDPhotos.git
```

**推理！**

```
python app.py
```

运行程序将生成一个本地Web页面，在页面中可完成证件照的操作与交互。


# 引用项目

1. MTCNN: https://github.com/ipazc/mtcnn
2. ModNet: https://github.com/ZHKKKe/MODNet

# 📧联系我们

如果您有任何问题，请发邮件至 zeyi.lin@swanhub.co