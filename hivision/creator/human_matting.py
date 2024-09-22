#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
@DATE: 2024/9/5 21:21
@File: human_matting.py
@IDE: pycharm
@Description:
    人像抠图
"""
import numpy as np
from PIL import Image
import onnxruntime
from .tensor2numpy import NNormalize, NTo_Tensor, NUnsqueeze
from .context import Context
import cv2
import os
from time import time


WEIGHTS = {
    "hivision_modnet": os.path.join(
        os.path.dirname(__file__), "weights", "hivision_modnet.onnx"
    ),
    "modnet_photographic_portrait_matting": os.path.join(
        os.path.dirname(__file__),
        "weights",
        "modnet_photographic_portrait_matting.onnx",
    ),
    "mnn_hivision_modnet": os.path.join(
        os.path.dirname(__file__),
        "weights",
        "mnn_hivision_modnet.mnn",
    ),
    "rmbg-1.4": os.path.join(os.path.dirname(__file__), "weights", "rmbg-1.4.onnx"),
    "birefnet-v1-lite": os.path.join(
        os.path.dirname(__file__), "weights", "birefnet-v1-lite.onnx"
    ),
}

ONNX_DEVICE = onnxruntime.get_device()
ONNX_PROVIDER = (
    "CUDAExecutionProvider" if ONNX_DEVICE == "GPU" else "CPUExecutionProvider"
)

HIVISION_MODNET_SESS = None
MODNET_PHOTOGRAPHIC_PORTRAIT_MATTING_SESS = None
RMBG_SESS = None
BIREFNET_V1_LITE_SESS = None


def load_onnx_model(checkpoint_path, set_cpu=False):
    providers = (
        ["CUDAExecutionProvider", "CPUExecutionProvider"]
        if ONNX_PROVIDER == "CUDAExecutionProvider"
        else ["CPUExecutionProvider"]
    )

    if set_cpu:
        sess = onnxruntime.InferenceSession(
            checkpoint_path, providers=["CPUExecutionProvider"]
        )
    else:
        try:
            sess = onnxruntime.InferenceSession(checkpoint_path, providers=providers)
        except Exception as e:
            if ONNX_DEVICE == "CUDAExecutionProvider":
                print(f"Failed to load model with CUDAExecutionProvider: {e}")
                print("Falling back to CPUExecutionProvider")
                # 尝试使用CPU加载模型
                sess = onnxruntime.InferenceSession(
                    checkpoint_path, providers=["CPUExecutionProvider"]
                )
            else:
                raise e  # 如果是CPU执行失败，重新抛出异常

    return sess


def extract_human(ctx: Context):
    """
    人像抠图
    :param ctx: 上下文
    """
    # 抠图
    matting_image = get_modnet_matting(ctx.processing_image, WEIGHTS["hivision_modnet"])
    # 修复抠图
    ctx.processing_image = hollow_out_fix(matting_image)
    ctx.matting_image = ctx.processing_image.copy()


def extract_human_modnet_photographic_portrait_matting(ctx: Context):
    """
    人像抠图
    :param ctx: 上下文
    """
    # 抠图
    matting_image = get_modnet_matting_photographic_portrait_matting(
        ctx.processing_image, WEIGHTS["modnet_photographic_portrait_matting"]
    )
    # 修复抠图
    ctx.processing_image = matting_image
    ctx.matting_image = ctx.processing_image.copy()


def extract_human_mnn_modnet(ctx: Context):
    matting_image = get_mnn_modnet_matting(
        ctx.processing_image, WEIGHTS["mnn_hivision_modnet"]
    )
    ctx.processing_image = hollow_out_fix(matting_image)
    ctx.matting_image = ctx.processing_image.copy()


def extract_human_rmbg(ctx: Context):
    matting_image = get_rmbg_matting(ctx.processing_image, WEIGHTS["rmbg-1.4"])
    ctx.processing_image = matting_image
    ctx.matting_image = ctx.processing_image.copy()


# def extract_human_birefnet_portrait(ctx: Context):
#     matting_image = get_birefnet_portrait_matting(
#         ctx.processing_image, WEIGHTS["birefnet-portrait"]
#     )
#     ctx.processing_image = matting_image
#     ctx.matting_image = ctx.processing_image.copy()


def extract_human_birefnet_lite(ctx: Context):
    matting_image = get_birefnet_portrait_matting(
        ctx.processing_image, WEIGHTS["birefnet-v1-lite"]
    )
    ctx.processing_image = matting_image
    ctx.matting_image = ctx.processing_image.copy()


def hollow_out_fix(src: np.ndarray) -> np.ndarray:
    """
    修补抠图区域，作为抠图模型精度不够的补充
    :param src:
    :return:
    """
    b, g, r, a = cv2.split(src)
    src_bgr = cv2.merge((b, g, r))
    # -----------padding---------- #
    add_area = np.zeros((10, a.shape[1]), np.uint8)
    a = np.vstack((add_area, a, add_area))
    add_area = np.zeros((a.shape[0], 10), np.uint8)
    a = np.hstack((add_area, a, add_area))
    # -------------end------------ #
    _, a_threshold = cv2.threshold(a, 127, 255, 0)
    a_erode = cv2.erode(
        a_threshold,
        kernel=cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)),
        iterations=3,
    )
    contours, hierarchy = cv2.findContours(
        a_erode, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )
    contours = [x for x in contours]
    # contours = np.squeeze(contours)
    contours.sort(key=lambda c: cv2.contourArea(c), reverse=True)
    a_contour = cv2.drawContours(np.zeros(a.shape, np.uint8), contours[0], -1, 255, 2)
    # a_base = a_contour[1:-1, 1:-1]
    h, w = a.shape[:2]
    mask = np.zeros(
        [h + 2, w + 2], np.uint8
    )  # mask 必须行和列都加 2，且必须为 uint8 单通道阵列
    cv2.floodFill(a_contour, mask=mask, seedPoint=(0, 0), newVal=255)
    a = cv2.add(a, 255 - a_contour)
    return cv2.merge((src_bgr, a[10:-10, 10:-10]))


def image2bgr(input_image):
    if len(input_image.shape) == 2:
        input_image = input_image[:, :, None]
    if input_image.shape[2] == 1:
        result_image = np.repeat(input_image, 3, axis=2)
    elif input_image.shape[2] == 4:
        result_image = input_image[:, :, 0:3]
    else:
        result_image = input_image

    return result_image


def read_modnet_image(input_image, ref_size=512):
    im = Image.fromarray(np.uint8(input_image))
    width, length = im.size[0], im.size[1]
    im = np.asarray(im)
    im = image2bgr(im)
    im = cv2.resize(im, (ref_size, ref_size), interpolation=cv2.INTER_AREA)
    im = NNormalize(im, mean=np.array([0.5, 0.5, 0.5]), std=np.array([0.5, 0.5, 0.5]))
    im = NUnsqueeze(NTo_Tensor(im))

    return im, width, length


def get_modnet_matting(input_image, checkpoint_path, ref_size=512):
    global HIVISION_MODNET_SESS

    if not os.path.exists(checkpoint_path):
        print(f"Checkpoint file not found: {checkpoint_path}")
        return None

    # 如果RUN_MODE不是野兽模式，则不加载模型
    if HIVISION_MODNET_SESS is None:
        HIVISION_MODNET_SESS = load_onnx_model(checkpoint_path, set_cpu=True)

    input_name = HIVISION_MODNET_SESS.get_inputs()[0].name
    output_name = HIVISION_MODNET_SESS.get_outputs()[0].name

    im, width, length = read_modnet_image(input_image=input_image, ref_size=ref_size)

    matte = HIVISION_MODNET_SESS.run([output_name], {input_name: im})
    matte = (matte[0] * 255).astype("uint8")
    matte = np.squeeze(matte)
    mask = cv2.resize(matte, (width, length), interpolation=cv2.INTER_AREA)
    b, g, r = cv2.split(np.uint8(input_image))

    output_image = cv2.merge((b, g, r, mask))
    
    # 如果RUN_MODE不是野兽模式，则释放模型
    if os.getenv("RUN_MODE") != "beast":
        HIVISION_MODNET_SESS = None

    return output_image


def get_modnet_matting_photographic_portrait_matting(
    input_image, checkpoint_path, ref_size=512
):
    global MODNET_PHOTOGRAPHIC_PORTRAIT_MATTING_SESS

    if not os.path.exists(checkpoint_path):
        print(f"Checkpoint file not found: {checkpoint_path}")
        return None

    # 如果RUN_MODE不是野兽模式，则不加载模型
    if MODNET_PHOTOGRAPHIC_PORTRAIT_MATTING_SESS is None:
        MODNET_PHOTOGRAPHIC_PORTRAIT_MATTING_SESS = load_onnx_model(
            checkpoint_path, set_cpu=True
        )

    input_name = MODNET_PHOTOGRAPHIC_PORTRAIT_MATTING_SESS.get_inputs()[0].name
    output_name = MODNET_PHOTOGRAPHIC_PORTRAIT_MATTING_SESS.get_outputs()[0].name

    im, width, length = read_modnet_image(input_image=input_image, ref_size=ref_size)

    matte = MODNET_PHOTOGRAPHIC_PORTRAIT_MATTING_SESS.run(
        [output_name], {input_name: im}
    )
    matte = (matte[0] * 255).astype("uint8")
    matte = np.squeeze(matte)
    mask = cv2.resize(matte, (width, length), interpolation=cv2.INTER_AREA)
    b, g, r = cv2.split(np.uint8(input_image))

    output_image = cv2.merge((b, g, r, mask))
    
    # 如果RUN_MODE不是野兽模式，则释放模型
    if os.getenv("RUN_MODE") != "beast":
        MODNET_PHOTOGRAPHIC_PORTRAIT_MATTING_SESS = None

    return output_image


def get_rmbg_matting(input_image: np.ndarray, checkpoint_path, ref_size=1024):
    global RMBG_SESS

    if not os.path.exists(checkpoint_path):
        print(f"Checkpoint file not found: {checkpoint_path}")
        return None

    def resize_rmbg_image(image):
        image = image.convert("RGB")
        model_input_size = (ref_size, ref_size)
        image = image.resize(model_input_size, Image.BILINEAR)
        return image

    if RMBG_SESS is None:
        RMBG_SESS = load_onnx_model(checkpoint_path, set_cpu=True)

    orig_image = Image.fromarray(input_image)
    image = resize_rmbg_image(orig_image)
    im_np = np.array(image).astype(np.float32)
    im_np = im_np.transpose(2, 0, 1)  # Change to CxHxW format
    im_np = np.expand_dims(im_np, axis=0)  # Add batch dimension
    im_np = im_np / 255.0  # Normalize to [0, 1]
    im_np = (im_np - 0.5) / 0.5  # Normalize to [-1, 1]

    # Inference
    result = RMBG_SESS.run(None, {RMBG_SESS.get_inputs()[0].name: im_np})[0]

    # Post process
    result = np.squeeze(result)
    ma = np.max(result)
    mi = np.min(result)
    result = (result - mi) / (ma - mi)  # Normalize to [0, 1]

    # Convert to PIL image
    im_array = (result * 255).astype(np.uint8)
    pil_im = Image.fromarray(
        im_array, mode="L"
    )  # Ensure mask is single channel (L mode)

    # Resize the mask to match the original image size
    pil_im = pil_im.resize(orig_image.size, Image.BILINEAR)

    # Paste the mask on the original image
    new_im = Image.new("RGBA", orig_image.size, (0, 0, 0, 0))
    new_im.paste(orig_image, mask=pil_im)
    
    # 如果RUN_MODE不是野兽模式，则释放模型
    if os.getenv("RUN_MODE") != "beast":
        RMBG_SESS = None

    return np.array(new_im)


def get_mnn_modnet_matting(input_image, checkpoint_path, ref_size=512):
    if not os.path.exists(checkpoint_path):
        print(f"Checkpoint file not found: {checkpoint_path}")
        return None

    try:
        import MNN.expr as expr
        import MNN.nn as nn
    except ImportError as e:
        raise ImportError(
            "The MNN module is not installed or there was an import error. Please ensure that the MNN library is installed by using the command 'pip install mnn'."
        ) from e

    config = {}
    config["precision"] = "low"  # 当硬件支持（armv8.2）时使用fp16推理
    config["backend"] = 0  # CPU
    config["numThread"] = 4  # 线程数
    im, width, length = read_modnet_image(input_image, ref_size=512)
    rt = nn.create_runtime_manager((config,))
    net = nn.load_module_from_file(
        checkpoint_path, ["input1"], ["output1"], runtime_manager=rt
    )
    input_var = expr.convert(im, expr.NCHW)
    output_var = net.forward(input_var)
    matte = expr.convert(output_var, expr.NCHW)
    matte = matte.read()  # var转换为np
    matte = (matte * 255).astype("uint8")
    matte = np.squeeze(matte)
    mask = cv2.resize(matte, (width, length), interpolation=cv2.INTER_AREA)
    b, g, r = cv2.split(np.uint8(input_image))

    output_image = cv2.merge((b, g, r, mask))

    return output_image


def get_birefnet_portrait_matting(input_image, checkpoint_path, ref_size=512):
    global BIREFNET_V1_LITE_SESS

    if not os.path.exists(checkpoint_path):
        print(f"Checkpoint file not found: {checkpoint_path}")
        return None

    def transform_image(image):
        image = image.resize((1024, 1024))  # Resize to 1024x1024
        image = (
            np.array(image, dtype=np.float32) / 255.0
        )  # Convert to numpy array and normalize to [0, 1]
        image = (image - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]  # Normalize
        image = np.transpose(image, (2, 0, 1))  # Change from (H, W, C) to (C, H, W)
        image = np.expand_dims(image, axis=0)  # Add batch dimension
        return image.astype(np.float32)  # Ensure the output is float32

    orig_image = Image.fromarray(input_image)
    input_images = transform_image(
        orig_image
    )  # This will already have the correct shape

    # 记录加载onnx模型的开始时间
    load_start_time = time()

    # 如果RUN_MODE不是野兽模式，则不加载模型
    if BIREFNET_V1_LITE_SESS is None:
        # print("首次加载birefnet-v1-lite模型...")
        if ONNX_DEVICE == "GPU":
            print("onnxruntime-gpu已安装，尝试使用CUDA加载模型")
            try:
                import torch
            except ImportError:
                print(
                    "torch未安装，尝试直接使用onnxruntime-gpu加载模型，这需要配置好CUDA和cuDNN"
                )
            BIREFNET_V1_LITE_SESS = load_onnx_model(checkpoint_path)
        else:
            BIREFNET_V1_LITE_SESS = load_onnx_model(checkpoint_path, set_cpu=True)

    # 记录加载onnx模型的结束时间
    load_end_time = time()

    # 打印加载onnx模型所花的时间
    print(f"Loading ONNX model took {load_end_time - load_start_time:.4f} seconds")

    input_name = BIREFNET_V1_LITE_SESS.get_inputs()[0].name
    print(onnxruntime.get_device(), BIREFNET_V1_LITE_SESS.get_providers())

    time_st = time()
    pred_onnx = BIREFNET_V1_LITE_SESS.run(None, {input_name: input_images})[
        -1
    ]  # Use float32 input
    pred_onnx = np.squeeze(pred_onnx)  # Use numpy to squeeze
    result = 1 / (1 + np.exp(-pred_onnx))  # Sigmoid function using numpy
    print(f"Inference time: {time() - time_st:.4f} seconds")

    # Convert to PIL image
    im_array = (result * 255).astype(np.uint8)
    pil_im = Image.fromarray(
        im_array, mode="L"
    )  # Ensure mask is single channel (L mode)

    # Resize the mask to match the original image size
    pil_im = pil_im.resize(orig_image.size, Image.BILINEAR)

    # Paste the mask on the original image
    new_im = Image.new("RGBA", orig_image.size, (0, 0, 0, 0))
    new_im.paste(orig_image, mask=pil_im)
    
    # 如果RUN_MODE不是野兽模式，则释放模型
    if os.getenv("RUN_MODE") != "beast":
        BIREFNET_V1_LITE_SESS = None

    return np.array(new_im)
