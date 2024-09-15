import csv


def csv_to_size_list(csv_file: str) -> dict:
    # 初始化一个空字典
    size_list_dict = {}

    # 打开 CSV 文件并读取数据
    with open(csv_file, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        # 跳过表头
        next(reader)
        # 读取数据并填充字典
        for row in reader:
            size_name, h, w = row
            size_name_add_size = "{}\t\t({}, {})".format(size_name, h, w)
            size_list_dict[size_name_add_size] = (int(h), int(w))

    return size_list_dict


def csv_to_color_list(csv_file: str) -> dict:
    # 初始化一个空字典
    color_list_dict = {}

    # 打开 CSV 文件并读取数据
    with open(csv_file, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        # 跳过表头
        next(reader)
        # 读取数据并填充字典
        for row in reader:
            color_name, hex_code = row
            color_list_dict[color_name] = hex_code

    return color_list_dict


def range_check(value, min_value=0, max_value=255):
    value = int(value)
    return max(min_value, min(value, max_value))
