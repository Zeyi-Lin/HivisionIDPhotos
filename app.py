import argparse
import os
from demo.config import load_configuration
from demo.processor import IDPhotoProcessor
from demo.ui import create_ui

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

    root_dir = os.path.dirname(os.path.abspath(__file__))
    size_list_dict_CN, size_list_dict_EN, color_list_dict_CN, color_list_dict_EN = (
        load_configuration(root_dir)
    )
    processor = IDPhotoProcessor(
        size_list_dict_CN, size_list_dict_EN, color_list_dict_CN, color_list_dict_EN
    )

    demo = create_ui(processor, root_dir)
    demo.launch(
        server_name=args.host,
        server_port=args.port,
        show_api=False,
        favicon_path=os.path.join(root_dir, "assets/hivision_logo.png"),
        root_path=args.root_path,
    )
