from fastapi import FastAPI, UploadFile, Form
import onnxruntime
from hivision import IDCreator
from hivision.error import FaceError
from hivision.creator.layout_calculator import (
    generate_layout_photo,
    generate_layout_image,
)
from hivision.utils import add_background, resize_image_to_kb_base64, hex_to_rgb
import base64
import numpy as np
import cv2
import os

app = FastAPI()
creator = IDCreator()


# 将图像转换为Base64编码
def numpy_2_base64(img: np.ndarray):
    retval, buffer = cv2.imencode(".png", img)
    base64_image = base64.b64encode(buffer).decode("utf-8")

    return base64_image


# 证件照智能制作接口
@app.post("/idphoto")
async def idphoto_inference(
    input_image: UploadFile,
    height: str = Form(...),
    width: str = Form(...),
    head_measure_ratio=0.2,
    head_height_ratio=0.45,
    top_distance_max=0.12,
    top_distance_min=0.10,
):

    image_bytes = await input_image.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 将字符串转为元组
    size = (int(height), int(width))
    try:
        result = creator(
            img,
            size=size,
            head_measure_ratio=head_measure_ratio,
            head_height_ratio=head_height_ratio,
        )
    except FaceError:
        result_message = {"status": False}
    # 如果检测到人脸数量等于1, 则返回标准证和高清照结果（png 4通道图像）
    else:
        result_message = {
            "status": True,
            "image_base64_standard": numpy_2_base64(result.standard),
            "image_base64_hd": numpy_2_base64(result.hd),
        }

    return result_message


# 透明图像添加纯色背景接口
@app.post("/add_background")
async def photo_add_background(
    input_image: UploadFile, color: str = Form(...), kb: str = Form(None)
):
    image_bytes = await input_image.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

    color = hex_to_rgb(color)
    color = (color[2], color[1], color[0])

    result_image = add_background(img, bgr=color).astype(np.uint8)

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
    height: str = Form(...),
    width: str = Form(...),
    kb: str = Form(None),
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


if __name__ == "__main__":
    import uvicorn

    # 加载权重文件
    root_dir = os.path.dirname(os.path.abspath(__file__))
    HY_HUMAN_MATTING_WEIGHTS_PATH = os.path.join(
        root_dir, "hivision/creator/weights/hivision_modnet.onnx"
    )
    sess = onnxruntime.InferenceSession(HY_HUMAN_MATTING_WEIGHTS_PATH)

    # 在8080端口运行推理服务
    uvicorn.run(app, host="0.0.0.0", port=8080)
