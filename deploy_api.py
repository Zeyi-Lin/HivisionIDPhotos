from fastapi import FastAPI, UploadFile, Form
from hivision import IDCreator
from hivision.error import FaceError
from hivision.creator.layout_calculator import (
    generate_layout_photo,
    generate_layout_image,
)
from hivision.creator.choose_handler import choose_handler
from hivision.utils import (
    add_background,
    resize_image_to_kb_base64,
    hex_to_rgb,
    add_watermark,
)
import base64
import numpy as np
import cv2
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()
creator = IDCreator()

# 添加 CORS 中间件 解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的请求来源
    allow_credentials=True,  # 允许携带 Cookie
    allow_methods=[
        "*"
    ],  # 允许的请求方法，例如：GET, POST 等，也可以指定 ["GET", "POST"]
    allow_headers=["*"],  # 允许的请求头，也可以指定具体的头部
)


# 将图像转换为Base64编码
def numpy_2_base64(img: np.ndarray):
    retval, buffer = cv2.imencode(".png", img)
    base64_image = base64.b64encode(buffer).decode("utf-8")

    return "data:image/png;base64," + base64_image


# 证件照智能制作接口
@app.post("/idphoto")
async def idphoto_inference(
    input_image: UploadFile,
    height: int = Form(413),
    width: int = Form(295),
    human_matting_model: str = Form("hivision_modnet"),
    face_detect_model: str = Form("mtcnn"),
    hd: bool = Form(True),
    head_measure_ratio: float = 0.2,
    head_height_ratio: float = 0.45,
    top_distance_max: float = 0.12,
    top_distance_min: float = 0.10,
):
    image_bytes = await input_image.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # ------------------- 选择抠图与人脸检测模型 -------------------
    choose_handler(creator, human_matting_model, face_detect_model)

    # 将字符串转为元组
    size = (int(height), int(width))
    try:
        result = creator(
            img,
            size=size,
            head_measure_ratio=head_measure_ratio,
            head_height_ratio=head_height_ratio,
            head_top_range=(top_distance_max, top_distance_min),
        )
    except FaceError:
        result_message = {"status": False}
    # 如果检测到人脸数量等于1, 则返回标准证和高清照结果（png 4通道图像）
    else:
        result_message = {
            "status": True,
            "image_base64_standard": numpy_2_base64(result.standard),
        }

        # 如果hd为True, 则增加高清照结果（png 4通道图像）
        if hd:
            result_message["image_base64_hd"] = numpy_2_base64(result.hd)

    return result_message


# 人像抠图接口
@app.post("/human_matting")
async def human_matting_inference(
    input_image: UploadFile,
    human_matting_model: str = Form("hivision_modnet"),
):
    image_bytes = await input_image.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # ------------------- 选择抠图与人脸检测模型 -------------------
    choose_handler(creator, human_matting_model, None)

    try:
        result = creator(
            img,
            change_bg_only=True,
        )
    except FaceError:
        result_message = {"status": False}

    else:
        result_message = {
            "status": True,
            "image_base64": numpy_2_base64(result.standard),
        }
    return result_message


# 透明图像添加纯色背景接口
@app.post("/add_background")
async def photo_add_background(
    input_image: UploadFile,
    color: str = Form("000000"),
    kb: int = Form(None),
    render: int = Form(0),
):
    render_choice = ["pure_color", "updown_gradient", "center_gradient"]

    image_bytes = await input_image.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

    color = hex_to_rgb(color)
    color = (color[2], color[1], color[0])

    result_image = add_background(
        img,
        bgr=color,
        mode=render_choice[render],
    ).astype(np.uint8)

    if kb:
        result_image = cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR)
        result_image_base64 = resize_image_to_kb_base64(result_image, int(kb))
    else:
        result_image_base64 = numpy_2_base64(result_image)

    # try:
    result_messgae = {
        "status": True,
        "image_base64": result_image_base64,
    }

    # except Exception as e:
    #     print(e)
    #     result_messgae = {
    #         "status": False,
    #         "error": e
    #     }

    return result_messgae


