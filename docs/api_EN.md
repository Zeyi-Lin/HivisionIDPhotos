# API Docs

English / [中文](api_CN.md)

## Table of Contents

- [Before You Start: Start the Backend Service](#before-you-start-start-the-backend-service)
- [API Functionality Description](#api-functionality-description)
  - [1. Generate ID Photo (Transparent Background)](#1-generate-id-photo-transparent-background)
  - [2. Add Background Color](#2-add-background-color)
  - [3. Generate Six-Inch Layout Photo](#3-generate-six-inch-layout-photo)
  - [4. Human Matting](#4-human-matting)
  - [5. Add Watermark to Image](#5-add-watermark-to-image)
  - [6. Set Image KB Size](#6-set-image-kb-size)
  - [7. ID Photo Cropping](#7-id-photo-cropping)
- [cURL Request Examples](#curl-request-examples)
- [Python Request Examples](#python-request-examples)

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

- **High-definition ID Photo**: An ID photo created based on the aspect ratio of `size`, with the filename having `_hd` appended to `output_image_dir`.
- **Standard ID Photo**: The size equals `size`, scaled from the high-definition ID photo, with the filename as `output_image_dir`.

It is important to note that both generated photos are transparent (RGBA four-channel images). To create a complete ID photo, you will also need to use the `Add Background Color` API below.

> Q: Why is it designed this way?  
> A: Because in actual products, users frequently switch background color preview effects, providing a transparent background image for the front-end JS code to composite colors is a better experience.

**Request Parameters:**

| Parameter Name | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| input_image | file | Choose one of `input_image` or `input_image_base64` | The input image file, which needs to be an RGB three-channel image. |
| input_image_base64 | str | Choose one of `input_image` or `input_image_base64` | The base64 encoding of the input image file, which needs to be an RGB three-channel image. |
| height | int | No | The height of the standard ID photo, with a default value of `413`. |
| width | int | No | The width of the standard ID photo, with a default value of `295`. |
| human_matting_model | str | No | The human segmentation model, with a default value of `modnet_photographic_portrait_matting`. Available values are `modnet_photographic_portrait_matting`, `hivision_modnet`, `rmbg-1.4`, and `birefnet-v1-lite`. |
| face_detect_model | str | No | The face detection model, with a default value of `mtcnn`. Available values are `mtcnn`, `face_plusplus`, and `retinaface-resnet50`. |
| hd | bool | No | Whether to generate a high-definition ID photo, with a default value of `true`. |
| dpi | int | No | The image resolution, with a default value of `300`. |
| face_alignment | bool | No | Whether to perform face alignment, with a default value of `true`. |
| head_measure_ratio | float | No | The ratio of the face area to the photo area, with a default value of `0.2`. |
| head_height_ratio | float | No | The ratio of the face center to the top of the photo, with a default value of `0.45`. |
| top_distance_max | float | No | The maximum ratio of the head to the top of the photo, with a default value of `0.12`. |
| top_distance_min | float | No | The minimum ratio of the head to the top of the photo, with a default value of `0.1`. |

**Return Parameters:**

| Parameter Name | Type | Description |
| :--- | :--- | :--- |
| status | str | The status of the request, with a default value of `success`. |
| image_base64_standard | str | The base64 encoding of the standard ID photo. |
| image_base64_hd | str | The base64 encoding of the high-definition ID photo. |

### 2. Add Background Color

API Name: `add_background`

The logic of the `Add Background Color` API is to receive an RGBA image (transparent image) and add a background color based on `color`, composing a JPG image.

**Request Parameters:**

| Parameter Name | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| input_image | file | Choose one of `input_image` or `input_image_base64` | The input image file, which needs to be an RGB three-channel image. |
| input_image_base64 | str | Choose one of `input_image` or `input_image_base64` | The base64 encoding of the input image file, which needs to be an RGB three-channel image. |
| color | str | Yes | The background color in hexadecimal format, e.g., `#000000` for black. |
| kb | int | No | The target file size in KB. If the specified KB value is less than the original file, it adjusts the compression rate. If the specified KB value is greater than the source file, it increases the KB value by adding information to the file header, aiming for the final size of the image to match the specified KB value. |
| render | int | No | The rendering mode, with a default value of `0`. Available values are `0`, `1`, and `2`. |
| dpi | int | No | The image resolution, with a default value of `300`. |

**Return Parameters:**

| Parameter Name | Type | Description |
| :--- | :--- | :--- |
| status | str | The status of the request, with a default value of `success`. |
| image_base64 | str | The base64 encoding of the image with the background color added. |



### 3. Generate Six-Inch Layout Photo

API Name: `generate_layout_photos`

The logic of the `Generate Six-Inch Layout Photo` API is to receive an RGB image (usually the ID photo after adding background color), arrange the photos based on `size`, and then generate a six-inch layout photo.

**Request Parameters:**

| Parameter Name | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| input_image | file | Choose one of `input_image` or `input_image_base64` | The input image file, which needs to be an RGB three-channel image. |
| input_image_base64 | str | Choose one of `input_image` or `input_image_base64` | The base64 encoding of the input image file, which needs to be an RGB three-channel image. |
| height | int | No | The height of the standard ID photo, with a default value of `413`. |
| width | int | No | The width of the standard ID photo, with a default value of `295`. |
| kb | int | No | The target file size in KB. If the specified KB value is less than the original file, it adjusts the compression rate. If the specified KB value is greater than the source file, it increases the KB value by adding information to the file header, aiming for the final size of the image to match the specified KB value. |
| dpi | int | No | The image resolution, with a default value of `300`. |

**Return Parameters:**

| Parameter Name | Type | Description |
| :--- | :--- | :--- |
| status | str | The status of the request, with a default value of `success`. |
| image_base64 | str | The base64 encoding of the six-inch layout photo. |




### 4. Human Matting

API Name: `human_matting`

The logic of the `Human Matting` API is to receive an RGB image and output a standard matting portrait and a high-definition matting portrait (without any background filling).

**Request Parameters:**

| Parameter Name | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| input_image | file | Choose one of `input_image` or `input_image_base64` | The input image file, which needs to be an RGB three-channel image. |
| input_image_base64 | str | Choose one of `input_image` or `input_image_base64` | The base64 encoding of the input image file, which needs to be an RGB three-channel image. |
| human_matting_model | str | No | The human segmentation model, with a default value of `modnet_photographic_portrait_matting`. Available values are `modnet_photographic_portrait_matting`, `hivision_modnet`, `rmbg-1.4`, and `birefnet-v1-lite`. |
| dpi | int | No | The image resolution, with a default value of `300`. |

**Return Parameters:**

| Parameter Name | Type | Description |
| :--- | :--- | :--- |
| status | str | The status of the request, with a default value of `success`. |
| image_base64 | str | The base64 encoding of the human matting portrait. |




### 5. Add Watermark to Image

API Name: `watermark`

The functionality of the `Add Watermark to Image` API is to receive a watermark text and add the specified watermark to the original image. Users can specify attributes such as the watermark's position, opacity, and size to seamlessly blend the watermark into the original image.

**Request Parameters:**

| Parameter Name | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| input_image | file | Choose one of `input_image` or `input_image_base64` | The input image file, which needs to be an RGB three-channel image. |
| input_image_base64 | str | Choose one of `input_image` or `input_image_base64` | The base64 encoding of the input image file, which needs to be an RGB three-channel image. |
| text | str | Yes | The watermark text to be added. |
| size | int | No | The size of the watermark text, with a default value of `20`. |
| opacity | float | No | The opacity of the watermark text, with a default value of `0.5`. |
| angle | int | No | The angle of the watermark text, with a default value of `30`. |
| color | str | No | The color of the watermark text, with a default value of `#000000`. |
| space | int | No | The space between the watermark text and the image, with a default value of `25`. |
| dpi | int | No | The image resolution, with a default value of `300`. |

**Return Parameters:**

| Parameter Name | Type | Description |
| :--- | :--- | :--- |
| status | str | The status of the request, with a default value of `success`. |



### 6. Set Image KB Size

API Name: `set_kb`

The functionality of the `Set Image KB Size` API is to receive an image and a target file size (in KB). If the specified KB value is less than the original file, it adjusts the compression rate. If the specified KB value is greater than the source file, it increases the KB value by adding information to the file header, aiming for the final size of the image to match the specified KB value.

**Request Parameters:**

| Parameter Name | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| input_image | file | Choose one of `input_image` or `input_image_base64` | The input image file, which needs to be an RGB three-channel image. |
| input_image_base64 | str | Choose one of `input_image` or `input_image_base64` | The base64 encoding of the input image file, which needs to be an RGB three-channel image. |
| kb | int | Yes | The target file size in KB. |
| dpi | int | No | The image resolution, with a default value of `300`. |

**Return Parameters:**

| Parameter Name | Type | Description |
| :--- | :--- | :--- |
| status | str | The status of the request, with a default value of `success`. |
| image_base64 | str | The base64 encoding of the image with the specified KB size. |




### 7. ID Photo Cropping

API Name: `idphoto_crop`

The functionality of the `ID Photo Cropping` API is to receive an RGBA image (transparent image) and output a standard ID photo and a high-definition ID photo.

**Request Parameters:**

| Parameter Name | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| input_image | file | Choose one of `input_image` or `input_image_base64` | The input image file, which needs to be an RGB three-channel image. |
| input_image_base64 | str | Choose one of `input_image` or `input_image_base64` | The base64 encoding of the input image file, which needs to be an RGB three-channel image. |
| height | int | Yes | The height of the standard ID photo. |
| width | int | Yes | The width of the standard ID photo. |
| face_detect_model | str | No | The face detection model, with a default value of `mtcnn`. Available values are `mtcnn`, `face_plusplus`, and `retinaface-resnet50`. |
| hd | bool | No | Whether to generate a high-definition ID photo, with a default value of `true`. |
| dpi | int | No | The image resolution, with a default value of `300`. |
| head_measure_ratio | float | No | The ratio of the face area to the photo area, with a default value of `0.2`. |
| head_height_ratio | float | No | The ratio of the face center to the top of the photo, with a default value of `0.45`. |
| top_distance_max | float | No | The maximum ratio of the head to the top of the photo, with a default value of `0.12`. |
| top_distance_min | float | No | The minimum ratio of the head to the top of the photo, with a default value of `0.1`. |

**Return Parameters:**

| Parameter Name | Type | Description |
| :--- | :--- | :--- |
| status | str | The status of the request, with a default value of `success`. |
| image_base64 | str | The base64 encoding of the ID photo. |



<br>

## cURL Request Examples

cURL is a command-line tool for transferring data using various network protocols. Here are examples of using cURL to call these APIs.

### 1. Generate ID Photo (Transparent Background)

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

### 2. Add Background Color

```bash
curl -X POST "http://127.0.0.1:8080/add_background" \
-F "input_image=@test.png" \
-F "color=638cce" \
-F "kb=200" \
-F "render=0" \
-F "dpi=300"
```

### 3. Generate Six-Inch Layout Photo

```bash
curl -X POST "http://127.0.0.1:8080/generate_layout_photos" \
-F "input_image=@test.jpg" \
-F "height=413" \
-F "width=295" \
-F "kb=200" \
-F "dpi=300"
```

### 4. Human Matting

```bash
curl -X POST "http://127.0.0.1:8080/human_matting" \
-F "input_image=@demo/images/test0.jpg" \
-F "human_matting_model=modnet_photographic_portrait_matting" \
-F "dpi=300"
```

### 5. Add Watermark to Image
```bash
curl -X 'POST' \
  'http://127.0.0.1:8080/watermark?size=20&opacity=0.5&angle=30&color=%23000000&space=25' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'input_image=@demo/images/test0.jpg;type=image/jpeg' \
  -F 'text=Hello' \
  -F 'dpi=300'
```

### 6. Set Image KB Size
```bash
curl -X 'POST' \
  'http://127.0.0.1:8080/set_kb' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'input_image=@demo/images/test0.jpg;type=image/jpeg' \
  -F 'kb=50' \
  -F 'dpi=300'
```

### 7. ID Photo Cropping
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

## Python Request Examples

#### 1. Generate ID Photo (Transparent Background)
```python
import requests

url = "http://127.0.0.1:8080/idphoto"
input_image_path = "demo/images/test0.jpg"

# Set request parameters
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

# response is a JSON formatted dictionary containing status, image_base64_standard, and image_base64_hd
print(response)
```

#### 2. Add Background Color

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

# response is a JSON formatted dictionary containing status and image_base64
print(response)
```

#### 3. Generate Six-Inch Layout Photo

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

# response is a JSON formatted dictionary containing status and image_base64
print(response)
```

#### 4. Human Matting

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

# response is a JSON formatted dictionary containing status and image_base64
print(response)
```

#### 5. Add Watermark to Image

```python
import requests

# Set the request URL and parameters
url = "http://127.0.0.1:8080/watermark"
params = {
    "size": 20,
    "opacity": 0.5,
    "angle": 30,
    "color": "#000000",
    "space": 25,
}

# Set file and other form data
input_image_path = "demo/images/test0.jpg"
files = {"input_image": open(input_image_path, "rb")}
data = {"text": "Hello", "dpi": 300}

# Send POST request
response = requests.post(url, params=params, files=files, data=data)

# Check response
if response.ok:
    # Output response content
    print(response.json())
else:
    # Output error message
    print(f"Request failed with status code {response.status_code}: {response.text}")
```

### 6. Set Image KB Size

```python
import requests

# Set the request URL
url = "http://127.0.0.1:8080/set_kb"

# Set file and other form data
input_image_path = "demo/images/test0.jpg"
files = {"input_image": open(input_image_path, "rb")}
data = {"kb": 50, "dpi": 300}

# Send POST request
response = requests.post(url, files=files, data=data)

# Check response
if response.ok:
    # Output response content
    print(response.json())
else:
    # Output error message
    print(f"Request failed with status code {response.status_code}: {response.text}")
```

### 7. ID Photo Cropping

```python
import requests

# Set the request URL
url = "http://127.0.0.1:8080/idphoto_crop"

# Set request parameters
params = {
    "head_measure_ratio": 0.2,
    "head_height_ratio": 0.45,
    "top_distance_max": 0.12,
    "top_distance_min": 0.1,
}

# Set file and other form data
input_image_path = "idphoto_matting.png"
files = {"input_image": ("idphoto_matting.png", open(input_image_path, "rb"), "image/png")}
data = {
    "height": 413,
    "width": 295,
    "face_detect_model": "mtcnn",
    "hd": "true",
    "dpi": 300,
}

# Send POST request
response = requests.post(url, params=params, files=files, data=data)

# Check response
if response.ok:
    # Output response content
    print(response.json())
else:
    # Output error message
    print(f"Request failed with status code {response.status_code}: {response.text}")
```