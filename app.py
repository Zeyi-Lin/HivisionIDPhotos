import argparse
import os
from demo.processor import IDPhotoProcessor
from demo.ui import create_ui
from hivision.creator.choose_handler import HUMAN_MATTING_MODELS

root_dir = os.path.dirname(os.path.abspath(__file__))

# 获取存在的人像分割模型列表
# 通过检查 hivision/creator/weights 目录下的 .onnx 和 .mnn 文件
# 只保留文件名（不包括扩展名）
HUMAN_MATTING_MODELS_EXIST = [
    os.path.splitext(file)[0]
    for file in os.listdir(os.path.join(root_dir, "hivision/creator/weights"))
    if file.endswith(".onnx") or file.endswith(".mnn")
]
# 在HUMAN_MATTING_MODELS中的模型才会被加载到Gradio中显示
HUMAN_MATTING_MODELS_CHOICE = [
    model for model in HUMAN_MATTING_MODELS if model in HUMAN_MATTING_MODELS_EXIST
]

if len(HUMAN_MATTING_MODELS_CHOICE) == 0:
    raise ValueError(
        "未找到任何存在的人像分割模型，请检查 hivision/creator/weights 目录下的文件"
        + "\n"
        + "No existing portrait segmentation model was found, please check the files in the hivision/creator/weights directory."
    )

FACE_DETECT_MODELS = ["face++ (联网Online API)", "mtcnn"]
FACE_DETECT_MODELS_EXPAND = (
    ["retinaface-resnet50"]
    if os.path.exists(
        os.path.join(
            root_dir, "hivision/creator/retinaface/weights/retinaface-resnet50.onnx"
        )
    )
    else []
)
FACE_DETECT_MODELS_CHOICE = FACE_DETECT_MODELS + FACE_DETECT_MODELS_EXPAND

LANGUAGE = ["zh", "en", "ko", "ja"]

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--port", type=int, default=7860, help="The port number of the server"
    )
    argparser.add_argument(
        "--host", type=str, default="127.0.0.1", help="The host of the server"
    )
    argparser.add_argument(
        "--root_path",
        type=str,
        default=None,
        help="The root path of the server, default is None (='/'), e.g. '/myapp'",
    )
    args = argparser.parse_args()

    processor = IDPhotoProcessor()

    demo = create_ui(
        processor,
        root_dir,
        HUMAN_MATTING_MODELS_CHOICE,
        FACE_DETECT_MODELS_CHOICE,
        LANGUAGE,
    )
    
    # 如果RUN_MODE是Beast，打印已开启野兽模式
    if os.getenv("RUN_MODE") == "beast":
        print("[Beast mode activated.] 已开启野兽模式。")

    demo.launch(
        server_name=args.host,
        server_port=args.port,
        favicon_path=os.path.join(root_dir, "assets/hivision_logo.png"),
        root_path=args.root_path,
        show_api=False,
    )
