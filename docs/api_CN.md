# API Docs

## 开始之前：开启后端服务

在请求 API 之前，请先运行后端服务

```bash
python delopy_api.py
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

`添加背景色`接口的逻辑是发送一张 RGBA 图像，根据`color`添加背景色，合成一张 JPG 图像。

### 3.生成六寸排版照

接口名：`generate_layout_photos`

`生成六寸排版照`接口的逻辑是发送一张 RGB 图像（一般为添加背景色之后的证件照），根据`size`进行照片排布，然后生成一张六寸排版照。

<br>

## 1️⃣ Python Requests 请求方法

### 1.生成证件照(底透明)

```python
import requests

url = "http://127.0.0.1:8080/idphoto"
input_image_path = "images/test.jpg"

files = {"input_image": open(input_image_path, "rb")}
data = {"height": 413, "width": 295}

response = requests.post(url, files=files, data=data).json()

# response为一个json格式字典，包含status、image_base64_standard和image_base64_hd三项
print(response)

```

### 2.添加背景色

```python
import requests

url = "http://127.0.0.1:8080/add_background"
input_image_path = "test.png"

files = {"input_image": open(input_image_path, "rb")}
data = {"color": '638cce', 'kb': None}

response = requests.post(url, files=files, data=data).json()

# response为一个json格式字典，包含status和image_base64
print(response)
```

### 3.生成六寸排版照

```python
import requests

url = "http://127.0.0.1:8080/generate_layout_photos"
input_image_path = "test.jpg"

files = {"input_image": open(input_image_path, "rb")}
data = {"height": 413, "width": 295, "kb": 200}

response = requests.post(url, files=files, data=data).json()

# response为一个json格式字典，包含status和image_base64
print(response)
```

<br>

## 2️⃣ Python 脚本请求方法

```bash
python requests_api.py -u <URL> -t <TYPE> -i <INPUT_IMAGE_DIR> -o <OUTPUT_IMAGE_DIR> [--height <HEIGHT>] [--width <WIDTH>] [-c <COLOR>] [-k <KB>]
```

### 参数说明

#### 基本参数

- `-u`, `--url`

  - **描述**: API 服务的 URL。
  - **默认值**: `http://127.0.0.1:8080`

- `-t`, `--type`

  - **描述**: 请求 API 的种类，可选值有 `idphoto`、`add_background` 和 `generate_layout_photos`。分别代表证件照制作、透明图加背景和排版照生成。
  - **默认值**: `idphoto`

- `-i`, `--input_image_dir`

  - **描述**: 输入图像路径。
  - **必需**: 是
  - **示例**: `./input_images/photo.jpg`

- `-o`, `--output_image_dir`
  - **描述**: 保存图像路径。
  - **必需**: 是
  - **示例**: `./output_images/processed_photo.jpg`

#### 可选参数

- `--height`,

  - **描述**: 标准证件照的输出尺寸的高度。
  - **默认值**: 413

- `--width`,

  - **描述**: 标准证件照的输出尺寸的宽度。
  - **默认值**: 295

- `-c`, `--color`

  - **描述**: 给透明图增加背景色，格式为 Hex（如#638cce），仅在 type 为`add_background`时生效
  - **默认值**: `638cce`

- `-k`, `--kb`
  - **描述**: 输出照片的 KB 值，仅在 type 为`add_background`和`generate_layout_photos`时生效，值为 None 时不做设置。
  - **默认值**: `None`
  - **示例**: `50`

### 1.生成证件照(底透明)

```bash
python requests_api.py  \
    -u http://127.0.0.1:8080 \
    -t idphoto \
    -i ./photo.jpg \
    -o ./idphoto.png \
    --height 413 \
    --width 295
```

### 2.添加背景色

```bash
python requests_api.py  \
    -u http://127.0.0.1:8080  \
    -t add_background  \
    -i ./idphoto.png  \
    -o ./idphoto_with_background.jpg  \
    -c 638cce  \
    -k 50
```

### 3.生成六寸排版照

```bash
python requests_api.py  \
    -u http://127.0.0.1:8080  \
    -t generate_layout_photos  \
    -i ./idphoto_with_background.jpg  \
    -o ./layout_photo.jpg  \
    --height 413  \
    --width 295 \
    -k 200
```

### 请求失败的情况

- 照片中检测到的人脸大于 1，则失败
