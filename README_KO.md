<div align="center">
<h1>HivisionIDPhoto</h1>

[English](README_EN.md) / [中文](README_CN.md) / [日本語](README_JP.md) / 한국어

[![GitHub](https://img.shields.io/static/v1?label=GitHub&message=GitHub&color=black)](https://github.com/xiaolin199912/HivisionIDPhotos)
[![SwanHub Demo](https://swanhub.co/git/repo/SwanHub%2FAuto-README/file/preview?ref=main&path=swanhub.svg)](https://swanhub.co/ZeYiLin/HivisionIDPhotos/demo)
[![zhihu](https://img.shields.io/static/v1?label=知乎&message=知乎&color=blue)](https://zhuanlan.zhihu.com/p/638254028)
[![Spaces](https://img.shields.io/badge/🤗-Open%20in%20Spaces-blue)](https://huggingface.co/spaces/TheEeeeLin/HivisionIDPhotos)

<a href="https://trendshift.io/repositories/11622" target="_blank"><img src="https://trendshift.io/api/badge/repositories/11622" alt="Zeyi-Lin%2FHivisionIDPhotos | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

<img src="assets/demoImage.png" width=900>
</div>

<br>

> **관련 프로젝트**：
>
> - [SwanLab](https://github.com/SwanHubX/SwanLab)：인물 사진 모델의 학습을 분석 및 모니터링하고 실험실 동료와 협업하여 학습 효율성을 크게 향상시키기 위해 사용되었습니다.

<br>

# 🤩 프로젝트 업데이트

- 온라인 체험: [![SwanHub Demo](https://img.shields.io/static/v1?label=Demo&message=SwanHub%20Demo&color=blue)](https://swanhub.co/ZeYiLin/HivisionIDPhotos/demo)、[![Spaces](https://img.shields.io/badge/🤗-Open%20in%20Spaces-blue)](https://huggingface.co/spaces/TheEeeeLin/HivisionIDPhotos)
- 2024.9.2: **사진 KB 크기 조정** 업데이트
- 2023.12.1: **API 배포(fastapi 기반)** 업데이트
- 2023.6.20: **미리 설정된 사이즈 메뉴** 업데이트
- 2023.6.19: **레이아웃 사진** 업데이트
- 2023.6.13: **중앙 그라데이션 색상** 업데이트
- 2023.6.11: **상하 그라데이션 색상** 업데이트
- 2023.6.8: **맞춤형 사이즈** 업데이트
- 2023.6.4: **맞춤형 배경색, 얼굴 인식 오류 알림** 업데이트
- 2023.5.10: **크기 변경 없이 배경만 교체** 업데이트

# 개요

> 🚀 저희 작업에 관심을 가져주셔서 감사합니다. 이미지 분야의 다른 성과도 확인해보시기 바랍니다. 문의사항은 이메일로 연락주세요: zeyi.lin@swanhub.co.

HivisionIDPhoto는 실용적인 증명사진 자동 생성 알고리즘을 개발하는 것을 목표로 합니다.

이 프로젝트는 다양한 사용자 촬영 장면을 인식하고, 인물 사진을 배경에서 분리하여 증명사진을 생성할 수 있는 포괄적인 모델 워크플로우를 활용합니다.

**HivisionIDPhoto는 다음을 수행할 수 있습니다:**

1. 경량화된 배경 제거 (CPU만으로도 빠르게 추론 가능)
2. 다양한 크기 규격에 따라 표준 증명사진 및 여섯 컷 레이아웃 사진 생성
3. 미화(추후 지원 예정)
4. 지능형 정장 변경(추후 지원 예정)

<div align="center">
<img src="assets/gradio-image.jpeg" width=900>
</div>

---

HivisionIDPhoto가 유용하셨다면, 이 저장소에 별을 달거나 친구들에게 추천하여 증명사진 응급 제작 문제를 해결해보세요!

<br>

# 🔧 환경 설치 및 의존성

- Python >= 3.7 (프로젝트는 주로 Python 3.10에서 테스트되었습니다)
- onnxruntime
- OpenCV
- 선택 사항: Linux, Windows, MacOS

**1. 프로젝트 클론**

```bash
git clone https://github.com/Zeyi-Lin/HivisionIDPhotos.git
cd  HivisionIDPhotos
```

**2. 의존성 설치**

```bash
pip install -r requirements.txt
```

**3. 모델 가중치 다운로드**

[Release](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/tag/pretrained-model)에서 가중치 파일 `hivision_modnet.onnx`를 다운로드하여 루트 디렉토리에 저장하세요.

<br>

# 🚀 Gradio 데모 실행

```bash
python app.py
```

프로그램을 실행하면 로컬 웹 페이지가 생성되며, 해당 페이지에서 증명사진 작업 및 상호작용을 완료할 수 있습니다.

<br>

# ⚡️ API 서비스 배포

```
python deploy_api.py
```

**API 서비스 요청(Python)**

Python을 사용하여 서비스에 요청을 보낼 수 있습니다:

증명사진 생성(사진 1장을 입력하여 표준 증명사진 1장과 고해상도 증명사진의 4채널 투명 PNG 1장을 얻습니다):

```bash
python requests_api.py -u http://127.0.0.1:8080 -i images/test.jpg -o ./idphoto.png -s '(413,295)'
```

배경색 추가(4채널 투명 PNG 1장을 입력하여 배경색이 추가된 이미지를 얻습니다):

```bash
python requests_api.py -u http://127.0.0.1:8080 -t add_background -i ./idphoto.png -o ./idhoto_ab.jpg  -c '(0,0,0)' -k 30
```

여섯 컷 레이아웃 사진 얻기(3채널 사진 1장을 입력하여 여섯 컷 레이아웃 사진을 얻습니다):

```bash
python requests_api.py -u http://127.0.0.1:8080 -t generate_layout_photos -i ./idhoto_ab.jpg -o ./idhoto_layout.jpg  -s '(413,295)' -k 200
```

<br>

# 🐳 Docker 배포

## 1. 이미지 가져오기 또는 빌드

> 다음 3가지 방법 중 하나를 선택하십시오.

**이미지 가져오기:**

> 이 이미지는 ARM 아키텍처 머신(Mac M1 등)에서 빌드되었습니다. x86 아키텍처 머신에서 사용할 경우 Dockerfile을 사용하여 빌드하세요.

```bash
docker pull linzeyi/hivision_idphotos:v1
```

**Dockerfile로 이미지 빌드:**

모델 가중치 파일 [hivision_modnet.onnx](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/tag/pretrained-model)을 루트 디렉토리에 놓고, 루트 디렉토리에서 다음 명령어를 실행하세요:

```bash
docker build -t hivision_idphotos .
```

**Docker Compose:**

모델 가중치 파일 [hivision_modnet.onnx](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/tag/pretrained-model)가 루트 디렉터리에 있는지 확인한 후 루트 디렉터리에서 실행합니다:

```bash
도커 컴포즈 빌드
```

이미지 패키징이 완료되면 다음 명령어를 실행하여 API 서비스를 시작합니다:

```bash
docker compose up -d
```

## 2. Gradio 데모 실행

이미지 패키징이 완료되면 다음 명령어를 실행하여 Gradio 데모 서비스를 시작하세요:

```bash
docker run -p 7860:7860 hivision_idphotos
```

로컬에서 [http://127.0.0.1:7860](http://127.0.0.1:7860/)에 접속하여 사용할 수 있습니다.

## 3. API 백엔드 서비스 실행

```bash
docker run -p 8080:8080 hivision_idphotos python3 deploy_api.py
```

<br>

# 📖 프로젝트 인용

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

**1. 미리 설정된 사이즈를 어떻게 수정하나요?**

[size_list_CN.csv](size_list_CN.csv)을 수정한 후 app.py 를 다시 실행하세요. 첫 번째 열은 사이즈 이름, 두 번째 열은 높이, 세 번째 열은 너비입니다.

<br>

# 📧 문의하기

문의사항이 있으시면 zeyi.lin@swanhub.co 로 이메일을 보내주세요.

<br>

# 기여자

[Zeyi-Lin](https://github.com/Zeyi-Lin)、[SAKURA-CAT](https://github.com/SAKURA-CAT)、[Feudalman](https://github.com/Feudalman)、[swpfY](https://github.com/swpfY)、[Kaikaikaifang](https://github.com/Kaikaikaifang)、[ShaohonChen](https://github.com/ShaohonChen)、[KashiwaByte](https://github.com/KashiwaByte)

<br>

# StarHistory

[![Star History Chart](https://api.star-history.com/svg?repos=Zeyi-Lin/HivisionIDPhotos&type=Date)](https://star-history.com/#Zeyi-Lin/HivisionIDPhotos&Date)
