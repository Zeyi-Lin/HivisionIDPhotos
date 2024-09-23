# API Docs

[English](api_EN.md) / 中文


## 目录

- [开始之前：开启后端服务](#开始之前开启后端服务)
- [接口功能说明](#接口功能说明)
  - [1.生成证件照(底透明)](#1生成证件照底透明)
  - [2.添加背景色](#2添加背景色)
  - [3.生成六寸排版照](#3生成六寸排版照)
  - [4.人像抠图](#4人像抠图)
  - [5.图像加水印](#5图像加水印)
  - [6.设置图像KB大小](#6设置图像KB大小)
  - [7.证件照裁切](#7证件照裁切)
- [cURL 请求示例](#curl-请求示例)
- [Python 请求示例](#python-请求示例)

## 开始之前：开启后端服务

在请求 API 之前，请先运行后端服务

```bash
python deploy_api.py
```

<br>

## 接口功能说明

### 1.生成证件照(底透明)

接口名：`idphoto`

`生成证件照`接口的逻辑是发送一张 RGB 图像，输出一张标准证件照和一张高清证件照：

- **高清证件照**：根据`size`的宽高比例制作的证件照，文件名为`output_image_dir`增加`_hd`后缀
- **标准证件照**：尺寸等于`size`，由高清证件照缩放而来，文件名为`output_image_dir`

需要注意的是，生成的两张照片都是透明的（RGBA 四通道图像），要生成完整的证件照，还需要下面的`添加背景色`接口。

> 问：为什么这么设计？  
> 答：因为在实际产品中，经常用户会频繁切换底色预览效果，直接给透明底图像，由前端 js 代码合成颜色是更好体验的做法。

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| input_image | file | 和`input_image_base64`二选一 | 传入的图像文件，图像文件为需为RGB三通道图像。 |
| input_image_base64 | str | 和`input_image`二选一 | 传入的图像文件的base64编码，图像文件为需为RGB三通道图像。 |
| height | int | 否 | 标准证件照高度，默认为`413` |
| width | int | 否 | 标准证件照宽度，默认为`295` |
| human_matting_model | str | 否 | 人像分割模型，默认为`modnet_photographic_portrait_matting`。可选值为`modnet_photographic_portrait_matting`、`hivision_modnet`、`rmbg-1.4`、`birefnet-v1-lite` |
| face_detect_model | str | 否 | 人脸检测模型，默认为`mtcnn`。可选值为`mtcnn`、`face_plusplus`、`retinaface-resnet50` |
| hd | bool | 否 | 是否生成高清证件照，默认为`true` |
| dpi | int | 否 | 图像分辨率，默认为`300` |
| face_alignment | bool | 否 | 是否进行人脸对齐，默认为`true` |
| head_measure_ratio | float | 否 | 面部面积与照片面积的比例，默认为`0.2` |
| head_height_ratio | float | 否 | 面部中心与照片顶部的高度比例，默认为`0.45` |
| top_distance_max | float | 否 | 头部与照片顶部距离的比例最大值，默认为`0.12` |
| top_distance_min | float | 否 | 头部与照片顶部距离的比例最小值，默认为`0.1` |


**返回参数：**

| 参数名 | 类型 | 说明 |
| :--- | :--- | :--- |
| status | int | 状态码，`true`表示成功 |
| image_base64_standard | str | 标准证件照的base64编码 |
| image_base64_hd | str | 高清证件照的base64编码。如`hd`参数为`false`，则不返回该参数 |

<br>

### 2.添加背景色

接口名：`add_background`

`添加背景色`接口的逻辑是接收一张 RGBA 图像（透明图），根据`color`添加背景色，合成一张 JPG 图像。

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| input_image | file | 和`input_image_base64`二选一 | 传入的图像文件，图像文件为需为RGBA四通道图像。 |
| input_image_base64 | str | 和`input_image`二选一 | 传入的图像文件的base64编码，图像文件为需为RGBA四通道图像。 |
| color | str | 否 | 背景色HEX值，默认为`000000` |
| kb | int | 否 | 输出照片的 KB 值，默认为`None`，即不对图像进行KB调整。|
| render | int | 否 | 渲染模式，默认为`0`。可选值为`0`、`1`、`2`，分别对应`纯色`、`上下渐变`、`中心渐变`。 |
| dpi | int | 否 | 图像分辨率，默认为`300` |

**返回参数：**

| 参数名 | 类型 | 说明 |
| :--- | :--- | :--- |
| status | int | 状态码，`true`表示成功 |
| image_base64 | str | 添加背景色之后的图像的base64编码 |

<br>

### 3.生成六寸排版照

接口名：`generate_layout_photos`

`生成六寸排版照`接口的逻辑是接收一张 RGB 图像（一般为添加背景色之后的证件照），根据`size`进行照片排布，然后生成一张六寸排版照。

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| input_image | file | 和`input_image_base64`二选一 | 传入的图像文件，图像文件为需为RGB三通道图像。 |
| input_image_base64 | str | 和`input_image`二选一 | 传入的图像文件的base64编码，图像文件为需为RGB三通道图像。 |
| height | int | 否 | 输入图像的高度，默认为`413` |
| width | int | 否 | 输入图像的宽度，默认为`295` |
| kb | int | 否 | 输出照片的 KB 值，默认为`None`，即不对图像进行KB调整。|
| dpi | int | 否 | 图像分辨率，默认为`300` |

**返回参数：**

| 参数名 | 类型 | 说明 |
| :--- | :--- | :--- |
| status | int | 状态码，`true`表示成功 |
| image_base64 | str | 六寸排版照的base64编码 |

<br>

### 4.人像抠图

接口名：`human_matting`

`人像抠图`接口的逻辑是接收一张 RGB 图像，输出一张标准抠图人像照和高清抠图人像照（无任何背景填充）。

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| input_image | file | 是 | 传入的图像文件，图像文件为需为RGB三通道图像。 |
| human_matting_model | str | 否 | 人像分割模型，默认为`modnet_photographic_portrait_matting`。可选值为`modnet_photographic_portrait_matting`、`hivision_modnet`、`rmbg-1.4`、`birefnet-v1-lite` |
| dpi | int | 否 | 图像分辨率，默认为`300` |

**返回参数：**

| 参数名 | 类型 | 说明 |
| :--- | :--- | :--- |
| status | int | 状态码，`true`表示成功 |
| image_base64 | str | 抠图人像照的base64编码 |

<br>

### 5.图像加水印

接口名：`watermark`

`图像加水印`接口的功能是接收一个水印文本，然后在原图上添加指定的水印。用户可以指定水印的位置、透明度和大小等属性，以便将水印无缝地融合到原图中。

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| input_image | file | 和`input_image_base64`二选一 | 传入的图像文件，图像文件为需为RGB三通道图像。 |
| input_image_base64 | str | 和`input_image`二选一 | 传入的图像文件的base64编码，图像文件为需为RGB三通道图像。 |
| text | str | 否 | 水印文本，默认为`Hello` |
| size | int | 否 | 水印字体大小，默认为`20` |
| opacity | float | 否 | 水印透明度，默认为`0.5` |
| angle | int | 否 | 水印旋转角度，默认为`30` |
| color | str | 否 | 水印颜色，默认为`#000000` |
| space | int | 否 | 水印间距，默认为`25` |
| dpi | int | 否 | 图像分辨率，默认为`300` |

**返回参数：**

| 参数名 | 类型 | 说明 |
| :--- | :--- | :--- |
| status | int | 状态码，`true`表示成功 |
| image_base64 | str | 添加水印之后的图像的base64编码 |

<br>

### 6.设置图像KB大小

接口名：`set_kb`

`设置图像KB大小`接口的功能是接收一张图像和目标文件大小（以KB为单位），如果设置的KB值小于原文件，则调整压缩率；如果设置的KB值大于源文件，则通过给文件头添加信息的方式调大KB值，目标是让图像的最终大小与设置的KB值一致。

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| input_image | file | 和`input_image_base64`二选一 | 传入的图像文件，图像文件为需为RGB三通道图像。 |
| input_image_base64 | str | 和`input_image`二选一 | 传入的图像文件的base64编码，图像文件为需为RGB三通道图像。 |
| kb | int | 否 | 输出照片的 KB 值，默认为`None`，即不对图像进行KB调整。|
| dpi | int | 否 | 图像分辨率，默认为`300` |

**返回参数：**

| 参数名 | 类型 | 说明 |
| :--- | :--- | :--- |
| status | int | 状态码，`true`表示成功 |
| image_base64 | str | 设置KB大小之后的图像的base64编码 |

<br>

### 7.证件照裁切

接口名：`idphoto_crop`

`证件照裁切`接口的功能是接收一张 RBGA 图像（透明图），输出一张标准证件照和一张高清证件照。

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| input_image | file | 和`input_image_base64`二选一 | 传入的图像文件，图像文件为需为RGBA四通道图像。 |
| input_image_base64 | str | 和`input_image`二选一 | 传入的图像文件的base64编码，图像文件为需为RGBA四通道图像。 |
| height | int | 否 | 标准证件照高度，默认为`413` |
| width | int | 否 | 标准证件照宽度，默认为`295` |
| face_detect_model | str | 否 | 人脸检测模型，默认为`mtcnn`。可选值为`mtcnn`、`face_plusplus`、`retinaface-resnet50` |
| hd | bool | 否 | 是否生成高清证件照，默认为`true` |
| dpi | int | 否 | 图像分辨率，默认为`300` |
| head_measure_ratio | float | 否 | 面部面积与照片面积的比例，默认为`0.2` |
| head_height_ratio | float | 否 | 面部中心与照片顶部的高度比例，默认为`0.45` |
| top_distance_max | float | 否 | 头部与照片顶部距离的比例最大值，默认为`0.12` |
| top_distance_min | float | 否 | 头部与照片顶部距离的比例最小值，默认为`0.1` |

**返回参数：**

| 参数名 | 类型 | 说明 |
| :--- | :--- | :--- |
| status | int | 状态码，`true`表示成功 |
| image_base64 | str | 证件照裁切之后的图像的base64编码 |
| image_base64_hd | str | 高清证件照裁切之后的图像的base64编码，如`hd`参数为`false`，则不返回该参数 |

<br>

## cURL 请求示例

cURL 是一个命令行工具，用于使用各种网络协议传输数据。以下是使用 cURL 调用这些 API 的示例。

### 1. 生成证件照(底透明)

```bash
curl -X POST "http://127.0.0.1:8080/idphoto" \
-F "input_image=@demo/images/test0.jpg" \
-F "height=413" \
-F "width=295" \
-F "human_matting_model=modnet_photographic_portrait_matting" \
-F "face_detect_model=mtcnn" \
-F "hd=true" \
-F "dpi=300" \
-F "face_alignment=true"
```

### 2. 添加背景色

```bash
curl -X POST "http://127.0.0.1:8080/add_background" \
-F "input_image=@test.png" \
-F "color=638cce" \
-F "kb=200" \
-F "render=0" \
-F "dpi=300"
```

### 3. 生成六寸排版照

```bash
curl -X POST "http://127.0.0.1:8080/generate_layout_photos" \
-F "input_image=@test.jpg" \
-F "height=413" \
-F "width=295" \
-F "kb=200" \
-F "dpi=300"
```

### 4. 人像抠图

```bash
curl -X POST "http://127.0.0.1:8080/human_matting" \
-F "input_image=@demo/images/test0.jpg" \
-F "human_matting_model=modnet_photographic_portrait_matting" \
-F "dpi=300"
```

### 5. 图片加水印
```bash
curl -X 'POST' \
  'http://127.0.0.1:8080/watermark?size=20&opacity=0.5&angle=30&color=%23000000&space=25' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'input_image=@demo/images/test0.jpg;type=image/jpeg' \
  -F 'text=Hello' \
  -F 'dpi=300'
```

### 6. 设置图像KB大小
```bash
curl -X 'POST' \
  'http://127.0.0.1:8080/set_kb' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'input_image=@demo/images/test0.jpg;type=image/jpeg' \
  -F 'kb=50' \
  -F 'dpi=300'
```

### 7. 证件照裁切
```bash
curl -X 'POST' \
  'http://127.0.0.1:8080/idphoto_crop?head_measure_ratio=0.2&head_height_ratio=0.45&top_distance_max=0.12&top_distance_min=0.1' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'input_image=@idphoto_matting.png;type=image/png' \
  -F 'height=413' \
  -F 'width=295' \
  -F 'face_detect_model=mtcnn' \
  -F 'hd=true' \
  -F 'dpi=300'
```

<br>

## Python 请求示例

#### 1.生成证件照(底透明)
```python
import requests

url = "http://127.0.0.1:8080/idphoto"
input_image_path = "demo/images/test0.jpg"

# 设置请求参数
params = {
    "head_measure_ratio": 0.2,
    "head_height_ratio": 0.45,
    "top_distance_max": 0.12,
    "top_distance_min": 0.1,
}
files = {"input_image": open(input_image_path, "rb")}
data = {
    "height": 413,
    "width": 295,
    "human_matting_model": "modnet_photographic_portrait_matting",
    "face_detect_model": "mtcnn",
    "hd": True,
    "dpi": 300,
    "face_alignment": True,
}

response = requests.post(url, params=params, files=files, data=data).json()

# response为一个json格式字典，包含status、image_base64_standard和image_base64_hd三项
print(response)
```

#### 2.添加背景色

```python
import requests

url = "http://127.0.0.1:8080/add_background"
input_image_path = "test.png"

files = {"input_image": open(input_image_path, "rb")}
data = {
    "color": '638cce',
    "kb": None,
    "render": 0,
    "dpi": 300,
}

response = requests.post(url, files=files, data=data).json()

# response为一个json格式字典，包含status和image_base64
print(response)
```

#### 3.生成六寸排版照

```python
import requests

url = "http://127.0.0.1:8080/generate_layout_photos"
input_image_path = "test.jpg"

files = {"input_image": open(input_image_path, "rb")}
data = {
    "height": 413,
    "width": 295,
    "kb": 200,
    "dpi": 300,
}

response = requests.post(url, files=files, data=data).json()

# response为一个json格式字典，包含status和image_base64
print(response)
```

#### 4.人像抠图

```python
import requests

url = "http://127.0.0.1:8080/human_matting"
input_image_path = "test.jpg"

files = {"input_image": open(input_image_path, "rb")}
data = {
    "human_matting_model": "modnet_photographic_portrait_matting",
    "dpi": 300,
}

response = requests.post(url, files=files, data=data).json()

# response为一个json格式字典，包含status和image_base64
print(response)
```

#### 5.图片加水印

```python
import requests

# 设置请求的 URL 和参数
url = "http://127.0.0.1:8080/watermark"
params = {
    "size": 20,
    "opacity": 0.5,
    "angle": 30,
    "color": "#000000",
    "space": 25,
}

# 设置文件和其他表单数据
input_image_path = "demo/images/test0.jpg"
files = {"input_image": open(input_image_path, "rb")}
data = {"text": "Hello", "dpi": 300}

# 发送 POST 请求
response = requests.post(url, params=params, files=files, data=data)

# 检查响应
if response.ok:
    # 输出响应内容
    print(response.json())
else:
    # 输出错误信息
    print(f"Request failed with status code {response.status_code}: {response.text}")
```

### 6. 设置图像KB大小

```python
import requests

# 设置请求的 URL
url = "http://127.0.0.1:8080/set_kb"

# 设置文件和其他表单数据
input_image_path = "demo/images/test0.jpg"
files = {"input_image": open(input_image_path, "rb")}
data = {"kb": 50, "dpi": 300}

# 发送 POST 请求
response = requests.post(url, files=files, data=data)

# 检查响应
if response.ok:
    # 输出响应内容
    print(response.json())
else:
    # 输出错误信息
    print(f"Request failed with status code {response.status_code}: {response.text}")
```

### 7. 证件照裁切

```python
import requests

# 设置请求的 URL
url = "http://127.0.0.1:8080/idphoto_crop"

# 设置请求参数
params = {
    "head_measure_ratio": 0.2,
    "head_height_ratio": 0.45,
    "top_distance_max": 0.12,
    "top_distance_min": 0.1,
}

# 设置文件和其他表单数据
input_image_path = "idphoto_matting.png"
files = {"input_image": ("idphoto_matting.png", open(input_image_path, "rb"), "image/png")}
data = {
    "height": 413,
    "width": 295,
    "face_detect_model": "mtcnn",
    "hd": "true",
    "dpi": 300,
}

# 发送 POST 请求
response = requests.post(url, params=params, files=files, data=data)

# 检查响应
if response.ok:
    # 输出响应内容
    print(response.json())
else:
    # 输出错误信息
    print(f"Request failed with status code {response.status_code}: {response.text}")
```