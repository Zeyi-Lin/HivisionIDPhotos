<div align="center">

<img alt="hivision_logo" src="assets/hivision_logo.png" width=120 height=120>
<h1>HivisionIDPhoto</h1>

[English](README_EN.md) / [中文](README.md) / [日本語](README_JP.md) / [한국어](README_KO.md)

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

[![][trendshift-shield]][trendshift-link]

<img src="assets/demoImage.png" width=900>

</div>

<br>

> **관련 프로젝트**：
>
> - [SwanLab](https://github.com/SwanHubX/SwanLab)：인물 사진 모델 훈련 전 과정에서 분석하고 모니터링하며 실험실 동료들과 협력하여 훈련 효율성을 크게 향상시킴.

<br>

# 목차

- [프로젝트 업데이트](#-프로젝트-업데이트)
- [개요](#overview)
- [준비 작업](#-준비-작업)
- [데모 시작](#-구동-gradio-demo)
- [Python 추론](#-python-추론)
- [API 서비스 배포](#️-배포-api-서비스)
- [Docker 배포](#-docker-배포)
- [링크](#-링크)
- [연락처](#-연락처)
- [기여자](#기여자)

<br>

# 🤩 프로젝트 업데이트

- 온라인 체험: [![SwanHub Demo](https://img.shields.io/static/v1?label=Demo&message=SwanHub%20Demo&color=blue)](https://swanhub.co/ZeYiLin/HivisionIDPhotos/demo)、[![Spaces](https://img.shields.io/badge/🤗-Open%20in%20Spaces-blue)](https://huggingface.co/spaces/TheEeeeLin/HivisionIDPhotos)

- 2024.09.08: 새로운 배경 제거 모델 [RMBG-1.4](https://huggingface.co/briaai/RMBG-1.4)가 추가되었습니다 | ComfyUI 워크플로우 - [HivisionIDPhotos-ComfyUI](https://github.com/AIFSH/HivisionIDPhotos-ComfyUI)는 [AIFSH](https://github.com/AIFSH/HivisionIDPhotos-ComfyUI)에 의해 제공되었습니다.
- 2024.09.07: **얼굴 인식 API 옵션** [Face++](docs/face++_EN.md) 추가, 더 높은 정확도의 얼굴 인식 구현
- 2024.09.06: 새로운 배경 제거 모델 [modnet_photographic_portrait_matting.onnx](https://github.com/ZHKKKe/MODNet) 추가
- 2024.09.05: [Restful API 문서](docs/api_EN.md) 업데이트
- 2024.09.02: **사진 KB 크기 조정** 업데이트, [DockerHub](https://hub.docker.com/r/linzeyi/hivision_idphotos/tags)
- 2023.12.01: **API 배포(기반 fastapi)** 업데이트
- 2023.06.20: **프리셋 사이즈 메뉴** 업데이트

# 개요

> 🚀 우리의 작업에 관심을 가져 주셔서 감사합니다. 이미지 분야의 다른 성과도 확인해 보시기 바랍니다. 문의는 zeyi.lin@swanhub.co로 해주세요.

HivisionIDPhoto는 실용적이고 시스템적인 증명사진 제작 알고리즘을 개발하는 것을 목표로 합니다.

다양한 사용자 촬영 시나리오를 인식하고 배경 제거 및 증명사진 생성을 구현하기 위해 완전한 AI 모델 워크플로우를 활용합니다.

**HivisionIDPhoto는 다음과 같은 기능을 제공합니다:**

1. 경량 배경 제거(순수 오프라인, **CPU**만으로 빠른 추론 가능)
2. 다양한 크기 규격에 따라 다양한 표준 증명사진 및 6인치 배치 사진 생성
3. 순수 오프라인 또는 클라우드 추론 지원
4. 미용(대기 중)
5. 스마트 정장 교체(대기 중)

<div align="center">
<img src="assets/harry.png" width=900>
</div>

---

HivisionIDPhoto가 도움이 되었다면, 이 레포지토리를 스타하거나 친구에게 추천하여 증명사진 긴급 제작 문제를 해결해 주세요!

<br>

# 🔧 준비 작업

환경 설치 및 의존성:
- Python >= 3.7(주로 Python 3.10에서 테스트됨)
- OS: Linux, Windows, MacOS

## 1. 프로젝트 클론

```bash
git clone https://github.com/Zeyi-Lin/HivisionIDPhotos.git
cd HivisionIDPhotos
```

## 2. 의존성 환경 설치

> conda로 python3.10 가상 환경을 생성한 후, 다음 명령을 실행하는 것을 권장합니다.

```bash
pip install -r requirements.txt
pip install -r requirements-app.txt
```

## 3. 가중치 파일 다운로드

**방법 1: 스크립트 다운로드**

```bash
python scripts/download_model.py --models all
```

**방법 2: 직접 다운로드**

프로젝트의 `hivision/creator/weights` 디렉토리에 저장:
- `modnet_photographic_portrait_matting.onnx` (24.7MB): [MODNet](https://github.com/ZHKKKe/MODNet) 공식 가중치, [다운로드](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/download/pretrained-model/modnet_photographic_portrait_matting.onnx)
- `hivision_modnet.onnx` (24.7MB): 단색 배경 교체에 더 적합한 배경 제거 모델, [다운로드](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/download/pretrained-model/hivision_modnet.onnx)
- `mnn_hivision_modnet.mnn` (24.7MB): mnn 변환된 배경 제거 모델 by [zjkhahah](https://github.com/zjkhahah), [다운로드](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/download/pretrained-model/mnn_hivision_modnet.mnn)
- `rmbg-1.4.onnx` (176.2MB): [BRIA AI](https://huggingface.co/briaai/RMBG-1.4)에서 제공하는 오픈 소스 매트팅 모델입니다. [다운로드](https://huggingface.co/briaai/RMBG-1.4/resolve/main/onnx/model.onnx?download=true) 후 `rmbg-1.4.onnx`로 이름을 변경해 주세요.

## 4. 얼굴 인식 모델 설정

> 선택 사항입니다.

| 확장 얼굴 인식 모델 | 설명 | 사용 문서 |
| -- | -- | -- |
| MTCNN | **오프라인** 얼굴 인식 모델, 높은 성능의 CPU 추론, 기본 모델로, 정확도가 낮음 | 이 프로젝트를 클론한 후 직접 사용 |
| Face++ | 메가페이스에서 제공하는 온라인 얼굴 인식 API, 높은 정확도, [공식 문서](https://console.faceplusplus.com.cn/documents/4888373) | [사용 문서](docs/face++_EN.md)|

<br>

# 🚀 구동 Gradio Demo

```bash
python app.py
```

프로그램을 실행하면 로컬 웹 페이지가 생성되며, 페이지에서 증명사진 작업 및 상호작용을 수행할 수 있습니다.

<br>

# 🚀 Python 추론

핵심 파라미터:

- `-i`: 입력 이미지 경로
- `-o`: 저장 이미지 경로
- `-t`: 추론 유형, idphoto, human_matting, add_background, generate_layout_photos 중 선택
- `--matting_model`: 인물 배경 제거 모델 가중치 선택, `hivision_modnet`, `modnet_photographic_portrait_matting` 중 선택 가능

더 많은 파라미터는 `python inference.py --help`를 통해 확인할 수 있습니다.

## 1. 증명사진 제작

1장의 사진을 입력하여 1장의 표준 증명사진과 1장의 고화질 증명사진의 4채널 투명 png를 얻습니다.

```python
python inference.py -i demo/images/test.jpg -o ./idphoto.png --height 413 --width 295
```

## 2. 인물 배경 제거

```python
python inference.py -t human_matting -i demo/images/test.jpg -o ./idphoto_matting.png --matting_model hivision_modnet
```

## 3. 투명 이미지에 배경색 추가

1장의 4채널 투명 png를 입력하여 1장의 배경색이 추가된 이미지를 얻습니다.

```python
python inference.py -t add_background -i ./idphoto.png -o ./idhoto_ab.jpg -c 4f83ce -k 30 -r 1
```

## 4. 6인치 배치 사진 얻기

1장의 3채널 사진을 입력하여 1장의 6인치 배치 사진을 얻습니다.

```python
python inference.py -t generate_layout_photos -i ./idhoto_ab.jpg -o ./idhoto_layout.jpg --height 413 --width 295 -k 200
```

<br>

# ⚡️ API 서비스 배포

## 백엔드 시작

```
python deploy_api.py
```

## API 서비스 요청 - Python Request

> 요청 방법은 [API 문서](docs/api_EN.md)를 참조해 주세요. 여기에는 [cURL](docs/api_EN.md#curl-request-examples)、[Python](docs/api_EN.md#python-request-example)、[Java](docs/api_EN.md#java-request-example)、[Javascript](docs/api_EN.md#javascript-request-examples) 요청 예시가 포함됩니다.

### 1. 증명사진 제작

1장의 사진을 입력하여 1장의 표준 증명사진과 1장의 고화질 증명사진의 4채널 투명 png를 얻습니다.

```python
import requests

url = "http://127.0.0.1:8080/idphoto"
input_image_path = "demo/images/test.jpg"

files = {"input_image": open(input_image_path, "rb")}
data = {"height": 413, "width": 295}

response = requests.post(url, files=files, data=data).json()

# response는 status, image_base64_standard, image_base64_hd 세 가지 항목을 포함하는 json 형식의 딕셔너리입니다.
print(response)

```

### 2. 배경색 추가

1장의 4채널 투명 png를 입력하여 1장의 배경색이 추가된 이미지를 얻습니다.

```python
import requests

url = "http://127.0.0.1:8080/add_background"
input_image_path = "test.png"

files = {"input_image": open(input_image_path, "rb")}
data = {"color": '638cce', 'kb': None}

response = requests.post(url, files=files, data=data).json()

# response는 status와 image_base64를 포함하는 json 형식의 딕셔너리입니다.
print(response)
```

### 3. 6인치 배치 사진 얻기

1장의 3채널 사진을 입력하여 1장의 6인치 배치 사진을 얻습니다.

```python
import requests

url = "http://127.0.0.1:8080/generate_layout_photos"
input_image_path = "test.jpg"

files = {"input_image": open(input_image_path, "rb")}
data = {"height": 413, "width": 295, "kb": 200}

response = requests.post(url, files=files, data=data).json()

# response는 status와 image_base64를 포함하는 json 형식의 딕셔너리입니다.
print(response)
```

<br>

# 🐳 Docker 배포

## 1. 이미지 가져오기 또는 빌드하기

> 다음 방법 중 하나 선택

**방법 1: 최신 이미지 가져오기:**

```bash
docker pull linzeyi/hivision_idphotos
```

**방법 2: Dockerfile로 직접 이미지 빌드:**

모델 가중치 파일 [hivision_modnet.onnx](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/tag/pretrained-model)를 `hivision/creator/weights`에 넣은 후, 프로젝트 루트 디렉토리에서 실행:

```bash
docker build -t linzeyi/hivision_idphotos .
```

**방법 3: Docker compose로 빌드:**

모델 가중치 파일 [hivision_modnet.onnx](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/tag/pretrained-model)를 `hivision/creator/weights`에 넣은 후, 프로젝트 루트 디렉토리에서 실행:

```bash
docker compose build
```

## 2. 서비스 실행

**Gradio Demo 서비스 시작**

아래 명령을 실행하여 로컬에서 [http://127.0.0.1:7860](http://127.0.0.1:7860/)에 접속하여 사용합니다.

```bash
docker run -d -p 7860:7860 linzeyi/hivision_idphotos
```

**API 백엔드 서비스 시작**

```bash
docker run -d -p 8080:8080 linzeyi/hivision_idphotos python3 deploy_api.py
```

**두 서비스 동시에 시작**

```bash
docker compose up -d
```

## 환경 변수

본 프로젝트는 몇 가지 추가 설정을 환경 변수를 사용하여 설정할 수 있습니다:

| 환경 변수 | 유형 | 설명 | 예시 |
|--|--|--|--|
| FACE_PLUS_API_KEY | 선택 | Face++ 콘솔에서 신청한 API 키 | `7-fZStDJ····` |
| FACE_PLUS_API_SECRET | 선택 | Face++ API 키에 해당하는 Secret | `VTee824E····` |

docker 환경 변수 사용 예시:
```bash
docker run -d -p 7860:7860 \
    -e FACE_PLUS_API_KEY=7-fZStDJ···· \
    -e FACE_PLUS_API_SECRET=VTee824E···· \
    linzeyi/hivision_idphotos 
```

<br>

# 🌲 링크

- [HivisionIDPhotos-windows-GUI](https://github.com/zhaoyun0071/HivisionIDPhotos-windows-GUI)

<br>

# 📖 인용 프로젝트

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

# 💻 개발 팁

**1. 프리셋 사이즈 수정 방법은?**

[size_list_CN.csv](demo/size_list_CN.csv)를 수정한 후 다시 app.py를 실행하면 됩니다. 첫 번째 열은 사이즈 이름, 두 번째 열은 높이, 세 번째 열은 너비입니다.

<br>

# 📧 연락처

궁금한 점이 있으시면 zeyi.lin@swanhub.co로 이메일을 보내주세요.

<br>

# 기여자

<a href="https://github.com/Zeyi-Lin/HivisionIDPhotos/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Zeyi-Lin/HivisionIDPhotos" />
</a>

[Zeyi-Lin](https://github.com/Zeyi-Lin)、[SAKURA-CAT](https://github.com/SAKURA-CAT)、[Feudalman](https://github.com/Feudalman)、[swpfY](https://github.com/swpfY)、[Kaikaikaifang](https://github.com/Kaikaikaifang)、[ShaohonChen](https://github.com/ShaohonChen)、[KashiwaByte](https://github.com/KashiwaByte)

<br>

# StarHistory

[![Star History Chart](https://api.star-history.com/svg?repos=Zeyi-Lin/HivisionIDPhotos&type=Date)](https://star-history.com/#Zeyi-Lin/HivisionIDPhotos&Date)

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