from hivision.creator.human_matting import *
from hivision.creator.face_detector import *


HUMAN_MATTING_MODELS = [
    "modnet_photographic_portrait_matting",
    "birefnet-v1-lite",
    "hivision_modnet",
    "rmbg-1.4",
]

FACE_DETECT_MODELS = ["face++ (联网Online API)", "mtcnn", "retinaface-resnet50"]


def choose_handler(creator, matting_model_option=None, face_detect_option=None):
    if matting_model_option == "modnet_photographic_portrait_matting":
        creator.matting_handler = extract_human_modnet_photographic_portrait_matting
    elif matting_model_option == "mnn_hivision_modnet":
        creator.matting_handler = extract_human_mnn_modnet
    elif matting_model_option == "rmbg-1.4":
        creator.matting_handler = extract_human_rmbg
    elif matting_model_option == "birefnet-v1-lite":
        creator.matting_handler = extract_human_birefnet_lite
    else:
        creator.matting_handler = extract_human

    if (
        face_detect_option == "face_plusplus"
        or face_detect_option == "face++ (联网Online API)"
    ):
        creator.detection_handler = detect_face_face_plusplus
    elif face_detect_option == "retinaface-resnet50":
        creator.detection_handler = detect_face_retinaface
    else:
        creator.detection_handler = detect_face_mtcnn
