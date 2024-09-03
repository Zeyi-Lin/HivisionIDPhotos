# Python API Docs

## 开启后端服务

在请求 API 之前，请先运行后端服务

```bash
python delopy_api.py
```

下面的请求示例是请求脚本与后端服务处于同一机子下的，如在不同机器，请更换`-u`参数值。

## 请求方法

```bash
python requests_api.py -u <URL> -t <TYPE> -i <INPUT_IMAGE_DIR> -o <OUTPUT_IMAGE_DIR> [-s <SIZE>] [-c <COLOR>] [-k <KB>]
```

## 参数说明

### 基本参数

- `-u`, `--url`

  - **描述**: API 服务的 URL。
  - **默认值**: `http://127.0.0.1:8080`

- `-t`, `--type`

  - **描述**: 请求 API 的种类，可选值有 `idphoto`、`add_background` 和 `generate_layout_photos`。分别代表证件照制作、透明图加背景和排版照生成。
  - **默认值**: `idphoto`

- `-i`, `--input_image_dir`

  - **描述**: 输入图像路径。
  - **必需**: 是
  - **示例**: `./input_images/photo.jpg`

- `-o`, `--output_image_dir`
  - **描述**: 保存图像路径。
  - **必需**: 是
  - **示例**: `./output_images/processed_photo.jpg`

### 可选参数

- `-s`, `--size`

  - **描述**: 标准证件照的输出尺寸，格式为 `(高度, 宽度)`。
  - **默认值**: `(413,295)`

- `-c`, `--color`

  - **描述**: 给透明图增加背景色，格式为 `(R, G, B)`，仅在 type 为`add_background`时生效
  - **默认值**: `(255,255,255)`

- `-k`, `--kb`
  - **描述**: 输出照片的 KB 值，仅在 type 为`add_background`和`generate_layout_photos`时生效，值为 None 时不做设置。
  - **默认值**: `None`
  - **示例**: `50`

## 功能示例

### 1.生成证件照(底透明)

`生成证件照`接口的逻辑是发送一张 RGB 图像，输出一张标准证件照和一张高清证件照：

- **高清证件照**：根据`size`的宽高比例制作的证件照，文件名为`output_image_dir`增加`_hd`后缀
- **标准证件照**：尺寸等于`size`，由高清证件照缩放而来，文件名为`output_image_dir`

需要注意的是，生成的两张照片都是透明的（RGBA 四通道图像），要生成完整的证件照，还需要下面的`添加背景色`接口。

> 问：为什么这么设计？  
> 答：因为在实际产品中，经常用户会频繁切换底色预览效果，直接给透明底图像，由前端 js 代码合成颜色是更好体验的做法。

```bash
python requests_api.py  \
    -u http://127.0.0.1:8080 \
    -t idphoto \
    -i ./photo.jpg \
    -o ./idphoto.png \
    -s (413,295)
```

### 2.添加背景色

`添加背景色`接口的逻辑是发送一张 RGBA 图像，根据`color`添加背景色，合成一张 JPG 图像。

```bash
python requests_api.py
    -u http://127.0.0.1:8080  \
    -t add_background  \
    -i ./idphoto.png  \
    -o ./idphoto_with_background.jpg \
    -c (0,0,255)  \
    -k 50
```

### 3.生成六寸排版照

`生成六寸排版照`接口的逻辑是发送一张 RGB 图像（一般为添加背景色之后的证件照），根据`size`进行照片排布，然后生成一张六寸排版照。

```bash
python requests_api.py
    -u http://127.0.0.1:8080  \
    -t generate_layout_photos  \
    -i ./idphoto_with_background.jpg  \
    -o ./layout_photo.jpg  \
    -s (413,295)  \
    -k 200
```

## 请求失败的情况

- 照片中检测到的人脸大于 1，则失败
