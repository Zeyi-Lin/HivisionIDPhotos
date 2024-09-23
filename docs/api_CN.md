# API Docs

[English](api_EN.md) / 中文


## 目录

- [开始之前：开启后端服务](#开始之前开启后端服务)
- [接口功能说明](#接口功能说明)
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

### 2.添加背景色

接口名：`add_background`

`添加背景色`接口的逻辑是接收一张 RGBA 图像（透明图），根据`color`添加背景色，合成一张 JPG 图像。

### 3.生成六寸排版照

接口名：`generate_layout_photos`

`生成六寸排版照`接口的逻辑是接收一张 RGB 图像（一般为添加背景色之后的证件照），根据`size`进行照片排布，然后生成一张六寸排版照。

### 4.人像抠图

接口名：`human_matting`

`人像抠图`接口的逻辑是接收一张 RGB 图像，输出一张标准抠图人像照和高清抠图人像照（无任何背景填充）。

### 5.图像加水印

接口名：`watermark`

`图像加水印`接口的功能是接收一个水印文本，然后在原图上添加指定的水印。用户可以指定水印的位置、透明度和大小等属性，以便将水印无缝地融合到原图中。


### 6.设置图像KB大小

接口名：`set_kb`

`设置图像KB大小`接口的功能是接收一张图像和目标文件大小（以KB为单位），如果设置的KB值小于原文件，则调整压缩率；如果设置的KB值大于源文件，则通过给文件头添加信息的方式调大KB值，目标是让图像的最终大小与设置的KB值一致。

### 7.证件照裁切

接口名：`idphoto_crop`

`证件照裁切`接口的功能是接收一张 RBGA 图像（透明图），输出一张标准证件照和一张高清证件照。

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