from hivision.creator.human_matting import *
from hivision.creator.face_detector import *


def choose_handler(creator, matting_model_option=None, face_detect_option=None):
    if matting_model_option == "modnet_photographic_portrait_matting":
        creator.matting_handler = extract_human_modnet_photographic_portrait_matting
    elif matting_model_option == "mnn_hivision_modnet":
        creator.matting_handler = extract_human_mnn_modnet
    elif matting_model_option == "rmbg-1.4":
        creator.matting_handler = extract_human_rmbg
    else:
        creator.matting_handler = extract_human

    if face_detect_option == "face_plusplus":
        creator.detection_handler = detect_face_face_plusplus
    else:
        creator.detection_handler = detect_face_mtcnn
