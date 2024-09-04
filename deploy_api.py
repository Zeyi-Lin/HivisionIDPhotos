from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse
import tempfile
import onnxruntime
from src.face_judgement_align import IDphotos_create
from src.layoutCreate import generate_layout_photo, generate_layout_image
from hivisionai.hycv.vision import add_background
from utils import numpy_2_base64
import numpy as np
import cv2
import ast
from utils import save_numpy_image
from loguru import logger

app = FastAPI()


"""证件照制作接口

input_image: 上传的图像文件
size: 证件照尺寸，格式为字符串，如 '(413,295)'
hd_mode: 是否输出高清照片，默认为false

"""


@app.post("/idphoto")
async def idphoto_inference(
    input_image: UploadFile,
    size: str = Form(...),
    hd_mode: bool = Form(False),
    head_measure_ratio=0.2,
    head_height_ratio=0.45,
    top_distance_max=0.12,
    top_distance_min=0.10,
):
    try:
        image_bytes = await input_image.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    except Exception:
        err_msg: str = "read image error"
        logger.error(err_msg)
        result_messgae = {"status": False, "err_msg": err_msg}
        return result_messgae

    try:
        # 将字符串转为元组
        size = ast.literal_eval(size)
    except Exception:
        err_msg = "size param error, expect format like '(418,295)'"
        logger.error(err_msg)
        result_messgae = {"status": False, "err_msg": err_msg}
        return result_messgae

    (
        result_image_hd,
        result_image_standard,
        typography_arr,
        typography_rotate,
        _,
        _,
        _,
        _,
        status,
    ) = IDphotos_create(
        img,
        size=size,
        head_measure_ratio=head_measure_ratio,
        head_height_ratio=head_height_ratio,
        align=False,
        beauty=False,
        fd68=None,
        human_sess=sess,
        IS_DEBUG=False,
        top_distance_max=top_distance_max,
        top_distance_min=top_distance_min,
    )

    # 如果检测到人脸数量不等于 1（照片无人脸 or 多人脸）
    if status == 0:
        result_messgae = {"status": False}
        return result_messgae
    else:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".png"
        ) as temp_standard, tempfile.NamedTemporaryFile(
            delete=False, suffix=".png"
        ) as temp_hd:
            temp_standard_path = temp_standard.name
            temp_hd_path = temp_hd.name

            # 假设 save_numpy_image 是一个将 numpy 图像保存为文件的函数
            save_numpy_image(result_image_standard, temp_standard_path)
            save_numpy_image(result_image_hd, temp_hd_path)

            if hd_mode:
                return FileResponse(
                    temp_hd_path, media_type="image/png", filename="output_hd.png"
                )
            else:
                return FileResponse(
                    temp_standard_path,
                    media_type="image/png",
                    filename="output_standard.png",
                )


# 透明图像添加纯色背景接口
@app.post("/add_background")
async def photo_add_background(input_image: UploadFile, color: str = Form(...)):
    # 读取图像
    try:
        image_bytes = await input_image.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    except Exception:
        err_msg = "read image error"
        logger.error(err_msg)
        result_messgae = {"status": False, "err_msg": err_msg}
        return result_messgae

    try:
        # 将字符串转为元组
        color = ast.literal_eval(color)
        # 将元组的 0 和 2 号数字交换
        color = (color[2], color[1], color[0])
    except Exception:
        err_msg = "color param error, expect format like '(255,255,255)'"
        logger.error(err_msg)
        result_messgae = {"status": False, "err_msg": err_msg}
        return result_messgae

    bg_img = add_background(img, bgr=color)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
        temp_path = temp.name
        save_numpy_image(bg_img, temp_path)
        return FileResponse(temp_path, media_type="image/jpeg", filename="output.jpg")


# 六寸排版照生成接口
@app.post("/generate_layout_photos")
async def generate_layout_photos(input_image: UploadFile, size: str = Form(...)):
    try:
        image_bytes = await input_image.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    except Exception:
        err_msg = "read image error"
        logger.error(err_msg)
        result_messgae = {"status": False, "err_msg": err_msg}
        return result_messgae

    try:
        size = ast.literal_eval(size)
    except Exception:
        err_msg = "size param error, expect format like '(418,295)'"
        logger.error(err_msg)
        result_messgae = {"status": False, "err_msg": err_msg}
        return result_messgae

    logger.info(f"size: {size}")
    try:
        typography_arr, typography_rotate = generate_layout_photo(
            input_height=size[0], input_width=size[1]
        )

        result_layout_image = generate_layout_image(
            img, typography_arr, typography_rotate, height=size[0], width=size[1]
        )
    except Exception as e:
        result_messgae = {
            "status": False,
        }
        return result_messgae

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
        temp_path = temp.name
        save_numpy_image(result_layout_image, temp_path)
        return FileResponse(temp_path, media_type="image/jpeg", filename="output.jpg")


if __name__ == "__main__":
    import uvicorn

    # 加载权重文件
    HY_HUMAN_MATTING_WEIGHTS_PATH = "./hivision_modnet.onnx"
    sess = onnxruntime.InferenceSession(HY_HUMAN_MATTING_WEIGHTS_PATH)

    # 在 8080 端口运行推理服务
    uvicorn.run(app, host="0.0.0.0", port=8080)
