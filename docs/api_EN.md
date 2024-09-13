# API Docs

English / [中文](api_CN.md) / [日本語](api_JP.md) / [한국어](api_KO.md)

## Table of Contents

- [Before You Start: Start the Backend Service](#before-you-start-start-the-backend-service)
- [API Functionality Description](#api-functionality-description)
- [cURL Request Examples](#curl-request-examples)
- [Python Request Examples](#python-request-examples)
- [Java Request Examples](#java-request-examples)
- [JavaScript Request Examples](#javascript-request-examples)

## Before You Start: Start the Backend Service

Before making API requests, please run the backend service.

```bash
python deploy_api.py
```

<br>

## API Functionality Description

### 1. Generate ID Photo (Transparent Background)

API Name: `idphoto`

The logic of the `Generate ID Photo` API is to send an RGB image and output a standard ID photo and a high-definition ID photo:

- **High-Definition ID Photo**: An ID photo created based on the aspect ratio of `size`, with the filename being `output_image_dir` plus `_hd` suffix.
- **Standard ID Photo**: Size equals to `size`, scaled down from the high-definition ID photo, with the filename `output_image_dir`.

It is important to note that both generated photos are transparent (RGBA four-channel images). To generate a complete ID photo, you will also need the `Add Background Color` API below.

> Q: Why is it designed this way?  
> A: Because in actual products, users often switch background color previews frequently. Providing a transparent background image for the frontend JS code to synthesize colors is a better user experience.

### 2. Add Background Color

API Name: `add_background`

The logic of the `Add Background Color` API is to send an RGBA image and add a background color based on `color`, synthesizing a JPG image.

### 3. Generate 6-inch Layout Photo

API Name: `generate_layout_photos`

The logic of the `Generate 6-inch Layout Photo` API is to send an RGB image (generally the ID photo after adding background color), arrange the photos based on `size`, and then generate a 6-inch layout photo.

### 4. Human Matting

API Name: `human_matting`

The logic of the `Human Matting` API is to send an RGB image and output a standard matting portrait and a high-definition matting portrait (without any background filling).

<br>

## cURL Request Examples

cURL is a command-line tool used to transfer data with various network protocols. Below are examples of calling these APIs using cURL.

### 1. Generate ID Photo (Transparent Background)

```bash
curl -X POST "http://127.0.0.1:8080/idphoto" \
-F "input_image=@demo/images/test0.jpg" \
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

### 3. Generate 6-inch Layout Photo

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
-F "input_image=@demo/images/test0.jpg" \
-F "human_matting_model=hivision_modnet"
```

### 5. Add Watermark to Image
```bash
curl -X 'POST' \
  'http://127.0.0.1:8080/watermark?size=20&opacity=0.5&angle=30&color=%23000000&space=25' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'input_image=@demo/images/test0.jpg;type=image/jpeg' \
  -F 'text=Hello'
```

<br>

## Python Request Examples

#### 1. Generate ID Photo (Transparent Background)

```python
import requests

url = "http://127.0.0.1:8080/idphoto"
input_image_path = "demo/images/test0.jpg"

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

#### 3. Generate 6-inch Layout Photo

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

#### 5. Add Watermark to Image

```python
import requests

# Set the request URL and parameters
url = "http://127.0.0.1:8080/watermark"
params = {"size": 20, "opacity": 0.5, "angle": 30, "color": "#000000", "space": 25}

# Set the file and other form data
input_image_path = "demo/images/test0.jpg"
files = {"input_image": open(input_image_path, "rb")}
data = {"text": "Hello"}

# Send POST request
response = requests.post(url, params=params, files=files, data=data)

# Check the response
if response.ok:
    # Output the response content
    print(response.json())
else:
    # Output the error information
    print(f"Request failed with status code {response.status_code}: {response.text}")
```

<br>

## Java Request Examples

### Add Maven Dependency

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

#### 3. Generate 6-inch Layout Photo

```java
/**
* Generate 6-inch Layout Photo /generate_layout_photos API
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

### 5. Add Watermark to Image

```java
/**
 * Add watermark to image /watermark API
 * @param inputImageDir File path
 * @param text Watermark text
 * @param size Watermark text size
 * @param opacity Watermark opacity
 * @param angle Watermark rotation angle
 * @param color Watermark color
 * @param space Watermark spacing
 * @return
 * @throws IOException
 */
public static String requestAddWatermark(String inputImageDir, String text, int size, double opacity, int angle, String color, int space) throws IOException {
    String url = BASE_URL + "/watermark?size=" + size + "&opacity=" + opacity + "&angle=" + angle + "&color=" + color + "&space=" + space;
    
    // Create file object
    File inputFile = new File(inputImageDir);
    
    // Create parameter mapping
    Map<String, Object> paramMap = new HashMap<>();
    paramMap.put("input_image", inputFile);
    paramMap.put("text", text);
    
    // Send POST request and return response
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

### 3. Generate 6-inch Layout Photo

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

    const result = await response.json(); // Assuming the response is in JSON format
    console.log(result);
    return result;
}

// Example call
uploadImage("demo/images/test0.jpg").then(response => {
    console.log(response);
});
```

### 5. Add Watermark to Image

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