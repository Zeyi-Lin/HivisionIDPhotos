import numpy as np
import cv2
import onnxruntime as ort
from hivision.creator.retinaface.box_utils import decode, decode_landm
from hivision.creator.retinaface.prior_box import PriorBox
import argparse


def py_cpu_nms(dets, thresh):
    """Pure Python NMS baseline."""
    x1 = dets[:, 0]
    y1 = dets[:, 1]
    x2 = dets[:, 2]
    y2 = dets[:, 3]
    scores = dets[:, 4]

    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    order = scores.argsort()[::-1]

    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        w = np.maximum(0.0, xx2 - xx1 + 1)
        h = np.maximum(0.0, yy2 - yy1 + 1)
        inter = w * h
        ovr = inter / (areas[i] + areas[order[1:]] - inter)

        inds = np.where(ovr <= thresh)[0]
        order = order[inds + 1]

    return keep


parser = argparse.ArgumentParser(description="Retinaface")

parser.add_argument(
    "--network", default="resnet50", help="Backbone network mobile0.25 or resnet50"
)
parser.add_argument(
    "--cpu", action="store_true", default=False, help="Use cpu inference"
)
parser.add_argument(
    "--confidence_threshold", default=0.8, type=float, help="confidence_threshold"
)
parser.add_argument("--top_k", default=5000, type=int, help="top_k")
parser.add_argument("--nms_threshold", default=0.2, type=float, help="nms_threshold")
parser.add_argument("--keep_top_k", default=750, type=int, help="keep_top_k")
parser.add_argument(
    "-s",
    "--save_image",
    action="store_true",
    default=True,
    help="show detection results",
)
parser.add_argument(
    "--vis_thres", default=0.6, type=float, help="visualization_threshold"
)
args = parser.parse_args()


def load_model_ort(model_path):
    ort_session = ort.InferenceSession(model_path)
    return ort_session


def retinaface_detect_faces(image, model_path: str):
    cfg = {
        "name": "Resnet50",
        "min_sizes": [[16, 32], [64, 128], [256, 512]],
        "steps": [8, 16, 32],
        "variance": [0.1, 0.2],
        "clip": False,
        "loc_weight": 2.0,
        "gpu_train": True,
        "batch_size": 24,
        "ngpu": 4,
        "epoch": 100,
        "decay1": 70,
        "decay2": 90,
        "image_size": 840,
        "pretrain": True,
        "return_layers": {"layer2": 1, "layer3": 2, "layer4": 3},
        "in_channel": 256,
        "out_channel": 256,
    }

    # Load ONNX model
    retinaface = load_model_ort(model_path)

    resize = 1

    # Read and preprocess the image
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img = np.float32(img_rgb)

    im_height, im_width, _ = img.shape
    scale = np.array([img.shape[1], img.shape[0], img.shape[1], img.shape[0]])
    img -= (104, 117, 123)
    img = img.transpose(2, 0, 1)
    img = np.expand_dims(img, axis=0)

    # Run the model
    inputs = {"input": img}
    loc, conf, landms = retinaface.run(None, inputs)

    # tic = time.time()
    priorbox = PriorBox(cfg, image_size=(im_height, im_width))
    priors = priorbox.forward()

    prior_data = priors

    boxes = decode(np.squeeze(loc, axis=0), prior_data, cfg["variance"])
    boxes = boxes * scale / resize
    scores = np.squeeze(conf, axis=0)[:, 1]

    landms = decode_landm(np.squeeze(landms.data, axis=0), prior_data, cfg["variance"])

    scale1 = np.array(
        [
            img.shape[3],
            img.shape[2],
            img.shape[3],
            img.shape[2],
            img.shape[3],
            img.shape[2],
            img.shape[3],
            img.shape[2],
            img.shape[3],
            img.shape[2],
        ]
    )
    landms = landms * scale1 / resize

    # ignore low scores
    inds = np.where(scores > args.confidence_threshold)[0]
    boxes = boxes[inds]
    landms = landms[inds]
    scores = scores[inds]

    # keep top-K before NMS
    order = scores.argsort()[::-1][: args.top_k]
    boxes = boxes[order]
    landms = landms[order]
    scores = scores[order]

    # do NMS
    dets = np.hstack((boxes, scores[:, np.newaxis])).astype(np.float32, copy=False)
    keep = py_cpu_nms(dets, args.nms_threshold)
    # keep = nms(dets, args.nms_threshold,force_cpu=args.cpu)
    dets = dets[keep, :]
    landms = landms[keep]

    # keep top-K faster NMS
    dets = dets[: args.keep_top_k, :]
    landms = landms[: args.keep_top_k, :]

    dets = np.concatenate((dets, landms), axis=1)
    # print("post processing time: {:.4f}s".format(time.time() - tic))

    return dets


if __name__ == "__main__":
    import gradio as gr

    # Create Gradio interface
    iface = gr.Interface(
        fn=retinaface_detect_faces,
        inputs=[
            gr.Image(
                type="numpy", label="上传图片", height=400
            ),  # Set the height to 400
            gr.Textbox(value="./FaceDetector.onnx", label="ONNX模型路径"),
        ],
        outputs=gr.Number(label="检测到的人脸数量"),
        title="人脸检测",
        description="上传图片并提供ONNX模型路径以检测人脸数量。",
    )

    # Launch the Gradio app
    iface.launch()
