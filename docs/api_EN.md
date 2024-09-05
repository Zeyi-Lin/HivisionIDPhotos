# API Documentation

## TOC

- [Before You Start: Launch the Backend Service](#before-you-start-launch-the-backend-service)
- [Interface Function Descriptions](#interface-function-descriptions)
- [Python Request Example](#python-request-example)
  - [Python Requests Method](#1️⃣-python-requests-method)
  - [Python Script Method](#2️⃣-python-script-request-method)
- [Java Request Example](#java-request-example)

## Before You Start: Launch the Backend Service

Before making API requests, please run the backend service:

```bash
python deploy_api.py
```

<br>

## Interface Function Descriptions

### 1. Generate ID Photo (Transparent Background)

Interface Name: `idphoto`

The `Generate ID Photo` interface logic involves sending an RGB image and receiving a standard ID photo and a high-definition ID photo:

- **High-Definition ID Photo**: An ID photo made according to the aspect ratio of `size`, with the filename being `output_image_dir` appended with `_hd` suffix.
- **Standard ID Photo**: A photo with dimensions equal to `size`, scaled from the high-definition ID photo, with the filename being `output_image_dir`.

It should be noted that both generated photos are transparent (RGBA four-channel images). To produce a complete ID photo, the following `Add Background Color` interface is also required.

> Q: Why is this design used?  
> A: In actual products, users often need to frequently switch background colors to preview effects. Providing a transparent background image and allowing the front-end JavaScript code to synthesize the color offers a better user experience.

### 2. Add Background Color

Interface Name: `add_background`

The `Add Background Color` interface logic involves sending an RGBA image, adding a background color based on `color`, and synthesizing a JPG image.

### 3. Generate 6-inch Layout Photo

Interface Name: `generate_layout_photos`

The `Generate 6-inch Layout Photo` interface logic involves sending an RGB image (usually an ID photo after adding a background color), arranging the photos according to `size`, and then generating a 6-inch layout photo.

<br>

## Python Request Example

### 1️⃣ Python Requests Method

#### 1. Generate ID Photo (Transparent Background)

```python
import requests

url = "http://127.0.0.1:8080/idphoto"
input_image_path = "images/test.jpg"

files = {"input_image": open(input_image_path, "rb")}
data = {"height": 413, "width": 295}

response = requests.post(url, files=files, data=data).json()

# response is a JSON dictionary containing status, image_base64_standard, and image_base64_hd
print(response)
```

#### 2. Add Background Color

```python
import requests

url = "http://127.0.0.1:8080/add_background"
input_image_path = "test.png"

files = {"input_image": open(input_image_path, "rb")}
data = {"color": '638cce', 'kb': None}

response = requests.post(url, files=files, data=data).json()

# response is a JSON dictionary containing status and image_base64
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

# response is a JSON dictionary containing status and image_base64
print(response)
```

<br>

### 2️⃣ Python Script Request Method

```bash
python requests_api.py -u <URL> -t <TYPE> -i <INPUT_IMAGE_DIR> -o <OUTPUT_IMAGE_DIR> [--height <HEIGHT>] [--width <WIDTH>] [-c <COLOR>] [-k <KB>]
```

#### Parameter Descriptions

##### Basic Parameters

- `-u`, `--url`

  - **Description**: The URL of the API service.
  - **Default Value**: `http://127.0.0.1:8080`

- `-t`, `--type`

  - **Description**: The type of API request, with optional values being `idphoto`, `add_background`, and `generate_layout_photos`. They represent ID photo creation, transparent image background addition, and layout photo generation, respectively.
  - **Default Value**: `idphoto`

- `-i`, `--input_image_dir`

  - **Description**: The path of the input image.
  - **Required**: Yes
  - **Example**: `./input_images/photo.jpg`

- `-o`, `--output_image_dir`
  - **Description**: The path to save the image.
  - **Required**: Yes
  - **Example**: `./output_images/processed_photo.jpg`

##### Optional Parameters

- `--height`

  - **Description**: The height of the output size for the standard ID photo.
  - **Default Value**: 413

- `--width`

  - **Description**: The width of the output size for the standard ID photo.
  - **Default Value**: 295

- `-c`, `--color`

  - **Description**: Adds a background color to the transparent image, in Hex format (e.g., #638cce), only effective when the type is `add_background`.
  - **Default Value**: `638cce`

- `-k`, `--kb`
  - **Description**: The KB value of the output photo, only effective when the type is `add_background` or `generate_layout_photos`, and no setting is made when the value is None.
  - **Default Value**: `None`
  - **Example**: `50`

#### 1. Generate ID Photo (Transparent Background)

```bash
python requests_api.py  \
    -u http://127.0.0.1:8080 \
    -t idphoto \
    -i ./photo.jpg \
    -o ./idphoto.png \
    --height 413 \
    --width 295
```

#### 2. Add Background Color

```bash
python requests_api.py  \
    -u http://127.0.0.1:8080  \
    -t add_background  \
    -i ./idphoto.png  \
    -o ./idphoto_with_background.jpg  \
    -c 638cce  \
    -k 50
```

#### 3. Generate 6-inch Layout Photo

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

#### Request Failure Scenarios

- The request fails if more than one face is detected in the photo.

## Java Request Example

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

### Running the Code

#### 1. Generate ID Photo (Transparent Background)

```java
    /**
     * Generate ID Photo (Transparent Background) /idphoto interface
     * @param inputImageDir File address
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
     * Add Background Color /add_background interface
     * @param inputImageDir File address
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
        // Response is a JSON dictionary containing status and image_base64
        return HttpUtil.post(url, paramMap);
    }
```

#### 3. Generate 6-inch Layout Photo

```java
    /**
     * Generate 6-inch Layout Photo /generate_layout_photos interface
     * @param inputImageDir File address
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
        // Response is a JSON dictionary containing status and image_base64
        return HttpUtil.post(url, paramMap);
    }
```

#### 4. Summary

```java

import cn.hutool.http.HttpUtil;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import org.apache.commons.io.FileUtils;
import org.springframework.util.StringUtils;
import java.io.File;
import java.io.IOException;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;

/**
 * @author: qingshuang
 * @createDate: 2024/09/05
 * @description: Java generate ID photo, test case
 */
public class Test {
    /**
     * Interface address
     */
    private final static String BASE_URL = "http://127.0.0.1:8080";

    /**
     * Generate ID Photo (Transparent Background) /idphoto interface
     * @param inputImageDir File address
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
        return HttpUtil.post(url, paramMap);
    }
    /**
     * Add Background Color /add_background interface
     * @param inputImageDir File address
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
        return HttpUtil.post(url, paramMap);
    }
    /**
     * Generate 6-inch Layout Photo /generate_layout_photos interface
     * @param inputImageDir File address
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
        return HttpUtil.post(url, paramMap);
    }
    /**
     * Generate ID Photo (Transparent Background)
     * @param inputImageDir Source file address
     * @param outputImageDir Output file address
     * @throws IOException
     */
    private static void requestIdPhotoToImage(String inputImageDir, String outputImageDir) throws IOException {
        String res =requestIdPhoto(inputImageDir);
        // Convert to JSON
        JSONObject response= JSONUtil.parseObj(res);
        if(response.getBool("status")){// Request interface success
            String  image_base64_standard= response.getStr("image_base64_standard");
            String  image_base64_hd =response.getStr("image_base64_hd");
            String[] outputImageDirArr= StringUtils.split(outputImageDir,".");
            // Base64 save as image
            FileUtils.writeByteArrayToFile(new File(outputImageDirArr[0]+"_standard."+outputImageDirArr[1]),  Base64.getDecoder().decode(image_base64_standard));
            FileUtils.writeByteArrayToFile(new File(outputImageDirArr[0]+"_hd."+outputImageDirArr[1]),  Base64.getDecoder().decode(image_base64_hd));
        }
    }
    /**
     * Add Background Color
     * @param inputImageDir Source file address
     * @param outputImageDir Output file address
     * @throws IOException
     */
    private static void requestAddBackgroundToImage(String inputImageDir, String outputImageDir) throws IOException {
        String res =requestAddBackground(inputImageDir);
        // Convert to JSON
        JSONObject response= JSONUtil.parseObj(res);
        if(response.getBool("status")){// Request interface success
            String  image_base64= response.getStr("image_base64");
            String[] outputImageDirArr= StringUtils.split(outputImageDir,".");
            // Base64 save as image
            FileUtils.writeByteArrayToFile(new File(outputImageDirArr[0]+"_background."+outputImageDirArr[1]),  Base64.getDecoder().decode(image_base64));
        }
    }
    /**
     * Generate 6-inch Layout Photo
     * @param inputImageDir Source file address
     * @param outputImageDir Output file address
     * @throws IOException
     */
    private static void requestGenerateLayoutPhotosToImage(String inputImageDir, String outputImageDir) throws IOException {
        String res =requestGenerateLayoutPhotos(inputImageDir);
        // Convert to JSON
        JSONObject response= JSONUtil.parseObj(res);
        if(response.getBool("status")){// Request interface success
            String  image_base64= response.getStr("image_base64");
            String[] outputImageDirArr= StringUtils.split(outputImageDir,".");
            // Base64 save as image
            FileUtils.writeByteArrayToFile(new File(outputImageDirArr[0]+"_layout."+outputImageDirArr[1]),  Base64.getDecoder().decode(image_base64));
        }
    }

    public static void main(String[] args) {
        try {
            // Generate ID Photo (Transparent Background)
            requestIdPhotoToImage("C:\\Users\\Administrator\\Desktop\\1111.jpg","C:\\Users\\Administrator\\Desktop\\2222.png");
            // Add Background Color
            requestAddBackgroundToImage("C:\\Users\\Administrator\\Desktop\\2222_hd.png","C:\\Users\\Administrator\\Desktop\\idphoto_with_background.jpg");
            // Generate 6-inch Layout Photo
            requestGenerateLayoutPhotosToImage("C:\\Users\\Administrator\\Desktop\\1111.jpg","C:\\Users\\Administrator\\Desktop\\2222.png");

        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}

```
