# API Docs

[English](api_EN.md) / [中文](api_CN.md) / 日本語 / [한국어](api_KO.md)

## 目次

- [始める前に：バックエンドサービスを起動する](#始める前にバックエンドサービスを起動する)
- [インターフェース機能説明](#インターフェース機能説明)
- [cURL リクエスト例](#curl-リクエスト例)
- [Python リクエスト例](#python-リクエスト例)
  - [Python Requests リクエスト方法](#1️⃣-python-requests-リクエスト方法)
  - [Python スクリプトリクエスト方法](#2️⃣-python-スクリプトリクエスト方法)
- [Java リクエスト例](#java-リクエスト例)
- [Javascript リクエスト例](#javascript-リクエスト例)

## 始める前に：バックエンドサービスを起動する

API をリクエストする前に、バックエンドサービスを実行してください。

```bash
python deploy_api.py
```

<br>

## インターフェース機能説明

### 1.証明写真を生成する（透明な背景）

インターフェース名：`idphoto`

`証明写真を生成する`インターフェースのロジックは、RGB画像を送信し、標準の証明写真と高解像度の証明写真を出力します：

- **高解像度の証明写真**：`size`のアスペクト比に基づいて作成された証明写真で、ファイル名は`output_image_dir`に`_hd`という接尾辞が追加されます。
- **標準の証明写真**：サイズは`size`と等しく、高解像度の証明写真からスケーリングされ、ファイル名は`output_image_dir`です。

生成される2枚の写真はどちらも透明です（RGBA 4チャンネル画像）ので、完全な証明写真を生成するには、以下の`背景色を追加する`インターフェースが必要です。

> 質問：なぜこのように設計されているのですか？  
> 答え：実際の製品では、ユーザーが頻繁に背景色を切り替えてプレビュー効果を確認するため、透明な背景画像を直接提供し、フロントエンドのjsコードで色を合成する方がより良い体験となります。

### 2.背景色を追加する

インターフェース名：`add_background`

`背景色を追加する`インターフェースのロジックは、RGBA画像を送信し、`color`に基づいて背景色を追加し、JPG画像を合成します。

### 3.六寸レイアウト写真を生成する

インターフェース名：`generate_layout_photos`

`六寸レイアウト写真を生成する`インターフェースのロジックは、RGB画像（一般的には背景色を追加した後の証明写真）を送信し、`size`に基づいて写真を配置し、六寸レイアウト写真を生成します。

### 4.人物切り抜き

インターフェース名：`human_matting`

`人物切り抜き`インターフェースのロジックは、RGB画像を送信し、標準の切り抜き人物写真と高解像度の切り抜き人物写真（背景が何も填充されていない）を出力します。

<br>

## cURL リクエスト例

cURLは、さまざまなネットワークプロトコルを使用してデータを転送するためのコマンドラインツールです。以下は、cURLを使用してこれらのAPIを呼び出す例です。

### 1. 証明写真を生成する（透明な背景）

```bash
curl -X POST "http://127.0.0.1:8080/idphoto" \
-F "input_image=@demo/images/test0.jpg" \
-F "height=413" \
-F "width=295" \
-F "human_matting_model=hivision_modnet" \
-F "face_detect_model=mtcnn"
```

### 2. 背景色を追加する

```bash
curl -X POST "http://127.0.0.1:8080/add_background" \
-F "input_image=@test.png" \
-F "color=638cce" \
-F "kb=200" \
-F "render=0"
```

### 3. 六寸レイアウト写真を生成する

```bash
curl -X POST "http://127.0.0.1:8080/generate_layout_photos" \
-F "input_image=@test.jpg" \
-F "height=413" \
-F "width=295" \
-F "kb=200"
```

### 4. 人物切り抜き

```bash
curl -X POST "http://127.0.0.1:8080/human_matting" \
-F "input_image=@demo/images/test0.jpg" \
-F "human_matting_model=hivision_modnet"
```

<br>

## Python リクエスト例

### 1️⃣ Python Requests リクエスト方法

#### 1.証明写真を生成する（透明な背景）

```python
import requests

url = "http://127.0.0.1:8080/idphoto"
input_image_path = "images/test0.jpg"

files = {"input_image": open(input_image_path, "rb")}
data = {"height": 413, "width": 295, "human_matting_model": "hivision_modnet", "face_detect_model": "mtcnn"}

response = requests.post(url, files=files, data=data).json()

# responseはjson形式の辞書で、status、image_base64_standard、image_base64_hdの3項目を含みます
print(response)

```

#### 2.背景色を追加する

```python
import requests

url = "http://127.0.0.1:8080/add_background"
input_image_path = "test.png"

files = {"input_image": open(input_image_path, "rb")}
data = {"color": '638cce', "kb": None, "render": 0}

response = requests.post(url, files=files, data=data).json()

# responseはjson形式の辞書で、statusとimage_base64を含みます
print(response)
```

#### 3.六寸レイアウト写真を生成する

```python
import requests

url = "http://127.0.0.1:8080/generate_layout_photos"
input_image_path = "test.jpg"

files = {"input_image": open(input_image_path, "rb")}
data = {"height": 413, "width": 295, "kb": 200}

response = requests.post(url, files=files, data=data).json()

# responseはjson形式の辞書で、statusとimage_base64を含みます
print(response)
```

#### 4.人物切り抜き

```python
import requests

url = "http://127.0.0.1:8080/human_matting"
input_image_path = "test.jpg"

files = {"input_image": open(input_image_path, "rb")}
data = {"human_matting_model": "hivision_modnet"}

response = requests.post(url, files=files, data=data).json()

# responseはjson形式の辞書で、statusとimage_base64を含みます
print(response)
```

### 2️⃣ Python スクリプトリクエスト方法

```bash
python requests_api.py -u <URL> -t <TYPE> -i <INPUT_IMAGE_DIR> -o <OUTPUT_IMAGE_DIR> [--height <HEIGHT>] [--width <WIDTH>] [-c <COLOR>] [-k <KB>]
```

#### パラメータ説明

##### 基本パラメータ

- `-u`, `--url`

  - **説明**: APIサービスのURL。
  - **デフォルト値**: `http://127.0.0.1:8080`

- `-t`, `--type`

  - **説明**: APIをリクエストする種類。
  - **デフォルト値**: `idphoto`

- `-i`, `--input_image_dir`

  - **説明**: 入力画像のパス。
  - **必須**: はい
  - **例**: `./input_images/photo.jpg`

- `-o`, `--output_image_dir`
  - **説明**: 画像の保存パス。
  - **必須**: はい
  - **例**: `./output_images/processed_photo.jpg`

##### オプションパラメータ

- `--face_detect_model`
  - **説明**: 顔検出モデル
  - **デフォルト値**: mtcnn

- `--human_matting_model`
  - **説明**: 人物切り抜きモデル
  - **デフォルト値**: hivision_modnet

- `--height`,
  - **説明**: 標準証明写真の出力サイズの高さ。
  - **デフォルト値**: 413

- `--width`,
  - **説明**: 標準証明写真の出力サイズの幅。
  - **デフォルト値**: 295

- `-c`, `--color`
  - **説明**: 透明画像に背景色を追加する、形式はHex（例：#638cce）、typeが`add_background`のときのみ有効
  - **デフォルト値**: `638cce`

- `-k`, `--kb`
  - **説明**: 出力写真のKB値、typeが`add_background`と`generate_layout_photos`のときのみ有効、値がNoneのときは設定しません。
  - **デフォルト値**: `None`
  - **例**: 50

- `-r`, `--render`
  - **説明**: 透明画像に背景色を追加する際のレンダリング方式、typeが`add_background`と`generate_layout_photos`のときのみ有効
  - **デフォルト値**: 0

### 1.証明写真を生成する（透明な背景）

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

### 2.背景色を追加する

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

### 3.六寸レイアウト写真を生成する

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

### 4.人物切り抜き

```bash
python requests_api.py  \
    -u http://127.0.0.1:8080  \
    -t human_matting  \
    -i ./photo.jpg  \
    -o ./photo_matting.png \
    --human_matting_model hivision_modnet
```

### リクエスト失敗の状況

- 写真に検出された顔が1つを超える場合、失敗します。

<br>

## Java リクエスト例

### Maven依存関係を追加

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

### コードを実行する

#### 1.証明写真を生成する（透明な背景）

```java
/**
    * 証明写真を生成する（透明な背景） /idphoto インターフェース
    * @param inputImageDir ファイルのパス
    * @return
    * @throws IOException
    */
public static String requestIdPhoto(String inputImageDir) throws IOException {
    String url = BASE_URL+"/idphoto";
    // ファイルオブジェクトを作成
    File inputFile = new File(inputImageDir);
    Map<String, Object> paramMap=new HashMap<>();
    paramMap.put("input_image",inputFile);
    paramMap.put("height","413");
    paramMap.put("width","295");
    // status、image_base64_standard、image_base64_hdの3項目を含みます
    return HttpUtil.post(url, paramMap);
}
```

#### 2.背景色を追加する

```java
/**
    * 背景色を追加する /add_background インターフェース
    * @param inputImageDir ファイルのパス
    * @return
    * @throws IOException
    */
public static String requestAddBackground(String inputImageDir) throws IOException {
    String url = BASE_URL+"/add_background";
    // ファイルオブジェクトを作成
    File inputFile = new File(inputImageDir);
    Map<String, Object> paramMap=new HashMap<>();
    paramMap.put("input_image",inputFile);
    paramMap.put("color","638cce");
    paramMap.put("kb","200");
    // responseはjson形式の辞書で、statusとimage_base64を含みます
    return HttpUtil.post(url, paramMap);
}
```

#### 3.六寸レイアウト写真を生成する

```java
/**
    * 六寸レイアウト写真を生成する /generate_layout_photos インターフェース
    * @param inputImageDir ファイルのパス
    * @return
    * @throws IOException
    */
public static String requestGenerateLayoutPhotos(String inputImageDir) throws IOException {
    String url = BASE_URL+"/generate_layout_photos";
    // ファイルオブジェクトを作成
    File inputFile = new File(inputImageDir);
    Map<String, Object> paramMap=new HashMap<>();
    paramMap.put("input_image",inputFile);
    paramMap.put("height","413");
    paramMap.put("width","295");
    paramMap.put("kb","200");
    // responseはjson形式の辞書で、statusとimage_base64を含みます
    return HttpUtil.post(url, paramMap);
}
```

#### 4.人物切り抜き

```java
/**
    * 人物切り抜き写真を生成する /human_matting インターフェース
    * @param inputImageDir ファイルのパス
    * @return
    * @throws IOException
    */
public static String requestHumanMattingPhotos(String inputImageDir) throws IOException {
    String url = BASE_URL+"/human_matting";
    // ファイルオブジェクトを作成
    File inputFile = new File(inputImageDir);
    Map<String, Object> paramMap=new HashMap<>();
    paramMap.put("input_image",inputFile);
    // status、image_base64を含みます
    return HttpUtil.post(url, paramMap);
}
```

<br>

## JavaScript リクエスト例

JavaScriptでは、`fetch` APIを使用してHTTPリクエストを送信できます。以下は、JavaScriptでこれらのAPIを呼び出す方法の例です。

### 1. 証明写真を生成する（透明な背景）

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

// サンプル呼び出し
generateIdPhoto("images/test0.jpg", 413, 295).then(response => {
    console.log(response);
});
```

### 2. 背景色を追加する

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

// サンプル呼び出し
addBackground("test.png", "638cce", 200).then(response => {
    console.log(response);
});
```

### 3. 六寸レイアウト写真を生成する

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

// サンプル呼び出し
generateLayoutPhotos("test.jpg", 413, 295, 200).then(response => {
    console.log(response);
});
```

### 4. 人物切り抜き

```javascript
async function uploadImage(inputImagePath) {
    const url = "http://127.0.0.1:8080/human_matting";
    const formData = new FormData();
    formData.append("input_image", new File([await fetch(inputImagePath).then(res => res.blob())], "test.jpg"));

    const response = await fetch(url, {
        method: 'POST',
        body: formData
    });

    const result = await response.json(); // 応答がJSON形式であると仮定
    console.log(result);
    return result;
}

// サンプル呼び出し
uploadImage("demo/images/test0.jpg").then(response => {
    console.log(response);
});
```