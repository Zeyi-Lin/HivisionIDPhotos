# API Docs

[中文](api_CN.md) | English

## Table of Contents

- [Getting Started: Start the Backend Service](#getting-started-start-the-backend-service)
- [API Function Descriptions](#api-function-descriptions)
- [cURL Request Examples](#curl-request-examples)
- [Python Request Examples](#python-request-examples)
  - [Python Requests Method](#1️⃣-python-requests-method)
  - [Python Script Method](#2️⃣-python-script-method)
- [Java Request Examples](#java-request-examples)
- [JavaScript Request Examples](#javascript-request-examples)

## Getting Started: Start the Backend Service

Before making API requests, please start the backend service

```bash
python delopy_api.py
```

<br>

## API Function Descriptions

### 1. Generate ID Photo (Transparent Background)

API Name: `idphoto`

The logic of the `Generate ID Photo` API is to send an RGB image and output a standard ID photo and a high-definition ID photo:

- **High-definition ID Photo**: The ID photo created based on the aspect ratio of `size`, with the filename being `output_image_dir` with the `_hd` suffix added.
- **Standard ID Photo**: The size is equal to `size`, scaled from the high-definition ID photo, with the filename being `output_image_dir`.

It is important to note that both generated photos are transparent (RGBA four-channel images). To generate a complete ID photo, the following `Add Background Color` API is needed.

> Q: Why is it designed this way?  
> A: Because in actual products, users often switch background colors to preview effects frequently. Providing a transparent background image allows for a better experience with color composition done by frontend JS code.

### 2. Add Background Color

API Name: `add_background`

The logic of the `Add Background Color` API is to send an RGBA image and add a background color based on `color`, resulting in a JPG image.

### 3. Generate Six-Inch Layout Photo

API Name: `generate_layout_photos`

The logic of the `Generate Six-Inch Layout Photo` API is to send an RGB image (typically the ID photo after adding background color) and arrange the photos based on `size`, resulting in a six-inch layout photo.

### 4. Human Matting

API Name: `human_matting`

The logic of the `Human Matting` API is to send an RGB image and output a standard matting portrait and a high-definition matting portrait (with no background fill).

<br>

## cURL Request Examples

cURL is a command-line tool for transferring data using various network protocols. Below are examples of using cURL to call these APIs.

### 1. Generate ID Photo (Transparent Background)

```bash
curl -X POST "http://127.0.0.1:8080/idphoto" \
-F "input_image=@demo/images/test.jpg" \
-F "height=413" \
-F "width=295" \
-F "human_matting_model=hivision_modnet" \
-F "face_detect_model=mtcnn"
```

### 2. Add Background Color

```bash
curl -X POST "http://127.0.0.1:8080/add_background" \
-F "input_image=@test.png" \
-F "color=638cce" \
-F "kb=200" \
-F "render=0"
```

### 3. Generate Six-Inch Layout Photo

```bash
curl -X POST "http://127.0.0.1:8080/generate_layout_photos" \
-F "input_image=@test.jpg" \
-F "height=413" \
-F "width=295" \
-F "kb=200"
```

### 4. Human Matting

```bash
curl -X POST "http://127.0.0.1:8080/human_matting" \
-F "input_image=@demo/images/test.jpg" \
-F "human_matting_model=hivision_modnet"
```

<br>

## Python Request Examples

### 1️⃣ Python Requests Method

#### 1. Generate ID Photo (Transparent Background)

```python
import requests

url = "http://127.0.0.1:8080/idphoto"
input_image_path = "images/test.jpg"

files = {"input_image": open(input_image_path, "rb")}
data = {"height": 413, "width": 295, "human_matting_model": "hivision_modnet", "face_detect_model": "mtcnn"}

response = requests.post(url, files=files, data=data).json()

# response is a JSON formatted dictionary containing status, image_base64_standard, and image_base64_hd
print(response)
```

#### 2. Add Background Color

```python
import requests

url = "http://127.0.0.1:8080/add_background"
input_image_path = "test.png"

files = {"input_image": open(input_image_path, "rb")}
data = {"color": '638cce', "kb": None, "render": 0}

response = requests.post(url, files=files, data=data).json()

# response is a JSON formatted dictionary containing status and image_base64
print(response)
```

#### 3. Generate Six-Inch Layout Photo

```python
import requests

url = "http://127.0.0.1:8080/generate_layout_photos"
input_image_path = "test.jpg"

files = {"input_image": open(input_image_path, "rb")}
data = {"height": 413, "width": 295, "kb": 200}

response = requests.post(url, files=files, data=data).json()

# response is a JSON formatted dictionary containing status and image_base64
print(response)
```

#### 4. Human Matting

```python
import requests

url = "http://127.0.0.1:8080/human_matting"
input_image_path = "test.jpg"

files = {"input_image": open(input_image_path, "rb")}
data = {"human_matting_model": "hivision_modnet"}

response = requests.post(url, files=files, data=data).json()

# response is a JSON formatted dictionary containing status and image_base64
print(response)
```

### 2️⃣ Python Script Method

```bash
python requests_api.py -u <URL> -t <TYPE> -i <INPUT_IMAGE_DIR> -o <OUTPUT_IMAGE_DIR> [--height <HEIGHT>] [--width <WIDTH>] [-c <COLOR>] [-k <KB>]
```

#### Parameter Descriptions

##### Basic Parameters

- `-u`, `--url`

  - **Description**: The URL of the API service.
  - **Default Value**: `http://127.0.0.1:8080`

- `-t`, `--type`

  - **Description**: The type of API request.
  - **Default Value**: `idphoto`

- `-i`, `--input_image_dir`

  - **Description**: The path to the input image.
  - **Required**: Yes
  - **Example**: `./input_images/photo.jpg`

- `-o`, `--output_image_dir`
  - **Description**: The path to save the image.
  - **Required**: Yes
  - **Example**: `./output_images/processed_photo.jpg`

##### Optional Parameters

- `--face_detect_model`
  - **Description**: Face detection model
  - **Default Value**: mtcnn

- `--human_matting_model`
  - **Description**: Human matting model
  - **Default Value**: hivision_modnet

- `--height`
  - **Description**: The height of the output size for the standard ID photo.
  - **Default Value**: 413

- `--width`
  - **Description**: The width of the output size for the standard ID photo.
  - **Default Value**: 295

- `-c`, `--color`
  - **Description**: Add background color to the transparent image, format as Hex (e.g., #638cce), only effective when type is `add_background`
  - **Default Value**: `638cce`

- `-k`, `--kb`
  - **Description**: The KB value of the output photo, only effective when type is `add_background` or `generate_layout_photos`, no setting when the value is None.
  - **Default Value**: `None`
  - **Example**: 50

- `-r`, `--render`
  - **Description**: The rendering method for adding background color to the transparent image, only effective when type is `add_background` or `generate_layout_photos`
  - **Default Value**: 0

### 1. Generate ID Photo (Transparent Background)

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

### 2. Add Background Color

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

### 3. Generate Six-Inch Layout Photo

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

### 4. Human Matting

```bash
python requests_api.py  \
    -u http://127.0.0.1:8080  \
    -t human_matting  \
    -i ./photo.jpg  \
    -o ./photo_matting.png \
    --human_matting_model hivision_modnet
```

### Failure Cases

- If more than one face is detected in the photo, the request will fail.

<br>

## Java Request Examples

### Add Maven Dependencies

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

### Run Code

#### 1. Generate ID Photo (Transparent Background)

```java
/**
    * Generate ID Photo (Transparent Background) /idphoto API
    * @param inputImageDir File path
    * @return
    * @throws IOException
    */
public static String requestIdPhoto(String inputImageDir) throws IOException {
    String url = BASE_URL+"/idphoto";
    // Create file object
    File inputFile = new File(inputImageDir);
    Map<String, Object> paramMap=new HashMap<>();
    paramMap.put("input_image",inputFile);
    paramMap.put("height","413");
    paramMap.put("width","295");
    // Contains status, image_base64_standard, and image_base64_hd
    return HttpUtil.post(url, paramMap);
}
```

#### 2. Add Background Color

```java
/**
    * Add Background Color /add_background API
    * @param inputImageDir File path
    * @return
    * @throws IOException
    */
public static String requestAddBackground(String inputImageDir) throws IOException {
    String url = BASE_URL+"/add_background";
    // Create file object
    File inputFile = new File(inputImageDir);
    Map<String, Object> paramMap=new HashMap<>();
    paramMap.put("input_image",inputFile);
    paramMap.put("color","638cce");
    paramMap.put("kb","200");
    // response is a JSON formatted dictionary containing status and image_base64
    return HttpUtil.post(url, paramMap);
}
```

#### 3. Generate Six-Inch Layout Photo

```java
/**
    * Generate Six-Inch Layout Photo /generate_layout_photos API
    * @param inputImageDir File path
    * @return
    * @throws IOException
    */
public static String requestGenerateLayoutPhotos(String inputImageDir) throws IOException {
    String url = BASE_URL+"/generate_layout_photos";
    // Create file object
    File inputFile = new File(inputImageDir);
    Map<String, Object> paramMap=new HashMap<>();
    paramMap.put("input_image",inputFile);
    paramMap.put("height","413");
    paramMap.put("width","295");
    paramMap.put("kb","200");
    // response is a JSON formatted dictionary containing status and image_base64
    return HttpUtil.post(url, paramMap);
}
```

#### 4. Human Matting

```java
/**
    * Generate Human Matting Photo /human_matting API
    * @param inputImageDir File path
    * @return
    * @throws IOException
    */
public static String requestHumanMattingPhotos(String inputImageDir) throws IOException {
    String url = BASE_URL+"/human_matting";
    // Create file object
    File inputFile = new File(inputImageDir);
    Map<String, Object> paramMap=new HashMap<>();
    paramMap.put("input_image",inputFile);
    // Contains status and image_base64
    return HttpUtil.post(url, paramMap);
}
```

<br>

## JavaScript Request Examples

In JavaScript, we can use the `fetch` API to send HTTP requests. Below are examples of how to call these APIs using JavaScript.

### 1. Generate ID Photo (Transparent Background)

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

// Example call
generateIdPhoto("images/test.jpg", 413, 295).then(response => {
    console.log(response);
});
```

### 2. Add Background Color

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

// Example call
addBackground("test.png", "638cce", 200).then(response => {
    console.log(response);
});
```

### 3. Generate Six-Inch Layout Photo

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

// Example call
generateLayoutPhotos("test.jpg", 413, 295, 200).then(response => {
    console.log(response);
});
```

### 4. Human Matting

```javascript
async function uploadImage(inputImagePath) {
    const url = "http://127.0.0.1:8080/human_matting";
    const formData = new FormData();
    formData.append("input_image", new File([await fetch(inputImagePath).then(res => res.blob())], "test.jpg"));

    const response = await fetch(url, {
        method: 'POST',
        body: formData
    });

    const result = await response.json(); // Assume the response is in JSON format
    console.log(result);
    return result;
}

// Example call
uploadImage("demo/images/test.jpg").then(response => {
    console.log(response);
});
```