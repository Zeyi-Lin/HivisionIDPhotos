import numpy as np
from .box_utils import nms, calibrate_box, get_image_boxes, convert_to_square
from .first_stage import run_first_stage
import onnxruntime
import os
from os.path import exists
import requests


def download_img(img_url, base_dir):
    print("Downloading Onnx Model in:",img_url)
    r = requests.get(img_url, stream=True)
    filename = img_url.split("/")[-1]
    # print(r.status_code) # 返回状态码
    if r.status_code == 200:
        open(f'{base_dir}/{filename}', 'wb').write(r.content) # 将内容写入图片
        print(f"Download Finshed -- {filename}")
    del r


def detect_faces(image, min_face_size=20.0, thresholds=None, nms_thresholds=None):
    """
    Arguments:
        image: an instance of PIL.Image.
        min_face_size: a float number.
        thresholds: a list of length 3.
        nms_thresholds: a list of length 3.

    Returns:
        two float numpy arrays of shapes [n_boxes, 4] and [n_boxes, 10],
        bounding boxes and facial landmarks.
    """
    if nms_thresholds is None:
        nms_thresholds = [0.7, 0.7, 0.7]
    if thresholds is None:
        thresholds = [0.6, 0.7, 0.8]
    base_url = "https://linimages.oss-cn-beijing.aliyuncs.com/"
    onnx_filedirs = ["pnet.onnx",  "rnet.onnx", "onet.onnx"]

    # LOAD MODELS
    basedir = os.path.dirname(os.path.realpath(__file__)).split("detector.py")[0]

    for onnx_filedir in onnx_filedirs:
        if not exists(f"{basedir}/weights"):
            os.mkdir(f"{basedir}/weights")
        if not exists(f"{basedir}/weights/{onnx_filedir}"):
            # download onnx model
            download_img(img_url=base_url+onnx_filedir, base_dir=f"{basedir}/weights")

    pnet = onnxruntime.InferenceSession(f"{basedir}/weights/pnet.onnx")  # Load a ONNX model
    input_name_pnet = pnet.get_inputs()[0].name
    output_name_pnet1 = pnet.get_outputs()[0].name
    output_name_pnet2 = pnet.get_outputs()[1].name
    pnet = [pnet, input_name_pnet, [output_name_pnet1, output_name_pnet2]]

    rnet = onnxruntime.InferenceSession(f"{basedir}/weights/rnet.onnx")  # Load a ONNX model
    input_name_rnet = rnet.get_inputs()[0].name
    output_name_rnet1 = rnet.get_outputs()[0].name
    output_name_rnet2 = rnet.get_outputs()[1].name
    rnet = [rnet, input_name_rnet, [output_name_rnet1, output_name_rnet2]]

    onet = onnxruntime.InferenceSession(f"{basedir}/weights/onet.onnx")  # Load a ONNX model
    input_name_onet = onet.get_inputs()[0].name
    output_name_onet1 = onet.get_outputs()[0].name
    output_name_onet2 = onet.get_outputs()[1].name
    output_name_onet3 = onet.get_outputs()[2].name
    onet = [onet, input_name_onet, [output_name_onet1, output_name_onet2, output_name_onet3]]

    # BUILD AN IMAGE PYRAMID
    width, height = image.size
    min_length = min(height, width)

    min_detection_size = 12
    factor = 0.707  # sqrt(0.5)

    # scales for scaling the image
    scales = []

    # scales the image so that
    # minimum size that we can detect equals to
    # minimum face size that we want to detect
    m = min_detection_size/min_face_size
    min_length *= m

    factor_count = 0
    while min_length > min_detection_size:
        scales.append(m*factor**factor_count)
        min_length *= factor
        factor_count += 1

    # STAGE 1

    # it will be returned
    bounding_boxes = []

    # run P-Net on different scales
    for s in scales:
        boxes = run_first_stage(image, pnet, scale=s, threshold=thresholds[0])
        bounding_boxes.append(boxes)

    # collect boxes (and offsets, and scores) from different scales
    bounding_boxes = [i for i in bounding_boxes if i is not None]
    bounding_boxes = np.vstack(bounding_boxes)

    keep = nms(bounding_boxes[:, 0:5], nms_thresholds[0])
    bounding_boxes = bounding_boxes[keep]

    # use offsets predicted by pnet to transform bounding boxes
    bounding_boxes = calibrate_box(bounding_boxes[:, 0:5], bounding_boxes[:, 5:])
    # shape [n_boxes, 5]

    bounding_boxes = convert_to_square(bounding_boxes)
    bounding_boxes[:, 0:4] = np.round(bounding_boxes[:, 0:4])

    # STAGE 2

    img_boxes = get_image_boxes(bounding_boxes, image, size=24)

    output = rnet[0].run([rnet[2][0], rnet[2][1]], {rnet[1]: img_boxes})
    offsets = output[0]  # shape [n_boxes, 4]
    probs = output[1]  # shape [n_boxes, 2]

    keep = np.where(probs[:, 1] > thresholds[1])[0]
    bounding_boxes = bounding_boxes[keep]
    bounding_boxes[:, 4] = probs[keep, 1].reshape((-1,))
    offsets = offsets[keep]

    keep = nms(bounding_boxes, nms_thresholds[1])
    bounding_boxes = bounding_boxes[keep]
    bounding_boxes = calibrate_box(bounding_boxes, offsets[keep])
    bounding_boxes = convert_to_square(bounding_boxes)
    bounding_boxes[:, 0:4] = np.round(bounding_boxes[:, 0:4])

    # STAGE 3

    img_boxes = get_image_boxes(bounding_boxes, image, size=48)
    if len(img_boxes) == 0: 
        return [], []
    #img_boxes = Variable(torch.FloatTensor(img_boxes), volatile=True)
    # with torch.no_grad():
    #     img_boxes = torch.FloatTensor(img_boxes)
    # output = onet(img_boxes)
    output = onet[0].run([onet[2][0], onet[2][1], onet[2][2]], {rnet[1]: img_boxes})
    landmarks = output[0]  # shape [n_boxes, 10]
    offsets = output[1]  # shape [n_boxes, 4]
    probs = output[2]  # shape [n_boxes, 2]

    keep = np.where(probs[:, 1] > thresholds[2])[0]
    bounding_boxes = bounding_boxes[keep]
    bounding_boxes[:, 4] = probs[keep, 1].reshape((-1,))
    offsets = offsets[keep]
    landmarks = landmarks[keep]

    # compute landmark points
    width = bounding_boxes[:, 2] - bounding_boxes[:, 0] + 1.0
    height = bounding_boxes[:, 3] - bounding_boxes[:, 1] + 1.0
    xmin, ymin = bounding_boxes[:, 0], bounding_boxes[:, 1]
    landmarks[:, 0:5] = np.expand_dims(xmin, 1) + np.expand_dims(width, 1)*landmarks[:, 0:5]
    landmarks[:, 5:10] = np.expand_dims(ymin, 1) + np.expand_dims(height, 1)*landmarks[:, 5:10]

    bounding_boxes = calibrate_box(bounding_boxes, offsets)
    keep = nms(bounding_boxes, nms_thresholds[2], mode='min')
    bounding_boxes = bounding_boxes[keep]
    landmarks = landmarks[keep]

    return bounding_boxes, landmarks
