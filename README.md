<div align="center">
    <img src="https://linimages.oss-cn-beijing.aliyuncs.com/hivision_photo_logo.png" alt="alt text" width="160" height="160">
</div>


<div align="center"><h2>HivisionIDPhoto：焕影一新小程序官方证件照制作算法</h2></div>

> 🚀谢谢你对我们的工作感兴趣。您可能还想查看我们在图像领域的其他成果，欢迎来信:xiaolin199912@gmail.com

- 在线demo已更新：[![SwanHub Demo](https://img.shields.io/static/v1?label=HivisionIDphoto&message=SwanHub%20Demo&color=blue)](http://blackswanai.cn/ZeYiLin/HivisionIDPhotos/demo)

HivisionIDPhoto旨在开发一种实用的证件照智能制作算法。

它利用一套完善的模型工作流程，实现对多种用户拍照场景的识别、抠图与证件照生成。

**HivisionIDPhoto可以做到：**

1. 轻量级抠图
2. 根据不同尺寸规格生成不同的标准证件照、六寸排版照
3. 美颜（小程序）
4. 智能换正装（小程序）

> 由于商业原因，完整版的HivisionIDPhoto需在微信小程序使用，在微信搜一搜“焕影一新”即可。

---

如果GFPGAN对你的照片/项目有帮助，请收藏这个repo或推荐给你的朋友。谢谢😊其他推荐项目。



## 🔧环境依赖和安装

- Python >= 3.7 (Recommend to use [Anaconda](https://www.anaconda.com/download/#linux) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html))
- onnxruntime
- OpenCV
- Option: Linux, Windows, MacOS

### 安装

1. Clone repo

```bash
git clone http://182.92.206.173/ZeYiLin/HivisionIDPhotos.git
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
git clone http://182.92.206.173/ZeYiLin/HivisionIDPhotos.git
```

**推理！**

```
python app.py
```

运行程序将生成一个本地Web页面，在页面中可完成证件照的操作与交互。



# 🏠关于我们

焕影一新项目由西电极创工作室出品，是西安电子科技大学的本科生双创优秀案例之一。团队已成立西安焕视灵智科技有限公司，聚焦于智能图像处理、AIGC、人工智能基础设施等领域的研究，产品焕影一新小程序已在全国拥有80+万用户，在年轻的学生群体形成了良好口碑与传播效应。





# 📧 联系我们

如果您有任何问题，请发邮件至xiaolin199912@gmail.com