# 六寸排版照生成接口
@app.post("/generate_layout_photos")
async def generate_layout_photos(
    input_image: UploadFile,
    height: int = Form(413),
    width: int = Form(295),
    kb: int = Form(None),
):
    # try:
    image_bytes = await input_image.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    size = (int(height), int(width))

    typography_arr, typography_rotate = generate_layout_photo(
        input_height=size[0], input_width=size[1]
    )

    result_layout_image = generate_layout_image(
        img, typography_arr, typography_rotate, height=size[0], width=size[1]
    ).astype(np.uint8)

    if kb:
        result_layout_image = cv2.cvtColor(result_layout_image, cv2.COLOR_RGB2BGR)
        result_layout_image_base64 = resize_image_to_kb_base64(
            result_layout_image, int(kb)
        )
    else:
        result_layout_image_base64 = numpy_2_base64(result_layout_image)

    result_messgae = {
        "status": True,
        "image_base64": result_layout_image_base64,
    }

    # except Exception as e:
    #     result_messgae = {
    #         "status": False,
    #     }

    return result_messgae


# 透明图像添加水印接口
@app.post("/watermark")
async def watermark(
    input_image: UploadFile,
    text: str = Form("Hello"),
    size: int = 20,
    opacity: float = 0.5,
    angle: int = 30,
    color: str = "#000000",
    space: int = 25,
    kb: int = Form(None),
):
    image_bytes = await input_image.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    try:
        result_image = add_watermark(img, text, size, opacity, angle, color, space)

        if kb:
            result_image = cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR)
            result_image_base64 = resize_image_to_kb_base64(result_image, int(kb))
        else:
            result_image_base64 = numpy_2_base64(result_image)

        result_messgae = {
            "status": True,
            "image_base64": result_image_base64,
        }
    except Exception as e:
        result_messgae = {
            "status": False,
            "error": e,
        }

    return result_messgae


# 设置照片KB值接口(RGB图)
@app.post("/set_kb")
async def set_kb(
    input_image: UploadFile,
    kb: int = Form(50),
):
    image_bytes = await input_image.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    try:
        result_image = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        result_image_base64 = resize_image_to_kb_base64(result_image, int(kb))

        result_messgae = {
            "status": True,
            "image_base64": result_image_base64,
        }
    except Exception as e:
        result_messgae = {
            "status": False,
            "error": e,
        }

    return result_messgae


# 证件照智能裁剪接口
@app.post("/idphoto_crop")
async def idphoto_crop_inference(
    input_image: UploadFile,
    height: int = Form(413),
    width: int = Form(295),
    face_detect_model: str = Form("mtcnn"),
    hd: bool = Form(True),
    head_measure_ratio: float = 0.2,
    head_height_ratio: float = 0.45,
    top_distance_max: float = 0.12,
    top_distance_min: float = 0.10,
):
    image_bytes = await input_image.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)  # 读取图像(4通道)

    # ------------------- 选择抠图与人脸检测模型 -------------------
    choose_handler(creator, face_detect_option=face_detect_model)

    # 将字符串转为元组
    size = (int(height), int(width))
    try:
        result = creator(
            img,
            size=size,
            head_measure_ratio=head_measure_ratio,
            head_height_ratio=head_height_ratio,
            head_top_range=(top_distance_max, top_distance_min),
            crop_only=True,
        )
    except FaceError:
        result_message = {"status": False}
    # 如果检测到人脸数量等于1, 则返回标准证和高清照结果（png 4通道图像）
    else:
        result_message = {
            "status": True,
            "image_base64_standard": numpy_2_base64(result.standard),
        }

        # 如果hd为True, 则增加高清照结果（png 4通道图像）
        if hd:
            result_message["image_base64_hd"] = numpy_2_base64(result.hd)

    return result_message


if __name__ == "__main__":
    import uvicorn

    # 在8080端口运行推理服务
    uvicorn.run(app, host="0.0.0.0", port=8080)
