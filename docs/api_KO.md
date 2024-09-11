# API 문서

[English](api_EN.md) / [中文](api_CN.md) / [日本語](api_JP.md) / 한국어


## 목차

- [시작하기: 백엔드 서비스 시작하기](#시작하기-백엔드-서비스-시작하기)
- [인터페이스 기능 설명](#인터페이스-기능-설명)
- [cURL 요청 예시](#curl-요청-예시)
- [Python 요청 예시](#python-요청-예시)
  - [Python Requests 요청 방법](#1️⃣-python-requests-요청-방법)
  - [Python 스크립트 요청 방법](#2️⃣-python-스크립트-요청-방법)
- [Java 요청 예시](#java-요청-예시)
- [JavaScript 요청 예시](#javascript-요청-예시)

## 시작하기: 백엔드 서비스 시작하기

API를 요청하기 전에 백엔드 서비스를 먼저 실행하세요.

```bash
python deploy_api.py
```

<br>

## 인터페이스 기능 설명

### 1. 증명사진 생성(투명 배경)

인터페이스 이름: `idphoto`

`증명사진 생성` 인터페이스의 논리는 RGB 이미지를 전송하고 표준 증명사진과 고해상도 증명사진을 출력하는 것입니다:

- **고해상도 증명사진**: `size`의 가로 세로 비율에 따라 제작된 증명사진, 파일 이름은 `output_image_dir`에 `_hd` 접미사를 추가한 것입니다.
- **표준 증명사진**: 크기가 `size`와 같으며, 고해상도 증명사진에서 축소된 것입니다, 파일 이름은 `output_image_dir`입니다.

생성된 두 장의 사진은 모두 투명합니다(RGBA 4채널 이미지), 완전한 증명사진을 생성하려면 아래의 `배경색 추가` 인터페이스가 필요합니다.

> 질문: 왜 이렇게 디자인했나요?  
> 답변: 실제 제품에서는 사용자가 배경색 미리보기를 자주 변경하므로, 투명 배경 이미지를 제공하고 프론트엔드 js 코드로 색상을 합성하는 것이 더 나은 경험을 제공합니다.

### 2. 배경색 추가

인터페이스 이름: `add_background`

`배경색 추가` 인터페이스의 논리는 RGBA 이미지를 전송하고 `color`에 따라 배경색을 추가하여 JPG 이미지를 합성하는 것입니다.

### 3. 6인치 레이아웃 사진 생성

인터페이스 이름: `generate_layout_photos`

`6인치 레이아웃 사진 생성` 인터페이스의 논리는 RGB 이미지를 전송하고(일반적으로 배경색 추가 후의 증명사진), `size`에 따라 사진을 배치한 다음 6인치 레이아웃 사진을 생성하는 것입니다.

### 4. 인물 추출

인터페이스 이름: `human_matting`

`인물 추출` 인터페이스의 논리는 RGB 이미지를 전송하고 표준 인물 사진과 고해상도 인물 사진(배경이 없는)을 출력하는 것입니다.

<br>

## cURL 요청 예시

cURL은 다양한 네트워크 프로토콜을 사용하여 데이터를 전송하는 명령줄 도구입니다. 다음은 cURL을 사용하여 이 API를 호출하는 예시입니다.

### 1. 증명사진 생성(투명 배경)

```bash
curl -X POST "http://127.0.0.1:8080/idphoto" \
-F "input_image=@demo/images/test0.jpg" \
-F "height=413" \
-F "width=295" \
-F "human_matting_model=hivision_modnet" \
-F "face_detect_model=mtcnn"
```

### 2. 배경색 추가

```bash
curl -X POST "http://127.0.0.1:8080/add_background" \
-F "input_image=@test.png" \
-F "color=638cce" \
-F "kb=200" \
-F "render=0"
```

### 3. 6인치 레이아웃 사진 생성

```bash
curl -X POST "http://127.0.0.1:8080/generate_layout_photos" \
-F "input_image=@test.jpg" \
-F "height=413" \
-F "width=295" \
-F "kb=200"
```

### 4. 인물 추출

```bash
curl -X POST "http://127.0.0.1:8080/human_matting" \
-F "input_image=@demo/images/test0.jpg" \
-F "human_matting_model=hivision_modnet"
```

<br>

## Python 요청 예시

### 1️⃣ Python Requests 요청 방법

#### 1. 증명사진 생성(투명 배경)

```python
import requests

url = "http://127.0.0.1:8080/idphoto"
input_image_path = "images/test0.jpg"

files = {"input_image": open(input_image_path, "rb")}
data = {"height": 413, "width": 295, "human_matting_model": "hivision_modnet", "face_detect_model": "mtcnn"}

response = requests.post(url, files=files, data=data).json()

# response는 status, image_base64_standard 및 image_base64_hd를 포함하는 JSON 형식의 사전입니다.
print(response)

```

#### 2. 배경색 추가

```python
import requests

url = "http://127.0.0.1:8080/add_background"
input_image_path = "test.png"

files = {"input_image": open(input_image_path, "rb")}
data = {"color": '638cce', "kb": None, "render": 0}

response = requests.post(url, files=files, data=data).json()

# response는 status와 image_base64를 포함하는 JSON 형식의 사전입니다.
print(response)
```

#### 3. 6인치 레이아웃 사진 생성

```python
import requests

url = "http://127.0.0.1:8080/generate_layout_photos"
input_image_path = "test.jpg"

files = {"input_image": open(input_image_path, "rb")}
data = {"height": 413, "width": 295, "kb": 200}

response = requests.post(url, files=files, data=data).json()

# response는 status와 image_base64를 포함하는 JSON 형식의 사전입니다.
print(response)
```

#### 4. 인물 추출

```python
import requests

url = "http://127.0.0.1:8080/human_matting"
input_image_path = "test.jpg"

files = {"input_image": open(input_image_path, "rb")}
data = {"human_matting_model": "hivision_modnet"}

response = requests.post(url, files=files, data=data).json()

# response는 status와 image_base64를 포함하는 JSON 형식의 사전입니다.
print(response)
```

### 2️⃣ Python 스크립트 요청 방법

```bash
python requests_api.py -u <URL> -t <TYPE> -i <INPUT_IMAGE_DIR> -o <OUTPUT_IMAGE_DIR> [--height <HEIGHT>] [--width <WIDTH>] [-c <COLOR>] [-k <KB>]
```

#### 매개변수 설명

##### 기본 매개변수

- `-u`, `--url`

  - **설명**: API 서비스의 URL입니다.
  - **기본값**: `http://127.0.0.1:8080`

- `-t`, `--type`

  - **설명**: 요청 API의 종류입니다.
  - **기본값**: `idphoto`

- `-i`, `--input_image_dir`

  - **설명**: 입력 이미지 경로입니다.
  - **필수**: 예
  - **예시**: `./input_images/photo.jpg`

- `-o`, `--output_image_dir`
  - **설명**: 저장 이미지 경로입니다.
  - **필수**: 예
  - **예시**: `./output_images/processed_photo.jpg`

##### 선택적 매개변수

- `--face_detect_model`
  - **설명**: 얼굴 인식 모델입니다.
  - **기본값**: mtcnn

- `--human_matting_model`
  - **설명**: 인물 추출 모델입니다.
  - **기본값**: hivision_modnet

- `--height`
  - **설명**: 표준 증명사진의 출력 사이즈 높이입니다.
  - **기본값**: 413

- `--width`
  - **설명**: 표준 증명사진의 출력 사이즈 너비입니다.
  - **기본값**: 295

- `-c`, `--color`
  - **설명**: 투명 이미지에 배경색을 추가합니다, 형식은 Hex(#638cce)입니다, type이 `add_background`일 때만 유효합니다.
  - **기본값**: `638cce`

- `-k`, `--kb`
  - **설명**: 출력 사진의 KB 값입니다, type이 `add_background`와 `generate_layout_photos`일 때만 유효하며, 값이 None일 때는 설정하지 않습니다.
  - **기본값**: `None`
  - **예시**: 50

- `-r`, `--render`
  - **설명**: 투명 이미지에 배경색을 추가할 때의 렌더링 방식입니다, type이 `add_background`와 `generate_layout_photos`일 때만 유효합니다.
  - **기본값**: 0

### 1. 증명사진 생성(투명 배경)

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

### 2. 배경색 추가

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

### 3. 6인치 레이아웃 사진 생성

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


### 4. 인물 추출

```bash
python requests_api.py  \
    -u http://127.0.0.1:8080  \
    -t human_matting  \
    -i ./photo.jpg  \
    -o ./photo_matting.png \
    --human_matting_model hivision_modnet
```

### 요청 실패의 경우

- 사진에서 감지된 얼굴이 1개 이상일 경우 실패합니다.

<br>

## Java 요청 예시

### Maven 의존성 추가

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

### 코드 실행

#### 1. 증명사진 생성(투명 배경)

```java
/**
    * 증명사진 생성(투명 배경)  /idphoto 인터페이스
    * @param inputImageDir 파일 주소
    * @return
    * @throws IOException
    */
public static String requestIdPhoto(String inputImageDir) throws IOException {
    String url = BASE_URL+"/idphoto";
    // 파일 객체 생성
    File inputFile = new File(inputImageDir);
    Map<String, Object> paramMap=new HashMap<>();
    paramMap.put("input_image",inputFile);
    paramMap.put("height","413");
    paramMap.put("width","295");
    // status, image_base64_standard 및 image_base64_hd를 포함합니다.
    return HttpUtil.post(url, paramMap);
}
```

#### 2. 배경색 추가

```java
/**
    * 배경색 추가  /add_background 인터페이스
    * @param inputImageDir 파일 주소
    * @return
    * @throws IOException
    */
public static String requestAddBackground(String inputImageDir) throws IOException {
    String url = BASE_URL+"/add_background";
    // 파일 객체 생성
    File inputFile = new File(inputImageDir);
    Map<String, Object> paramMap=new HashMap<>();
    paramMap.put("input_image",inputFile);
    paramMap.put("color","638cce");
    paramMap.put("kb","200");
    // response는 status와 image_base64를 포함하는 JSON 형식의 사전입니다.
    return HttpUtil.post(url, paramMap);
}
```

#### 3. 6인치 레이아웃 사진 생성

```java
/**
    * 6인치 레이아웃 사진 생성  /generate_layout_photos 인터페이스
    * @param inputImageDir 파일 주소
    * @return
    * @throws IOException
    */
public static String requestGenerateLayoutPhotos(String inputImageDir) throws IOException {
    String url = BASE_URL+"/generate_layout_photos";
    // 파일 객체 생성
    File inputFile = new File(inputImageDir);
    Map<String, Object> paramMap=new HashMap<>();
    paramMap.put("input_image",inputFile);
    paramMap.put("height","413");
    paramMap.put("width","295");
    paramMap.put("kb","200");
    // response는 status와 image_base64를 포함하는 JSON 형식의 사전입니다.
    return HttpUtil.post(url, paramMap);
}
```

#### 4. 인물 추출

```java
/**
    * 인물 추출 사진 생성  /human_matting 인터페이스
    * @param inputImageDir 파일 주소
    * @return
    * @throws IOException
    */
public static String requestHumanMattingPhotos(String inputImageDir) throws IOException {
    String url = BASE_URL+"/human_matting";
    // 파일 객체 생성
    File inputFile = new File(inputImageDir);
    Map<String, Object> paramMap=new HashMap<>();
    paramMap.put("input_image",inputFile);
    // status와 image_base64를 포함합니다.
    return HttpUtil.post(url, paramMap);
}
```

<br>

## JavaScript 요청 예시

JavaScript에서는 `fetch` API를 사용하여 HTTP 요청을 보낼 수 있습니다. 다음은 JavaScript를 사용하여 이 API를 호출하는 예시입니다.

### 1. 증명사진 생성(투명 배경)

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

// 예시 호출
generateIdPhoto("images/test0.jpg", 413, 295).then(response => {
    console.log(response);
});
```

### 2. 배경색 추가

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

// 예시 호출
addBackground("test.png", "638cce", 200).then(response => {
    console.log(response);
});
```

### 3. 6인치 레이아웃 사진 생성

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

// 예시 호출
generateLayoutPhotos("test.jpg", 413, 295, 200).then(response => {
    console.log(response);
});
```

### 4. 인물 추출

```javascript
async function uploadImage(inputImagePath) {
    const url = "http://127.0.0.1:8080/human_matting";
    const formData = new FormData();
    formData.append("input_image", new File([await fetch(inputImagePath).then(res => res.blob())], "test.jpg"));

    const response = await fetch(url, {
        method: 'POST',
        body: formData
    });

    const result = await response.json(); // 응답이 JSON 형식이라고 가정합니다.
    console.log(result);
    return result;
}

// 예시 호출
uploadImage("demo/images/test0.jpg").then(response => {
    console.log(response);
});
```