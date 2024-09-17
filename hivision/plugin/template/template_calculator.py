import cv2
import numpy as np
import json
from hivision.creator.rotation_adjust import rotate_bound
import os

base_path = os.path.dirname(os.path.abspath(__file__))
template_config_path = os.path.join(base_path, 'assets', 'template_config.json')

def generte_template_photo(template_name: str, input_image: np.ndarray) -> np.ndarray:
    """
    生成模板照片
    :param template_name: 模板名称
    :param input_image: 输入图像
    :return: 模板照片
    """
    # 读取模板配置json
    with open(template_config_path, 'r') as f:
        template_config_dict = json.load(f)
    # 获取对应该模板的配置
    template_config = template_config_dict[template_name]
    
    template_width = template_config['width']
    template_height = template_config['height']

    anchor_points = template_config['anchor_points']
    rotation = anchor_points['rotation']
    left_top = anchor_points['left_top']
    right_top = anchor_points['right_top']
    left_bottom = anchor_points['left_bottom']
    right_bottom = anchor_points['right_bottom']

    if rotation < 0:
        height = right_bottom[1] - left_top[1]
        width = right_top[0] - left_bottom[0]
    else:
        height = left_top[1] - right_bottom[1]
        width = left_bottom[0] - right_top[0]

    # 读取模板图像
    template_image_path = os.path.join(base_path, 'assets', f'{template_name}.png')
    template_image = cv2.imread(template_image_path, cv2.IMREAD_UNCHANGED)

    # 无损旋转
    rotated_image = rotate_bound(input_image, -1 * rotation)[0]
    rotated_image_height, rotated_image_width, _ = rotated_image.shape

    # 计算缩放比例
    scale_x = width / rotated_image_width
    scale_y = height / rotated_image_height
    scale = max(scale_x, scale_y)

    resized_image = cv2.resize(rotated_image, None, fx=scale, fy=scale)
    resized_height, resized_width, _ = resized_image.shape

    # 创建一个与template_image大小相同的背景，使用白色填充
    result = np.full((template_height, template_width, 3), 255, dtype=np.uint8)

    # 计算粘贴位置
    paste_x = left_bottom[0]
    paste_y = left_top[1]

    # 确保不会超出边界
    paste_height = min(resized_height, template_height - paste_y)
    paste_width = min(resized_width, template_width - paste_x)

    # 将旋转后的图像粘贴到结果图像上
    result[paste_y:paste_y+paste_height, paste_x:paste_x+paste_width] = resized_image[:paste_height, :paste_width]
    
    template_image = cv2.cvtColor(template_image, cv2.COLOR_BGRA2RGBA)

    # 将template_image叠加到结果图像上
    if template_image.shape[2] == 4:  # 确保template_image有alpha通道
        alpha = template_image[:, :, 3] / 255.0
        for c in range(0, 3):
            result[:, :, c] = result[:, :, c] * (1 - alpha) + template_image[:, :, c] * alpha

    return result
