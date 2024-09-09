import os
from demo.utils import csv_to_size_list


def load_configuration(root_dir):
    size_list_dict_CN = csv_to_size_list(os.path.join(root_dir, "size_list_CN.csv"))
    size_list_dict_EN = csv_to_size_list(os.path.join(root_dir, "size_list_EN.csv"))

    color_list_dict_CN = {
        "蓝色": (86, 140, 212),
        "白色": (255, 255, 255),
        "红色": (233, 51, 35),
        "黑色": (0, 0, 0),
        "深蓝色": (69, 98, 148),
    }

    color_list_dict_EN = {
        "Blue": (86, 140, 212),
        "White": (255, 255, 255),
        "Red": (233, 51, 35),
        "Black": (0, 0, 0),
        "Dark blue": (69, 98, 148),
    }

    return size_list_dict_CN, size_list_dict_EN, color_list_dict_CN, color_list_dict_EN
