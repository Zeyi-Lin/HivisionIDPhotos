<div align="center">
<h1>HivisionIDPhoto</h1>

[English](README_EN.md) / [中文](README.md) / 日本語 / [한국어](README_KO.md)

[![GitHub](https://img.shields.io/static/v1?label=GitHub&message=GitHub&color=black)](https://github.com/xiaolin199912/HivisionIDPhotos)
[![SwanHub Demo](https://swanhub.co/git/repo/SwanHub%2FAuto-README/file/preview?ref=main&path=swanhub.svg)](https://swanhub.co/ZeYiLin/HivisionIDPhotos/demo)
[![zhihu](https://img.shields.io/static/v1?label=知乎&message=知乎&color=blue)](https://zhuanlan.zhihu.com/p/638254028)
[![Spaces](https://img.shields.io/badge/🤗-Open%20in%20Spaces-blue)](https://huggingface.co/spaces/TheEeeeLin/HivisionIDPhotos)

<a href="https://trendshift.io/repositories/11622" target="_blank"><img src="https://trendshift.io/api/badge/repositories/11622" alt="Zeyi-Lin%2FHivisionIDPhotos | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

<img src="assets/demoImage.png" width=900>
</div>

<br>

> **関連プロジェクト**：
>
> - [SwanLab](https://github.com/SwanHubX/SwanLab)：トレーニング画像マットモデル全体を分析および監視するために使用され、研究室の学生と協力して交流し、トレーニング効率を大幅に向上させました。

<br>

# 🤩 プロジェクトの更新

- オンラインデモ： [![SwanHub Demo](https://img.shields.io/static/v1?label=Demo&message=SwanHub%20Demo&color=blue)](https://swanhub.co/ZeYiLin/HivisionIDPhotos/demo)、[![Spaces](https://img.shields.io/badge/🤗-Open%20in%20Spaces-blue)](https://huggingface.co/spaces/TheEeeeLin/HivisionIDPhotos)

- 2024.9.2: **写真の KB サイズを調整して**を更新，[DockerHub](https://hub.docker.com/r/linzeyi/hivision_idphotos/tags)
- 2023.12.1: **API デプロイメント（fastapi ベース）**を更新
- 2023.6.20: **プリセットサイズメニュー**
- 2023.6.19: **レイアウト写真**を更新

# 概要

> 🚀 私たちの仕事に興味を持っていただきありがとうございます。画像処理分野での他の成果もご覧いただけます。お気軽に zeyi.lin@swanhub.co までご連絡ください。

HivisionIDPhoto は、実用的な証明写真のインテリジェント作成アルゴリズムを開発することを目的としています。

このアルゴリズムは、完全なモデルワークフローを使用して、さまざまなユーザーの写真シナリオを認識し、画像をセグメント化し、証明写真を生成します。

**HivisionIDPhoto は以下のことができます：**

1. 軽量な画像セグメンテーション (高速推論には CPU のみが必要です。)
2. 異なるサイズ仕様に基づいて標準的な証明写真や 6 インチのレイアウト写真を生成
3. 美顔機能（待機中）
4. インテリジェントなフォーマルウェアの交換（待機中）

<div align="center">
<img src="assets/gradio-image.jpeg" width=900>
</div>

---

HivisionIDPhoto が役に立つ場合は、このリポジトリにスターを付けるか、友人に推薦して、緊急の証明写真作成の問題を解決してください！

<br>

# 🔧 環境のインストールと依存関係

- Python >= 3.7（プロジェクトの主なテストは Python 3.10 で行われています）
- onnxruntime
- OpenCV
- オプション：Linux, Windows, MacOS

**1. プロジェクトをクローン**

```bash
git clone https://github.com/Zeyi-Lin/HivisionIDPhotos.git
cd  HivisionIDPhotos
```

**2. (大切です) 依存パッケージをインストール**

> conda を使用して Python 3.10 仮想環境を作成した後、次のコマンドを実行することがお勧めです。

```bash
pip install -r requirements.txt
pip install -r requirements-app.txt
```

**3. 重みファイルをダウンロード**

私たちの[Release](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/tag/pretrained-model)から重みファイル`hivision_modnet.onnx`（24.7MB）をダウンロードし、プロジェクトの`hivision/creator/weights`ディレクトリに保存してください。

<br>

# 🚀 Gradio デモの実行

```bash
python app.py
```

プログラムを実行すると、ローカルの Web ページが生成され、そのページで証明写真の操作と対話を完了できます。

<br>

# 🚀 Python 推論

## 1. 証明写真の作成

1 枚の写真を入力し、1 枚の標準証明写真と 1 枚の高解像度証明写真の 4 チャンネル透明 PNG を取得します。

```python
python inference.py -i demo/images/test.jpg -o ./idphoto.png --height 413 --width 295
```

## 2. 背景色の追加

1 枚の 4 チャンネル透明 PNG を入力し、背景色が追加された 1 枚の画像を取得します。

```python
python inference.py -t add_background -i ./idphoto.png -o ./idhoto_ab.jpg  -c 000000 -k 30
```

## 3. 六寸レイアウト写真の取得

1 枚の 3 チャンネル写真を入力し、1 枚の六寸レイアウト写真を取得します。

```python
python inference.py -t generate_layout_photos -i ./idhoto_ab.jpg -o ./idhoto_layout.jpg  --height 413 --width 295 -k 200
```

<br>

# ⚡️ API サービスのデプロイ

```
python deploy_api.py
```

**API サービスのリクエスト（Python）**

Python を使用してサービスにリクエストを送信します：

証明写真の作成（1 枚の写真を入力し、1 枚の標準証明写真と 1 枚の高解像度証明写真の 4 チャンネル透明 png を取得）：

```bash
python requests_api.py -u http://127.0.0.1:8080 -i images/test.jpg -o ./idphoto.png -s '(413,295)'
```

背景色を追加（1 枚の 4 チャンネル透明 png を入力し、背景色が追加された画像を取得）：

```bash
python requests_api.py -u http://127.0.0.1:8080 -t add_background -i ./idphoto.png -o ./idhoto_ab.jpg  -c '(0,0,0)' -k 30
```

6 インチのレイアウト写真を取得（3 チャンネルの写真を入力し、6 インチのレイアウト写真を取得）：

```bash
python requests_api.py -u http://127.0.0.1:8080 -t generate_layout_photos -i ./idhoto_ab.jpg -o ./idhoto_layout.jpg  -s '(413,295)' -k 200
```

<br>

## API サービスリクエスト - Python Request

### 1. 証明写真の作成

1枚の写真を入力し、1枚の標準証明写真と1枚の高解像度証明写真の4チャンネル透明PNGを取得します。

```bash
import requests

url = "http://127.0.0.1:8080/idphoto"
input_image_path = "demo/images/test.jpg"

files = {"input_image": open(input_image_path, "rb")}
data = {"height": 413, "width": 295}

response = requests.post(url, files=files, data=data).json()

# responseはstatus、image_base64_standard、image_base64_hdを含むJSON形式の辞書です。
print(response)

```

### 2. 背景色の追加

1枚の4チャンネル透明PNGを入力し、背景色が追加された1枚の画像を取得します。

```bash
import requests

url = "http://127.0.0.1:8080/add_background"
input_image_path = "test.png"

files = {"input_image": open(input_image_path, "rb")}
data = {"color": '638cce', 'kb': None}

response = requests.post(url, files=files, data=data).json()

# responseはstatusとimage_base64を含むJSON形式の辞書です。
print(response)
```

### 3. 6インチレイアウト写真の取得

1枚の3チャンネル写真を入力し、1枚の6インチレイアウト写真を取得します。

```bash
import requests

url = "http://127.0.0.1:8080/generate_layout_photos"
input_image_path = "test.jpg"

files = {"input_image": open(input_image_path, "rb")}
data = {"height": 413, "width": 295, "kb": 200}

response = requests.post(url, files=files, data=data).json()

# responseはstatusとimage_base64を含むJSON形式の辞書です。
print(response)
```

より多くのリクエスト方法については、[API ドキュメント](docs/api_EN.md)を参照してください。Python スクリプトリクエスト、Python Request リクエスト、Java リクエストが含まれています。

<br>

# 🐳 Docker デプロイ

## 1. イメージのプルまたはビルド

> 以下の方法から一つを選択してください

**方法一：イメージのプル：**

```bash
docker pull linzeyi/hivision_idphotos:v1
docker tag linzeyi/hivision_idphotos:v1 hivision_idphotos
```

**方法二：Dockerfile で直接イメージをビルド：**

モデルの重みファイル[hivision_modnet.onnx](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/tag/pretrained-model)を`hivision/creator/weights`ディレクトリに配置した後、プロジェクトのルートディレクトリで以下を実行します：

```bash
docker build -t hivision_idphotos .
```

**方法三：Docker compose でビルド：**

モデルの重みファイル [hivision_modnet.onnx](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/tag/pretrained-model) を`hivision/creator/weights`ディレクトリに配置した後、プロジェクトのルートディレクトリで以下を実行します：

```bash
docker compose build
```

イメージのパッケージングが完了したら、以下のコマンドを実行して Gradio サービスを起動します：

```bash
docker compose up -d
```

## 2. Gradio Demo の実行

イメージのパッケージングが完了したら、以下のコマンドを実行して Gradio Demo サービスを起動します：

```bash
docker run -p 7860:7860 hivision_idphotos
```

ローカルで [http://127.0.0.1:7860](http://127.0.0.1:7860/) にアクセスすると使用できます。

## 3. API バックエンドサービスの実行

```bash
docker run -p 8080:8080 hivision_idphotos python3 deploy_api.py
```

<br>

# 📖 参考プロジェクト

1. MTCNN:

```bibtex
@software{ipazc_mtcnn_2021,
    author = {ipazc},
    title = {{MTCNN}},
    url = {https://github.com/ipazc/mtcnn},
    year = {2021},
    publisher = {GitHub}
}
```

2. ModNet:

```bibtex
@software{zhkkke_modnet_2021,
    author = {ZHKKKe},
    title = {{ModNet}},
    url = {https://github.com/ZHKKKe/MODNet},
    year = {2021},
    publisher = {GitHub}
}
```

<br>

# 💻 開発のヒント

**1. デフォルトサイズを変更する方法**

[size_list_CN.csv](demo/size_list_CN.csv) を変更してから、app.py を再実行します。最初の列はサイズ名であり、2 番目の列は高さ、3 番目の列は幅です。

<br>

# 📧 お問い合わせ

ご質問がある場合は、zeyi.lin@swanhub.co までメールでお問い合わせください。

<br>

# 貢献者

<a href="https://github.com/Zeyi-Lin/HivisionIDPhotos/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Zeyi-Lin/HivisionIDPhotos" />
</a>

[Zeyi-Lin](https://github.com/Zeyi-Lin)、[SAKURA-CAT](https://github.com/SAKURA-CAT)、[Feudalman](https://github.com/Feudalman)、[swpfY](https://github.com/swpfY)、[Kaikaikaifang](https://github.com/Kaikaikaifang)、[ShaohonChen](https://github.com/ShaohonChen)、[KashiwaByte](https://github.com/KashiwaByte)

<br>

# StarHistory

[![Star History Chart](https://api.star-history.com/svg?repos=Zeyi-Lin/HivisionIDPhotos&type=Date)](https://star-history.com/#Zeyi-Lin/HivisionIDPhotos&Date)