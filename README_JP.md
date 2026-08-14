<div align="center">

<img alt="hivision_logo" src="assets/hivision_logo.png" width=120 height=120>
<h1>HivisionIDPhoto</h1>

[English](README_EN.md) / [中文](README.md) / 日本語 / [한국어](README_KO.md)

[![][release-shield]][release-link]
[![][dockerhub-shield]][dockerhub-link]
[![][github-stars-shield]][github-stars-link]
[![][github-issues-shield]][github-issues-link]
[![][github-contributors-shield]][github-contributors-link]
[![][github-forks-shield]][github-forks-link]
[![][license-shield]][license-link]  
[![][wechat-shield]][wechat-link]
[![][spaces-shield]][spaces-link]
[![][swanhub-demo-shield]][swanhub-demo-link]
[![][modelscope-shield]][modelscope-link]
[![][modelers-shield]][modelers-link]
[![][compshare-shield]][compshare-link]

[![][trendshift-shield]][trendshift-link]
[![][hellogithub-shield]][hellogithub-link]

<img src="assets/demoImage.jpg" width=900>

</div>

<br>

> **関連プロジェクト**：
>
> - [SwanLab](https://github.com/SwanHubX/SwanLab)：人物切り抜きモデルの訓練を通じて、分析と監視、ラボの仲間との協力と交流を行い、訓練効率を大幅に向上させました。

<br>

# 目次

- [最近の更新](#-最近の更新)
- [プロジェクト概要](#-プロジェクト概要)
- [コミュニティ](#-コミュニティ)
- [準備作業](#-準備作業)
- [デモの起動](#-デモの起動)
- [Python推論](#-python推論)
- [APIサービスのデプロイ](#️-APIサービスのデプロイ)
- [Dockerデプロイ](#-dockerデプロイ)
- [お問い合わせ](#-お問い合わせ)
- [貢献者](#貢献者)

<br>

# 🤩 最近の更新

- オンライン体験： [![SwanHub Demo](https://img.shields.io/static/v1?label=Demo&message=SwanHub%20Demo&color=blue)](https://swanhub.co/ZeYiLin/HivisionIDPhotos/demo)、[![Spaces](https://img.shields.io/badge/🤗-Open%20in%20Spaces-blue)](https://huggingface.co/spaces/TheEeeeLin/HivisionIDPhotos)、[![][modelscope-shield]][modelscope-link]、[![][compshare-shield]][compshare-link]

- 2024.11.20: Gradioデモに**印刷レイアウト**オプションを追加、六つ切り、五つ切り、A4、3R、4Rレイアウトサイズをサポート
- 2024.11.16: APIインターフェースに美顔効果パラメータを追加
- 2024.09.24: APIインターフェースにbase64画像入力オプションを追加 | Gradioデモに**レイアウト写真トリミングライン**機能を追加
- 2024.09.22: Gradioデモに**ビーストモード**と**DPI**パラメータを追加
- 2024.09.18: Gradioデモに**テンプレート写真の共有**機能を追加、**米国式**背景オプションを追加
- 2024.09.17: Gradioデモに**カスタム底色-HEX入力**機能を追加 | **（コミュニティ貢献）C++バージョン** - [HivisionIDPhotos-cpp](https://github.com/zjkhahah/HivisionIDPhotos-cpp) 貢献 by [zjkhahah](https://github.com/zjkhahah)
- 2024.09.16: Gradioデモに**顔回転対応**機能を追加、カスタムサイズ入力に**ミリメートル**をサポート

<br>

# プロジェクト概要

> 🚀 私たちの仕事に興味を持っていただきありがとうございます。画像分野における他の成果もぜひご覧ください。お問い合わせは、zeyi.lin@swanhub.co まで。

HivisionIDPhotoは、実用的で体系的な証明写真のスマート制作アルゴリズムを開発することを目的としています。

さまざまなユーザー撮影シーンの認識、切り抜きおよび証明写真の生成を実現するために、一連の洗練されたAIモデル作業フローを利用しています。

**HivisionIDPhotoは以下のことができます：**

1. 軽量切り抜き（完全オフラインで、**CPU**のみで迅速に推論可能）
2. 異なるサイズ仕様に基づいて異なる標準証明写真、六寸レイアウト写真を生成
3. 完全オフラインまたはエッジクラウド推論をサポート
4. 美顔（待機中）
5. スマートな正装変更（待機中）

<div align="center">
<img src="assets/demo.png" width=900>
</div>

---

HivisionIDPhotoがあなたに役立つ場合は、このリポジトリをスターしたり、友人に推薦したりして、証明写真の緊急制作の問題を解決してください！

<br>

# 🏠 コミュニティ

私たちは、コミュニティによって構築されたHivisionIDPhotosの興味深いアプリケーションや拡張機能をいくつか共有しています：

- [HivisionIDPhotos-ComfyUI](https://github.com/AIFSH/HivisionIDPhotos-ComfyUI)：ComfyUI証明写真処理ワークフロー、[AIFSH](https://github.com/AIFSH/HivisionIDPhotos-ComfyUI)によって構築 

[<img src="assets/comfyui.png" width="900" alt="ComfyUI workflow">](https://github.com/AIFSH/HivisionIDPhotos-ComfyUI)

- [HivisionIDPhotos-wechat-weapp](https://github.com/no1xuan/HivisionIDPhotos-wechat-weapp)：WeChat証明写真ミニプログラム、HivisionIDphotosアルゴリズムに基づく、[no1xuan](https://github.com/no1xuan)による貢献

[<img src="assets/community-wechat-miniprogram.png" width="900" alt="HivisionIDPhotos-wechat-weapp">](https://github.com/no1xuan/HivisionIDPhotos-wechat-weapp)

- [HivisionIDPhotos-Uniapp](https://github.com/soulerror/HivisionIDPhotos-Uniapp)：基本のuniapp証明写真ミニプログラムの前部、HivisionIDphotosアルゴリズムに基づく、[soulerror](https://github.com/soulerror)による貢献

[<img src="assets/community-uniapp-wechat-miniprogram.png" width="900" alt="HivisionIDPhotos-uniapp">](https://github.com/soulerror/HivisionIDPhotos-Uniapp)

- [HivisionIDPhotos-cpp](https://github.com/zjkhahah/HivisionIDPhotos-cpp)：HivisionIDphotos C++バージョン、[zjkhahah](https://github.com/zjkhahah)によって構築
- [HivisionIDPhotos-windows-GUI](https://github.com/zhaoyun0071/HivisionIDPhotos-windows-GUI)：Windowsクライアントアプリケーション、[zhaoyun0071](https://github.com/zhaoyun0071)によって構築
- [HivisionIDPhotos-NAS](https://github.com/ONG-Leo/HivisionIDPhotos-NAS)：Synology NAS導入の中国語チュートリアル、[ONG-Leo](https://github.com/ONG-Leo)による貢献

<br>

# 🔧 準備作業

環境のインストールと依存関係：
- Python >= 3.7（プロジェクトは主にpython 3.10でテストされています）
- OS: Linux, Windows, MacOS

## 1. プロジェクトをクローンする

```bash
git clone https://github.com/Zeyi-Lin/HivisionIDPhotos.git
cd  HivisionIDPhotos
```

## 2. 依存環境をインストールする

> condaでpython3.10の仮想環境を作成することをお勧めします。その後、以下のコマンドを実行してください。

```bash
pip install -r requirements.txt
pip install -r requirements-app.txt
```

## 3. 重みファイルをダウンロードする

**方法一：スクリプトでダウンロード**

```bash
python scripts/download_model.py --models all
```

**方法二：直接ダウンロード**

プロジェクトの`hivision/creator/weights`ディレクトリに保存します：
- `modnet_photographic_portrait_matting.onnx` (24.7MB): [MODNet](https://github.com/ZHKKKe/MODNet)公式の重み、[ダウンロード](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/download/pretrained-model/modnet_photographic_portrait_matting.onnx)
- `hivision_modnet.onnx` (24.7MB): 単色背景に対して適応性の高い切り抜きモデル、[ダウンロード](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/download/pretrained-model/hivision_modnet.onnx)
- `rmbg-1.4.onnx` (176.2MB): [BRIA AI](https://huggingface.co/briaai/RMBG-1.4)のオープンソース切り抜きモデル、[ダウンロード](https://huggingface.co/briaai/RMBG-1.4/resolve/main/onnx/model.onnx?download=true)後に`rmbg-1.4.onnx`にリネーム
- `birefnet-v1-lite.onnx`(224MB): [ZhengPeng7](https://github.com/ZhengPeng7/BiRefNet)のオープンソース切り抜きモデル、[ダウンロード](https://github.com/ZhengPeng7/BiRefNet/releases/download/v1/BiRefNet-general-bb_swin_v1_tiny-epoch_232.onnx)後に`birefnet-v1-lite.onnx`にリネーム

## 4. 顔検出モデルの設定（オプション）

| 拡張顔検出モデル | 説明 | 使用文書 |
| -- | -- | -- |
| MTCNN | **オフライン**顔検出モデル、高性能CPU推論、デフォルトモデル、検出精度は低い | このプロジェクトをクローン後、直接使用 |
| Face++ | Megviiが提供するオンライン顔検出API、高精度の検出、[公式文書](https://console.faceplusplus.com.cn/documents/4888373) | [使用文書](docs/face++_EN.md)|

## 5. パフォーマンスリファレンス

> テスト環境はMac M1 Max 64GB、非GPU加速、テスト画像の解像度は512x715(1)と764×1146(2)。

| モデルの組み合わせ | メモリ使用量 | 推論時間(1) | 推論時間(2) |
| -- | -- | -- | -- |
| MODNet + mtcnn | 410MB | 0.207秒 | 0.246秒 |
| MODNet + retinaface | 405MB | 0.571秒 | 0.971秒 |
| birefnet-v1-lite + retinaface | 6.20GB | 7.063秒 | 7.128秒 |

## 6. GPU推論の加速（オプション）

現在のバージョンでは、NVIDIA GPUで加速可能なモデルは`birefnet-v1-lite`です。約16GBのVRAMが必要であることにご注意ください。

NVIDIA GPUを使用して推論を加速したい場合は、CUDAとcuDNNがインストールされていることを確認した上で、[onnxruntime-gpuのドキュメント](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html#cuda-12x)に従って適切な`onnxruntime-gpu`バージョンをインストールし、[PyTorchの公式サイト](https://pytorch.org/get-started/locally/)から適切な`pytorch`バージョンをインストールしてください。

```bash
# もしコンピュータにCUDA 12.xとcuDNN 8がインストールされている場合
# torchのインストールは任意です。cuDNNが設定できない場合は、torchを試してみてください
pip install onnxruntime-gpu==1.18.0
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

インストールが完了したら、`birefnet-v1-lite`モデルを呼び出してGPU加速推論を利用します。

> TIPS: CUDAのインストールは下位互換性があります。たとえば、CUDAのバージョンが12.6で、torchが現在対応している最高バージョンが12.4である場合、コンピュータに12.4のバージョンをインストールすることも可能です。

<br>

# 🚀 デモの起動

```bash
python app.py
```

プログラムを実行すると、ローカルWebページが生成され、ページ内で証明写真の操作と対話が可能になります。

<img src="assets/harry.png" width=900>

<br>

# 🚀 Python推論

核心パラメータ：

- `-i`: 入力画像のパス
- `-o`: 保存画像のパス
- `-t`: 推論タイプ、idphoto、human_matting、add_background、generate_layout_photosから選択可能
- `--matting_model`: 人物切り抜きモデルの重み選択
- `--face_detect_model`: 顔検出モデルの選択

詳細なパラメータは`python inference.py --help`で確認できます。

## 1. 証明写真の作成

1枚の写真を入力し、1枚の標準証明写真と1枚の高解像度証明写真の4チャンネル透明PNGを取得します。

```python
python inference.py -i demo/images/test0.jpg -o ./idphoto.png --height 413 --width 295
```

## 2. 人物切り抜き

1枚の写真を入力し、1枚の4チャンネル透明PNGを取得します。

```python
python inference.py -t human_matting -i demo/images/test0.jpg -o ./idphoto_matting.png --matting_model hivision_modnet
```

## 3. 透明画像に背景色を追加

1枚の4チャンネル透明PNGを入力し、背景色を追加した3チャンネル画像を取得します。

```python
python inference.py -t add_background -i ./idphoto.png -o ./idphoto_ab.jpg -c 4f83ce -k 30 -r 1
```

## 4. 六寸レイアウト写真の取得

1枚の3チャンネル写真を入力し、1枚の六寸レイアウト写真を取得します。

```python
python inference.py -t generate_layout_photos -i ./idphoto_ab.jpg -o ./idphoto_layout.jpg --height 413 --width 295 -k 200
```

## 5. 証明写真のトリミング

1枚の4チャンネル写真（切り抜き済みの画像）を入力し、1枚の標準証明写真と1枚の高解像度証明写真の4チャンネル透明PNGを取得します。

```python
python inference.py -t idphoto_crop -i ./idphoto_matting.png -o ./idphoto_crop.png --height 413 --width 295
```

<br>

# ⚡️ APIサービスのデプロイ

## バックエンドを起動

```
python deploy_api.py
```

## APIサービスにリクエスト

詳細なリクエスト方法は[APIドキュメント](docs/api_EN.md)を参照してください。以下のリクエスト例が含まれます：
- [cURL](docs/api_EN.md#curl-request-examples)
- [Python](docs/api_EN.md#python-request-example)

<br>

# 🐳 Dockerデプロイ

## 1. イメージをプルまたはビルドする

> 以下の方法から3つを選択してください。

**方法一：最新のイメージをプル：**

```bash
docker pull linzeyi/hivision_idphotos
```

**方法二：Dockerfileから直接イメージをビルド：**

`hivision/creator/weights` ディレクトリに少なくとも1つの[マスキングモデルの重みファイル](#3-重みファイルのダウンロード)があることを確認してから、プロジェクトのルートディレクトリで以下を実行してください：

```bash
docker build -t linzeyi/hivision_idphotos .
```

**方法三：Docker composeでビルド：**

`hivision/creator/weights` ディレクトリに少なくとも1つの[マスキングモデルの重みファイル](#3-重みファイルのダウンロード)があることを確認してから、プロジェクトのルートディレクトリで以下を実行してください：

```bash
docker compose build
```

## 2. サービスを実行

**Gradioデモサービスを起動**

次のコマンドを実行し、ローカルで [http://127.0.0.1:7860](http://127.0.0.1:7860/) にアクセスすると使用可能です。

```bash
docker run -d -p 7860:7860 linzeyi/hivision_idphotos
```

**APIバックエンドサービスを起動**

```bash
docker run -d -p 8080:8080 linzeyi/hivision_idphotos python3 deploy_api.py
```

**2つのサービスを同時に起動**

```bash
docker compose up -d
```

## 環境変数

本プロジェクトは、いくつかの追加設定項目を提供し、環境変数を使用して設定します：

| 環境変数 | タイプ	| 説明 | 例 |
|--|--|--|--|
| FACE_PLUS_API_KEY	 | オプション	| これはFace++コンソールで申請したAPIキーです。	 | `7-fZStDJ····` |
| FACE_PLUS_API_SECRET	 | オプション	| Face++ APIキーに対応するSecret | `VTee824E····` |

dockerでの環境変数使用例：
```bash
docker run  -d -p 7860:7860 \
    -e FACE_PLUS_API_KEY=7-fZStDJ···· \
    -e FACE_PLUS_API_SECRET=VTee824E···· \
    linzeyi/hivision_idphotos 
```

<br>

# 📖 プロジェクトの引用

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

# よくある質問 (FAQ)

## 1. 基本的なサイズと色をどのように変更しますか？

- サイズ: [size_list_EN.csv](demo/assets/size_list_EN.csv) ファイルを修正した後、`app.py`を再実行すれば大丈夫です。最初の列はサイズ名、二番目の列は高さ、三番目の列は幅です。
- 色: [color_list_EN.csv](demo/assets/color_list_EN.csv) ファイルを修正した後、`app.py`を再実行すれば大丈夫です。最初の列は色名、二番目の列はHex値です。

## 2. ウォーターマークのフォントをどのように変更しますか？

1. フォントファイルを`hivision/plugin/font`フォルダーに置きます。
2. `hivision/plugin/watermark.py`ファイル内の`font_file`パラメータの値をフォントファイル名に変更します。

## 3. ソーシャルメディアのテンプレート画像をどのように追加しますか？

1. テンプレート画像を`hivision/plugin/template/assets`フォルダーに置きます。テンプレート画像は4チャンネルの透明PNGです。
2. `hivision/plugin/template/assets/template_config.json`ファイルに最新のテンプレート情報を追加します。ここで`width`はテンプレート画像の幅(px)、`height`はテンプレート画像の高さ(px)、`anchor_points`はテンプレートの透明領域の4つの隅の座標(px)です。`rotation`は透明領域の垂直方向に対する回転角度で、>0は反時計回り、<0は時計回りです。
3. `demo/processor.py`の`_generate_image_template`関数内の`TEMPLATE_NAME_LIST`変数に最新のテンプレート名を追加します。

<img src="assets/social_template.png" width="500">

## 4. Gradio Demoの上部ナビゲーションバーをどのように変更しますか？

- `demo/assets/title.md`ファイルを修正します。

<br>

# 📧 お問い合わせ

ご不明な点がございましたら、zeyi.lin@swanhub.coまでメールをお送りください。

<br>

# 貢献者

<a href="https://github.com/Zeyi-Lin/HivisionIDPhotos/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Zeyi-Lin/HivisionIDPhotos" />
</a>

[Zeyi-Lin](https://github.com/Zeyi-Lin)、[SAKURA-CAT](https://github.com/SAKURA-CAT)、[Feudalman](https://github.com/Feudalman)、[swpfY](https://github.com/swpfY)、[Kaikaikaifang](https://github.com/Kaikaikaifang)、[ShaohonChen](https://github.com/ShaohonChen)、[KashiwaByte](https://github.com/KashiwaByte)

<br>

# Thanks for support

[![Stargazers repo roster for @Zeyi-Lin/HivisionIDPhotos](https://reporoster.com/stars/Zeyi-Lin/HivisionIDPhotos)](https://github.com/Zeyi-Lin/HivisionIDPhotos/stargazers)

[![Forkers repo roster for @Zeyi-Lin/HivisionIDPhotos](https://reporoster.com/forks/Zeyi-Lin/HivisionIDPhotos)](https://github.com/Zeyi-Lin/HivisionIDPhotos/network/members)

[![Star History Chart](https://star-history.dera.page/svg?repos=Zeyi-Lin/HivisionIDPhotos&type=date)](https://star-history.dera.page/#Zeyi-Lin/HivisionIDPhotos&type=date)

<br>

# Lincese

This repository is licensed under the [Apache-2.0 License](LICENSE).

[github-stars-shield]: https://img.shields.io/github/stars/zeyi-lin/hivisionidphotos?color=ffcb47&labelColor=black&style=flat-square
[github-stars-link]: https://github.com/zeyi-lin/hivisionidphotos/stargazers

[swanhub-demo-shield]: https://swanhub.co/git/repo/SwanHub%2FAuto-README/file/preview?ref=main&path=swanhub.svg
[swanhub-demo-link]: https://swanhub.co/ZeYiLin/HivisionIDPhotos/demo

[spaces-shield]: https://img.shields.io/badge/🤗-Open%20in%20Spaces-blue
[spaces-link]: https://huggingface.co/spaces/TheEeeeLin/HivisionIDPhotos

<!-- 微信群链接 -->
[wechat-shield]: https://img.shields.io/badge/WeChat-微信-4cb55e
[wechat-link]: https://docs.qq.com/doc/DUkpBdk90eWZFS2JW

<!-- Github Release -->
[release-shield]: https://img.shields.io/github/v/release/zeyi-lin/hivisionidphotos?color=369eff&labelColor=black&logo=github&style=flat-square
[release-link]: https://github.com/zeyi-lin/hivisionidphotos/releases

[license-shield]: https://img.shields.io/badge/license-apache%202.0-white?labelColor=black&style=flat-square
[license-link]: https://github.com/Zeyi-Lin/HivisionIDPhotos/blob/master/LICENSE

[github-issues-shield]: https://img.shields.io/github/issues/zeyi-lin/hivisionidphotos?color=ff80eb&labelColor=black&style=flat-square
[github-issues-link]: https://github.com/zeyi-lin/hivisionidphotos/issues

[dockerhub-shield]: https://img.shields.io/docker/v/linzeyi/hivision_idphotos?color=369eff&label=docker&labelColor=black&logoColor=white&style=flat-square
[dockerhub-link]: https://hub.docker.com/r/linzeyi/hivision_idphotos/tags

[trendshift-shield]: https://trendshift.io/api/badge/repositories/11622
[trendshift-link]: https://trendshift.io/repositories/11622

[hellogithub-shield]: https://abroad.hellogithub.com/v1/widgets/recommend.svg?rid=8ea1457289fb4062ba661e5299e733d6&claim_uid=Oh5UaGjfrblg0yZ
[hellogithub-link]: https://hellogithub.com/repository/8ea1457289fb4062ba661e5299e733d6

[github-contributors-shield]: https://img.shields.io/github/contributors/zeyi-lin/hivisionidphotos?color=c4f042&labelColor=black&style=flat-square
[github-contributors-link]: https://github.com/zeyi-lin/hivisionidphotos/graphs/contributors

[github-forks-shield]: https://img.shields.io/github/forks/zeyi-lin/hivisionidphotos?color=8ae8ff&labelColor=black&style=flat-square
[github-forks-link]: https://github.com/zeyi-lin/hivisionidphotos/network/members

[modelscope-shield]: https://img.shields.io/badge/Demo_on_ModelScope-purple?logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjIzIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KCiA8Zz4KICA8dGl0bGU+TGF5ZXIgMTwvdGl0bGU+CiAgPHBhdGggaWQ9InN2Z18xNCIgZmlsbD0iIzYyNGFmZiIgZD0ibTAsODkuODRsMjUuNjUsMGwwLDI1LjY0OTk5bC0yNS42NSwwbDAsLTI1LjY0OTk5eiIvPgogIDxwYXRoIGlkPSJzdmdfMTUiIGZpbGw9IiM2MjRhZmYiIGQ9Im05OS4xNCwxMTUuNDlsMjUuNjUsMGwwLDI1LjY1bC0yNS42NSwwbDAsLTI1LjY1eiIvPgogIDxwYXRoIGlkPSJzdmdfMTYiIGZpbGw9IiM2MjRhZmYiIGQ9Im0xNzYuMDksMTQxLjE0bC0yNS42NDk5OSwwbDAsMjIuMTlsNDcuODQsMGwwLC00Ny44NGwtMjIuMTksMGwwLDI1LjY1eiIvPgogIDxwYXRoIGlkPSJzdmdfMTciIGZpbGw9IiMzNmNmZDEiIGQ9Im0xMjQuNzksODkuODRsMjUuNjUsMGwwLDI1LjY0OTk5bC0yNS42NSwwbDAsLTI1LjY0OTk5eiIvPgogIDxwYXRoIGlkPSJzdmdfMTgiIGZpbGw9IiMzNmNmZDEiIGQ9Im0wLDY0LjE5bDI1LjY1LDBsMCwyNS42NWwtMjUuNjUsMGwwLC0yNS42NXoiLz4KICA8cGF0aCBpZD0ic3ZnXzE5IiBmaWxsPSIjNjI0YWZmIiBkPSJtMTk4LjI4LDg5Ljg0bDI1LjY0OTk5LDBsMCwyNS42NDk5OWwtMjUuNjQ5OTksMGwwLC0yNS42NDk5OXoiLz4KICA8cGF0aCBpZD0ic3ZnXzIwIiBmaWxsPSIjMzZjZmQxIiBkPSJtMTk4LjI4LDY0LjE5bDI1LjY0OTk5LDBsMCwyNS42NWwtMjUuNjQ5OTksMGwwLC0yNS42NXoiLz4KICA8cGF0aCBpZD0ic3ZnXzIxIiBmaWxsPSIjNjI0YWZmIiBkPSJtMTUwLjQ0LDQybDAsMjIuMTlsMjUuNjQ5OTksMGwwLDI1LjY1bDIyLjE5LDBsMCwtNDcuODRsLTQ3Ljg0LDB6Ii8+CiAgPHBhdGggaWQ9InN2Z18yMiIgZmlsbD0iIzM2Y2ZkMSIgZD0ibTczLjQ5LDg5Ljg0bDI1LjY1LDBsMCwyNS42NDk5OWwtMjUuNjUsMGwwLC0yNS42NDk5OXoiLz4KICA8cGF0aCBpZD0ic3ZnXzIzIiBmaWxsPSIjNjI0YWZmIiBkPSJtNDcuODQsNjQuMTlsMjUuNjUsMGwwLC0yMi4xOWwtNDcuODQsMGwwLDQ3Ljg0bDIyLjE5LDBsMCwtMjUuNjV6Ii8+CiAgPHBhdGggaWQ9InN2Z18yNCIgZmlsbD0iIzYyNGFmZiIgZD0ibTQ3Ljg0LDExNS40OWwtMjIuMTksMGwwLDQ3Ljg0bDQ3Ljg0LDBsMCwtMjIuMTlsLTI1LjY1LDBsMCwtMjUuNjV6Ii8+CiA8L2c+Cjwvc3ZnPg==&labelColor=white
[modelscope-link]: https://modelscope.cn/studios/SwanLab/HivisionIDPhotos

[modelers-shield]: https://img.shields.io/badge/Demo_on_Modelers-c42a2a?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMjQiIGhlaWdodD0iNjQiIHZpZXdCb3g9IjAgMCAxMjQgNjQiIGZpbGw9Im5vbmUiPgo8cGF0aCBkPSJNNDIuNzc4MyAwSDI2LjU5NzdWMTUuNzc4N0g0Mi43NzgzVjBaIiBmaWxsPSIjREUwNDI5Ii8+CjxwYXRoIGQ9Ik0xNi41MDg4IDQuMTc5MkgwLjMyODEyNVYxOS45NTc5SDE2LjUwODhWNC4xNzkyWiIgZmlsbD0iIzI0NDk5QyIvPgo8cGF0aCBkPSJNMTIzLjk1MiA0LjE3OTJIMTA3Ljc3MVYxOS45NTc5SDEyMy45NTJWNC4xNzkyWiIgZmlsbD0iIzI0NDk5QyIvPgo8cGF0aCBkPSJNMTYuNTA4OCA0NS40NjE5SDAuMzI4MTI1VjYxLjI0MDZIMTYuNTA4OFY0NS40NjE5WiIgZmlsbD0iIzI0NDk5QyIvPgo8cGF0aCBkPSJNMTIzLjk1MiA0NS40NjE5SDEwNy43NzFWNjEuMjQwNkgxMjMuOTUyVjQ1LjQ2MTlaIiBmaWxsPSIjMjQ0OTlDIi8+CjxwYXRoIGQ9Ik0zMi43MDggMTUuNzc4OEgxNi41MjczVjMxLjU1NzVIMzIuNzA4VjE1Ljc3ODhaIiBmaWxsPSIjREUwNDI5Ii8+CjxwYXRoIGQ9Ik01Mi44NDg2IDE1Ljc3ODhIMzYuNjY4VjMxLjU1NzVINTIuODQ4NlYxNS43Nzg4WiIgZmlsbD0iI0RFMDQyOSIvPgo8cGF0aCBkPSJNOTcuNzIzNyAwSDgxLjU0M1YxNS43Nzg3SDk3LjcyMzdWMFoiIGZpbGw9IiNERTA0MjkiLz4KPHBhdGggZD0iTTg3LjY1MzQgMTUuNzc4OEg3MS40NzI3VjMxLjU1NzVIODcuNjUzNFYxNS43Nzg4WiIgZmlsbD0iI0RFMDQyOSIvPgo8cGF0aCBkPSJNMTA3Ljc5NCAxNS43Nzg4SDkxLjYxMzNWMzEuNTU3NUgxMDcuNzk0VjE1Ljc3ODhaIiBmaWxsPSIjREUwNDI5Ii8+CjxwYXRoIGQ9Ik0yNC42NzQ4IDMxLjU1NzZIOC40OTQxNFY0Ny4zMzYzSDI0LjY3NDhWMzEuNTU3NloiIGZpbGw9IiNERTA0MjkiLz4KPHBhdGggZD0iTTYwLjg3OTkgMzEuNTU3Nkg0NC42OTkyVjQ3LjMzNjNINjAuODc5OVYzMS41NTc2WiIgZmlsbD0iI0RFMDQyOSIvPgo8cGF0aCBkPSJNNzkuNjIwMSAzMS41NTc2SDYzLjQzOTVWNDcuMzM2M0g3OS42MjAxVjMxLjU1NzZaIiBmaWxsPSIjREUwNDI5Ii8+CjxwYXRoIGQ9Ik0xMTUuODI1IDMxLjU1NzZIOTkuNjQ0NVY0Ny4zMzYzSDExNS44MjVWMzEuNTU3NloiIGZpbGw9IiNERTA0MjkiLz4KPHBhdGggZD0iTTcwLjI1NDkgNDcuMzM1OUg1NC4wNzQyVjYzLjExNDdINzAuMjU0OVY0Ny4zMzU5WiIgZmlsbD0iI0RFMDQyOSIvPgo8L3N2Zz4=&labelColor=white
[modelers-link]: https://modelers.cn/spaces/SwanLab/HivisionIDPhotos

[compshare-shield]: https://www-s.ucloud.cn/2025/02/dbef8b07ea3d316006d9c22765c3cd53_1740104342584.svg
[compshare-link]: https://www.compshare.cn/images-detail?ImageID=compshareImage-17jacgm4ju16&ytag=HG_GPU_HivisionIDPhotos