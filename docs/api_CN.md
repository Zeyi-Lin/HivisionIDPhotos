# API Docs

中文 | [English](api_EN.md)

## 目录

- [开始之前：开启后端服务](#开始之前开启后端服务)
- [接口功能说明](#接口功能说明)
- [cURL 请求示例](#curl-请求示例)
- [Python 请求示例](#python-请求示例)
  - [Python Requests 请求方法](#1️⃣-python-requests-请求方法)
  - [Python 脚本请求方法](#2️⃣-python-脚本请求方法)
- [Java 请求示例](#java-请求示例)
- [Javascript 请求示例](#javascript-请求示例)

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

### 4.人像抠图

接口名：`human_matting`

`人像抠图`接口的逻辑是发送一张 RGB 图像，输出一张标准抠图人像照和高清抠图人像照（无任何背景填充）。

<br>

## cURL 请求示例

cURL 是一个命令行工具，用于使用各种网络协议传输数据。以下是使用 cURL 调用这些 API 的示例。

### 1. 生成证件照(底透明)

```bash
curl -X POST "http://127.0.0.1:8080/idphoto" \
-F "input_image=@demo/images/test.jpg" \
-F "height=413" \
-F "width=295" \
-F "human_matting_model=hivision_modnet" \
-F "face_detect_model=mtcnn"
```

### 2. 添加背景色

```bash
curl -X POST "http://127.0.0.1:8080/add_background" \
-F "input_image=@test.png" \
-F "color=638cce" \
-F "kb=200" \
-F "render=0"
```

### 3. 生成六寸排版照

```bash
curl -X POST "http://127.0.0.1:8080/generate_layout_photos" \
-F "input_image=@test.jpg" \
-F "height=413" \
-F "width=295" \
-F "kb=200"
```

### 4. 人像抠图

```bash
curl -X POST "http://127.0.0.1:8080/human_matting" \
-F "input_image=@demo/images/test.jpg" \
-F "human_matting_model=hivision_modnet"
```

<br>

## Python 请求示例

### 1️⃣ Python Requests 请求方法

#### 1.生成证件照(底透明)

```python
import requests

url = "http://127.0.0.1:8080/idphoto"
input_image_path = "images/test.jpg"

files = {"input_image": open(input_image_path, "rb")}
data = {"height": 413, "width": 295, "human_matting_model": "hivision_modnet", "face_detect_model": "mtcnn"}

response = requests.post(url, files=files, data=data).json()

# response为一个json格式字典，包含status、image_base64_standard和image_base64_hd三项
print(response)

```

#### 2.添加背景色

```python
import requests

url = "http://127.0.0.1:8080/add_background"
input_image_path = "test.png"

files = {"input_image": open(input_image_path, "rb")}
data = {"color": '638cce', "kb": None, "render": 0}

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
data = {"height": 413, "width": 295, "kb": 200}

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
data = {"human_matting_model": "hivision_modnet"}

response = requests.post(url, files=files, data=data).json()

# response为一个json格式字典，包含status和image_base64
print(response)
```

### 2️⃣ Python 脚本请求方法

```bash
python requests_api.py -u <URL> -t <TYPE> -i <INPUT_IMAGE_DIR> -o <OUTPUT_IMAGE_DIR> [--height <HEIGHT>] [--width <WIDTH>] [-c <COLOR>] [-k <KB>]
```

#### 参数说明

##### 基本参数

- `-u`, `--url`

  - **描述**: API 服务的 URL。
  - **默认值**: `http://127.0.0.1:8080`

- `-t`, `--type`

  - **描述**: 请求 API 的种类。
  - **默认值**: `idphoto`

- `-i`, `--input_image_dir`

  - **描述**: 输入图像路径。
  - **必需**: 是
  - **示例**: `./input_images/photo.jpg`

- `-o`, `--output_image_dir`
  - **描述**: 保存图像路径。
  - **必需**: 是
  - **示例**: `./output_images/processed_photo.jpg`

##### 可选参数

- `--face_detect_model`
  - **描述**: 人脸检测模型
  - **默认值**: mtcnn

- `--human_matting_model`
  - **描述**: 人像抠图模型
  - **默认值**: hivision_modnet

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
  - **示例**: 50

- `-r`, `--render`
  - **描述**: 给透明图增加背景色时的渲染方式，仅在 type 为`add_background`和`generate_layout_photos`时生效
  - **默认值**: 0

### 1.生成证件照(底透明)

```bash
python requests_api.py  \
    -u http://127.0.0.1:8080 \
    -t idphoto \
    -i ./photo.jpg \
    -o ./idphoto.png \
    --height 413 \
    --width 295 \
    --face_detect_model mtcnn \
    --human_matting_model hivision_modnet
```

### 2.添加背景色

```bash
python requests_api.py  \
    -u http://127.0.0.1:8080  \
    -t add_background  \
    -i ./idphoto.png  \
    -o ./idphoto_with_background.jpg  \
    -c 638cce  \
    -k 50 \
    -r 0
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


### 4.人像抠图

```bash
python requests_api.py  \
    -u http://127.0.0.1:8080  \
    -t human_matting  \
    -i ./photo.jpg  \
    -o ./photo_matting.png
    --human_matting_model hivision_modnet
```

### 请求失败的情况

- 照片中检测到的人脸大于 1，则失败

<br>

## Java 请求示例

### 添加 maven 依赖

```java
<dependency>
    <groupId>cn.hutool</groupId>
    <artifactId>hutool-all</artifactId>
    <version>5.8.16</version>
</dependency>

<dependency>
    <groupId>commons-io</groupId>
    <artifactId>commons-io</artifactId>
    <version>2.6</version>
</dependency>
```

### 运行代码

#### 1.生成证件照(底透明)

```java
/**
    * 生成证件照(底透明)  /idphoto 接口
    * @param inputImageDir 文件地址
    * @return
    * @throws IOException
    */
public static String requestIdPhoto(String inputImageDir) throws IOException {
    String url = BASE_URL+"/idphoto";
    // 创建文件对象
    File inputFile = new File(inputImageDir);
    Map<String, Object> paramMap=new HashMap<>();
    paramMap.put("input_image",inputFile);
    paramMap.put("height","413");
    paramMap.put("width","295");
    //包含status、image_base64_standard和image_base64_hd三项
    return HttpUtil.post(url, paramMap);
}
```

#### 2.添加背景色

```java
/**
    * 添加背景色  /add_background 接口
    * @param inputImageDir 文件地址
    * @return
    * @throws IOException
    */
public static String requestAddBackground(String inputImageDir) throws IOException {
    String url = BASE_URL+"/add_background";
    // 创建文件对象
    File inputFile = new File(inputImageDir);
    Map<String, Object> paramMap=new HashMap<>();
    paramMap.put("input_image",inputFile);
    paramMap.put("color","638cce");
    paramMap.put("kb","200");
    // response为一个json格式字典，包含status和image_base64
    return HttpUtil.post(url, paramMap);
}
```

#### 3.生成六寸排版照

```java
/**
    * 生成六寸排版照  /generate_layout_photos 接口
    * @param inputImageDir 文件地址
    * @return
    * @throws IOException
    */
public static String requestGenerateLayoutPhotos(String inputImageDir) throws IOException {
    String url = BASE_URL+"/generate_layout_photos";
    // 创建文件对象
    File inputFile = new File(inputImageDir);
    Map<String, Object> paramMap=new HashMap<>();
    paramMap.put("input_image",inputFile);
    paramMap.put("height","413");
    paramMap.put("width","295");
    paramMap.put("kb","200");
    //response为一个json格式字典，包含status和image_base64
    return HttpUtil.post(url, paramMap);
}
```

#### 4.人像抠图

```java
/**
    * 生成人像抠图照  /human_matting 接口
    * @param inputImageDir 文件地址
    * @return
    * @throws IOException
    */
public static String requestHumanMattingPhotos(String inputImageDir) throws IOException {
    String url = BASE_URL+"/human_matting";
    // 创建文件对象
    File inputFile = new File(inputImageDir);
    Map<String, Object> paramMap=new HashMap<>();
    paramMap.put("input_image",inputFile);
    //包含status、image_base64
    return HttpUtil.post(url, paramMap);
}
```

<br>

## JavaScript 请求示例

在JavaScript中，我们可以使用`fetch` API来发送HTTP请求。以下是如何使用JavaScript调用这些API的示例。

### 1. 生成证件照(底透明)

```javascript
async function generateIdPhoto(inputImagePath, height, width) {
    const url = "http://127.0.0.1:8080/idphoto";
    const formData = new FormData();
    formData.append("input_image", new File([await fetch(inputImagePath).then(res => res.blob())], "test.jpg"));
    formData.append("height", height);
    formData.append("width", width);

    const response = await fetch(url, {
        method: 'POST',
        body: formData
    });

    const result = await response.json();
    console.log(result);
    return result;
}

// 示例调用
generateIdPhoto("images/test.jpg", 413, 295).then(response => {
    console.log(response);
});
```

### 2. 添加背景色

```javascript
async function addBackground(inputImagePath, color, kb) {
    const url = "http://127.0.0.1:8080/add_background";
    const formData = new FormData();
    formData.append("input_image", new File([await fetch(inputImagePath).then(res => res.blob())], "test.png"));
    formData.append("color", color);
    formData.append("kb", kb);

    const response = await fetch(url, {
        method: 'POST',
        body: formData
    });

    const result = await response.json();
    console.log(result);
    return result;
}

// 示例调用
addBackground("test.png", "638cce", 200).then(response => {
    console.log(response);
});
```

### 3. 生成六寸排版照

```javascript
async function generateLayoutPhotos(inputImagePath, height, width, kb) {
    const url = "http://127.0.0.1:8080/generate_layout_photos";
    const formData = new FormData();
    formData.append("input_image", new File([await fetch(inputImagePath).then(res => res.blob())], "test.jpg"));
    formData.append("height", height);
    formData.append("width", width);
    formData.append("kb", kb);

    const response = await fetch(url, {
        method: 'POST',
        body: formData
    });

    const result = await response.json();
    console.log(result);
    return result;
}

// 示例调用
generateLayoutPhotos("test.jpg", 413, 295, 200).then(response => {
    console.log(response);
});
```

### 4.人像抠图

```javascript
async function uploadImage(inputImagePath) {
    const url = "http://127.0.0.1:8080/human_matting";
    const formData = new FormData();
    formData.append("input_image", new File([await fetch(inputImagePath).then(res => res.blob())], "test.jpg"));

    const response = await fetch(url, {
        method: 'POST',
        body: formData
    });

    const result = await response.json(); // 假设响应是JSON格式
    console.log(result);
    return result;
}

// 示例调用
uploadImage("demo/images/test.jpg").then(response => {
    console.log(response);
});
```