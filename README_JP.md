<div align="center">
<h1>HivisionIDPhoto</h1>

[English](README_EN.md) / [中文](README.md) / 日本語

[![GitHub](https://img.shields.io/static/v1?label=GitHub&message=GitHub&color=black)](https://github.com/xiaolin199912/HivisionIDPhotos)
[![SwanHub Demo](https://swanhub.co/git/repo/SwanHub%2FAuto-README/file/preview?ref=main&path=swanhub.svg)](https://swanhub.co/ZeYiLin/HivisionIDPhotos/demo)
[![zhihu](https://img.shields.io/static/v1?label=知乎&message=知乎&color=blue)](https://zhuanlan.zhihu.com/p/638254028)
[![Spaces](https://img.shields.io/badge/🤗-Open%20in%20Spaces-blue)](https://huggingface.co/spaces/TheEeeeLin/HivisionIDPhotos)

<img src="assets/demoImage.png" width=900>
</div>

<br>

> **関連プロジェクト**：
>
> - [SwanLab](https://github.com/SwanHubX/SwanLab)：トレーニング画像マットモデル全体を分析および監視するために使用され、研究室の学生と協力して交流し、トレーニング効率を大幅に向上させました。

<br>

# 🤩 プロジェクトの更新

- オンラインデモ： [![SwanHub Demo](https://img.shields.io/static/v1?label=Demo&message=SwanHub%20Demo&color=blue)](https://swanhub.co/ZeYiLin/HivisionIDPhotos/demo)、[![Spaces](https://img.shields.io/badge/🤗-Open%20in%20Spaces-blue)](https://huggingface.co/spaces/TheEeeeLin/HivisionIDPhotos)

- 2024.9.2: **写真の KB サイズを調整して**を更新
- 2023.12.1: **API デプロイメント（fastapi ベース）**を更新
- 2023.6.20: **プリセットサイズメニュー**
- 2023.6.19: **レイアウト写真**を更新
- 2023.6.13: **センターグラデーションカラー**を更新
- 2023.6.11: **上下グラデーションカラー**を更新
- 2023.6.8: **カスタムサイズ**を更新
- 2023.6.4: **カスタム背景色、顔検出バグ通知**を更新
- 2023.5.10: **サイズを変更せずに背景を変更**を更新

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

**2. 依存パッケージをインストール**

```bash
pip install -r requirements.txt
```

**3. 重みファイルをダウンロード**

[Release](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/tag/pretrained-model)から重みファイル`hivision_modnet.onnx`をダウンロードし、ルートディレクトリに保存します。

<br>

# 🚀 Gradio デモの実行

```bash
python app.py
```

プログラムを実行すると、ローカルの Web ページが生成され、そのページで証明写真の操作と対話を完了できます。

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

＃🐳 Docker デプロイメント

## 1. イメージの取得またはビルド

**イメージの取得：**

> このイメージは ARM アーキテクチャマシン（例：Mac M1）で構築されており、x86 アーキテクチャマシンを使用する場合は Dockerfile を使用してください。

```bash
docker pull linzeyi/hivision_idphotos:v1
```

**Dockrfile によるイメージの構築：**

[hivision_modnet.onnx](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/tag/pretrained-model)というモデルの重みファイルがルートディレクトリに配置されていることを確認した後、次のコマンドを実行します。

```bash
docker build -t hivision_idphotos .
```

## 2. Gradio Demo の実行

画像パッケージングが完了したら、次のコマンドを実行して Gradio Demo サービスを開始します。

```bash

docker run -p 7860:7860 hivision_idphotos

```

[http://127.0.0.1:7860](http://127.0.0.1:7860/)でローカルからアクセスできます。

## 3.API バックエンドサービスの実行

```bash

docker run -p 8080:8080 hivision_idphotos python3 deploy_api.py

```

<br>

# 📖 参考プロジェクト

1. MTCNN: https://github.com/ipazc/mtcnn
2. ModNet: https://github.com/ZHKKKe/MODNet

<br>

# 💻 開発のヒント

**1. デフォルトサイズを変更する方法**

[size_list_CN.csv](size_list_CN.csv) を変更してから、app.py を再実行します。最初の列はサイズ名であり、2 番目の列は高さ、3 番目の列は幅です。

<br>

# 📧 お問い合わせ

ご質問がある場合は、zeyi.lin@swanhub.co までメールでお問い合わせください。

# 貢献者

[Zeyi-Lin](https://github.com/Zeyi-Lin)、[SAKURA-CAT](https://github.com/SAKURA-CAT)、[Feudalman](https://github.com/Feudalman)、[swpfY](https://github.com/swpfY)、[Kaikaikaifang](https://github.com/Kaikaikaifang)、[ShaohonChen](https://github.com/ShaohonChen)、[KashiwaByte](https://github.com/KashiwaByte)
