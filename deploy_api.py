from fastapi import FastAPI, UploadFile, Form
import onnxruntime
from src.face_judgement_align import IDphotos_create
from src.layoutCreate import generate_layout_photo, generate_layout_image
from hivisionai.hycv.vision import add_background
import base64
import numpy as np
import cv2
import ast

app = FastAPI()


# 将图像转换为Base64编码

def numpy_2_base64(img: np.ndarray):
    retval, buffer = cv2.imencode('.png', img)
    base64_image = base64.b64encode(buffer).decode('utf-8')

    return base64_image


# 证件照智能制作接口
@app.post("/idphoto")
async def idphoto_inference(input_image: UploadFile,
                            size: str = Form(...),
                            head_measure_ratio=0.2,
                            head_height_ratio=0.45,
                            top_distance_max=0.12,
                            top_distance_min=0.10):
    image_bytes = await input_image.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 将字符串转为元组
    size = ast.literal_eval(size)

    result_image_hd, result_image_standard, typography_arr, typography_rotate, \
        _, _, _, _, status = IDphotos_create(img,
                                             size=size,
                                             head_measure_ratio=head_measure_ratio,
                                             head_height_ratio=head_height_ratio,
                                             align=False,
                                             beauty=False,
                                             fd68=None,
                                             human_sess=sess,
                                             IS_DEBUG=False,
                                             top_distance_max=top_distance_max,
                                             top_distance_min=top_distance_min)

    # 如果检测到人脸数量不等于1（照片无人脸 or 多人脸）
    if status == 0:
        result_messgae = {
            "status": False
        }

    # 如果检测到人脸数量等于1, 则返回标准证和高清照结果（png 4通道图像）
    else:
        result_messgae = {
            "status": True,
            "img_output_standard": numpy_2_base64(result_image_standard),
            "img_output_standard_hd": numpy_2_base64(result_image_hd),
        }

    return result_messgae


# 透明图像添加纯色背景接口
@app.post("/add_background")
async def photo_add_background(input_image: UploadFile,
                               color: str = Form(...)):
    
    # 读取图像
    image_bytes = await input_image.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

    # 将字符串转为元组
    color = ast.literal_eval(color)
    # 将元祖的0和2号数字交换
    color = (color[2], color[1], color[0])

    # try:
    result_messgae = {
        "status": True,
        "image": numpy_2_base64(add_background(img, bgr=color)),
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
async def generate_layout_photos(input_image: UploadFile, size: str = Form(...)):
    try:
        image_bytes = await input_image.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        size = ast.literal_eval(size)

        typography_arr, typography_rotate = generate_layout_photo(input_height=size[0],
                                                                  input_width=size[1])

        result_layout_image = generate_layout_image(img, typography_arr,
                                                    typography_rotate,
                                                    height=size[0],
                                                    width=size[1])

        result_messgae = {
            "status": True,
            "image": numpy_2_base64(result_layout_image),
        }

    except Exception as e:
        result_messgae = {
            "status": False,
        }

    return result_messgae


if __name__ == "__main__":
    import uvicorn

    # 加载权重文件
    HY_HUMAN_MATTING_WEIGHTS_PATH = "./hivision_modnet.onnx"
    sess = onnxruntime.InferenceSession(HY_HUMAN_MATTING_WEIGHTS_PATH)

    # 在8080端口运行推理服务
    uvicorn.run(app, host="0.0.0.0", port=8080)
