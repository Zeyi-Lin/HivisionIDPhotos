import os
from demo.utils import csv_to_size_list, csv_to_color_list


def load_configuration(root_dir):
    size_list_dict_CN = csv_to_size_list(
        os.path.join(root_dir, "assets/size_list_CN.csv")
    )
    size_list_dict_EN = csv_to_size_list(
        os.path.join(root_dir, "assets/size_list_EN.csv")
    )
    color_list_dict_CN = csv_to_color_list(
        os.path.join(root_dir, "assets/color_list_CN.csv")
    )
    color_list_dict_EN = csv_to_color_list(
        os.path.join(root_dir, "assets/color_list_EN.csv")
    )

    return size_list_dict_CN, size_list_dict_EN, color_list_dict_CN, color_list_dict_EN
