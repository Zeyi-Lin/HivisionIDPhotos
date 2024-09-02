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

- オンラインデモ: [![SwanHub Demo](https://img.shields.io/static/v1?label=Demo&message=SwanHub%20Demo&color=blue)](https://swanhub.co/ZeYiLin/HivisionIDPhotos/demo)
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

> 🚀 私たちの仕事に興味を持っていただきありがとうございます。画像処理分野での他の成果もご覧いただけます。お気軽にzeyi.lin@swanhub.coまでご連絡ください。

HivisionIDPhoto は、実用的な証明写真のインテリジェント作成アルゴリズムを開発することを目的としています。

このアルゴリズムは、完全なモデルワークフローを使用して、さまざまなユーザーの写真シナリオを認識し、画像をセグメント化し、証明写真を生成します。

**HivisionIDPhoto は以下のことができます:**

1. 軽量な画像セグメンテーション
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
- オプション: Linux, Windows, MacOS

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

# Gradio デモの実行

```bash
python app.py
```

プログラムを実行すると、ローカルの Web ページが生成され、そのページで証明写真の操作と対話を完了できます。

<br>

# API サービスのデプロイ

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
python requests_api.py -u http://127.0.0.1:8080 -t generate_layout_photos -i ./idhoto_ab.jpg -o ./idhoto_layout.jpg  -s '(413,295)' -k 30
```

<br>

# 🐳Docker デプロイ

モデルの重みファイル[hivision_modnet.onnx](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/tag/pretrained-model)をルートディレクトリに配置したことを確認した後、ルートディレクトリで次のコマンドを実行します：

```bash
docker build -t hivision_idphotos .
```

イメージのパッケージ化が完了したら、次のコマンドを実行して API サービスを開始します：

```bash
docker run -p 8080:8080 hivision_idphotos
```

<br>

# 参考プロジェクト

1. MTCNN: https://github.com/ipazc/mtcnn
2. ModNet: https://github.com/ZHKKKe/MODNet

<br>

# 📧 お問い合わせ

ご質問がある場合は、zeyi.lin@swanhub.coまでメールでお問い合わせください。

# 貢献者

[Zeyi-Lin](https://github.com/Zeyi-Lin)、[SAKURA-CAT](https://github.com/SAKURA-CAT)、[Feudalman](https://github.com/Feudalman)、[swpfY](https://github.com/swpfY)、[Kaikaikaifang](https://github.com/Kaikaikaifang)、[ShaohonChen](https://github.com/ShaohonChen)、[KashiwaByte](https://github.com/KashiwaByte)
