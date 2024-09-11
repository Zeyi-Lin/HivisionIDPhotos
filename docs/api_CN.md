# API Docs

[English](api_EN.md) / 中文 / [日本語](api_JP.md) / [한국어](api_KO.md)


## 目录

- [开始之前：开启后端服务](#开始之前开启后端服务)
- [接口功能说明](#接口功能说明)
- [cURL 请求示例](#curl-请求示例)
- [Python 请求示例](#python-请求示例)
- [Java 请求示例](#java-请求示例)
- [Javascript 请求示例](#javascript-请求示例)

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
-F "human_matting_model=hivision_modnet" \
-F "face_detect_model=mtcnn" \
-F "hd=true"
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
-F "input_image=@demo/images/test0.jpg" \
-F "human_matting_model=hivision_modnet"
```

### 5. 图片加水印
```bash
curl -X 'POST' \
  'http://127.0.0.1:8080/watermark?size=20&opacity=0.5&angle=30&color=%23000000&space=25' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'input_image=@demo/images/test0.jpg;type=image/jpeg' \
  -F 'text=Hello'
```

### 6. 设置图像KB大小
```bash
curl -X 'POST' \
  'http://127.0.0.1:8080/set_kb' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'input_image=@demo/images/test0.jpg;type=image/jpeg' \
  -F 'kb=50'
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
  -F 'hd=true'
```

<br>

## Python 请求示例

#### 1.生成证件照(底透明)

```python
import requests

url = "http://127.0.0.1:8080/idphoto"
input_image_path = "demo/images/test0.jpg"

files = {"input_image": open(input_image_path, "rb")}
data = {"height": 413, "width": 295, "human_matting_model": "hivision_modnet", "face_detect_model": "mtcnn", "hd": True}

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

#### 5.图片加水印

```python
import requests

# 设置请求的 URL 和参数
url = "http://127.0.0.1:8080/watermark"
params = {"size": 20, "opacity": 0.5, "angle": 30, "color": "#000000", "space": 25}

# 设置文件和其他表单数据
input_image_path = "demo/images/test0.jpg"
files = {"input_image": open(input_image_path, "rb")}
data = {"text": "Hello"}

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
data = {"kb": 50}

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
    "hd": "true"
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

### 5.图像加水印

```java
/**
 * 添加水印到图片 /watermark 接口
 * @param inputImageDir 文件地址
 * @param text 水印文本
 * @param size 水印文字大小
 * @param opacity 水印透明度
 * @param angle 水印旋转角度
 * @param color 水印颜色
 * @param space 水印间距
 * @return
 * @throws IOException
 */
public static String requestAddWatermark(String inputImageDir, String text, int size, double opacity, int angle, String color, int space) throws IOException {
    String url = BASE_URL + "/watermark?size=" + size + "&opacity=" + opacity + "&angle=" + angle + "&color=" + color + "&space=" + space;
    
    // 创建文件对象
    File inputFile = new File(inputImageDir);
    
    // 创建参数映射
    Map<String, Object> paramMap = new HashMap<>();
    paramMap.put("input_image", inputFile);
    paramMap.put("text", text);
    
    // 发送POST请求并返回响应
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
uploadImage("demo/images/test0.jpg").then(response => {
    console.log(response);
});
```

### 5.图像加水印

```javascript
async function sendMultipartRequest() {
    const url = "http://127.0.0.1:8080/watermark?size=20&opacity=0.5&angle=30&color=%23000000&space=25";

    const formData = new FormData();
    formData.append("text", "Hello");

    // Assuming you have a file input element with id 'fileInput'
    const fileInput = document.getElementById('fileInput');
    if (fileInput.files.length > 0) {
        formData.append("input_image", fileInput.files[0]);
    }

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json'
            },
            body: formData
        });

        if (response.ok) {
            const jsonResponse = await response.json();
            console.log(jsonResponse);
        } else {
            console.error('Request failed:', response.status, response.statusText);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Call the function to send request
sendMultipartRequest();
```