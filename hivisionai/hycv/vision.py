import cv2
from PIL import Image
import numpy as np
import functools
import time

def calTime(mark):
    """
    一个输出函数时间的装饰器.
    :param mark: str, 可选填, 如果填了就会在print开头加上mark标签。
    """
    if isinstance(mark, str):
        def decorater(func):
            @functools.wraps(func)
            def wrapper(*args, **kw):
                start_time = time.time()
                return_param = func(*args, **kw)
                print("[Mark-{}] {} 函数花费的时间为 {:.2f}.".format(mark, func.__name__, time.time() - start_time))
                return return_param

            return wrapper

        return decorater
    else:
        func = mark

        @functools.wraps(func)
        def wrapper(*args, **kw):
            start_time = time.time()
            return_param = func(*args, **kw)
            print("{} 函数花费的时间为 {:.2f}.".format(func.__name__, time.time() - start_time))
            return return_param

        return wrapper


def ChangeImageDPI(input_path, output_path, dpi=300):
    """
    改变输入图像的dpi.
    input_path: 输入图像路径
    output_path: 输出图像路径
    dpi：打印分辨率
    """
    image = Image.open(input_path)
    image.save(output_path, dpi=(dpi, dpi))
    # print(1)
    print("Your Image's DPI have been changed. The last DPI = ({},{}) ".format(dpi,dpi))


def IDphotos_cut(x1, y1, x2, y2, img):
    """
    在图片上进行滑动裁剪,输入输出为
    输入：一张图片img,和裁剪框信息(x1,x2,y1,y2)
    输出: 裁剪好的图片,然后裁剪框超出了图像范围,那么将用0矩阵补位
    ------------------------------------
    x:裁剪框左上的横坐标
    y:裁剪框左上的纵坐标
    x2:裁剪框右下的横坐标
    y2:裁剪框右下的纵坐标
    crop_size:裁剪框大小
    img:裁剪图像（numpy.array）
    output_path:裁剪图片的输出路径
    ------------------------------------
    """

    crop_size = (y2-y1, x2-x1)
    """
    ------------------------------------
    temp_x_1:裁剪框左边超出图像部分
    temp_y_1:裁剪框上边超出图像部分
    temp_x_2:裁剪框右边超出图像部分
    temp_y_2:裁剪框下边超出图像部分
    ------------------------------------
    """
    temp_x_1 = 0
    temp_y_1 = 0
    temp_x_2 = 0
    temp_y_2 = 0

    if y1 < 0:
        temp_y_1 = abs(y1)
        y1 = 0
    if y2 > img.shape[0]:
        temp_y_2 = y2
        y2 = img.shape[0]
        temp_y_2 = temp_y_2 - y2

    if x1 < 0:
        temp_x_1 = abs(x1)
        x1 = 0
    if x2 > img.shape[1]:
        temp_x_2 = x2
        x2 = img.shape[1]
        temp_x_2 = temp_x_2 - x2

    # 生成一张全透明背景
    print("crop_size:", crop_size)
    background_bgr = np.full((crop_size[0], crop_size[1]), 255, dtype=np.uint8)
    background_a = np.full((crop_size[0], crop_size[1]), 0, dtype=np.uint8)
    background = cv2.merge((background_bgr, background_bgr, background_bgr, background_a))

    background[temp_y_1: crop_size[0] - temp_y_2, temp_x_1: crop_size[1] - temp_x_2] = img[y1:y2, x1:x2]

    return background


def resize_image_esp(input_image, esp=2000):
    """
    输入：
    input_path：numpy图片
    esp：限制的最大边长
    """
    # resize函数=>可以让原图压缩到最大边为esp的尺寸(不改变比例)
    width = input_image.shape[0]

    length = input_image.shape[1]
    max_num = max(width, length)

    if max_num > esp:
        print("Image resizing...")
        if width == max_num:
            length = int((esp / width) * length)
            width = esp

        else:
            width = int((esp / length) * width)
            length = esp
        print(length, width)
        im_resize = cv2.resize(input_image, (length, width), interpolation=cv2.INTER_AREA)
        return im_resize
    else:
        return input_image


def resize_image_by_min(input_image, esp=600):
    """
    将图像缩放为最短边至少为esp的图像。
    :param input_image: 输入图像（OpenCV矩阵）
    :param esp: 缩放后的最短边长
    :return: 缩放后的图像，缩放倍率
    """
    height, width = input_image.shape[0], input_image.shape[1]
    min_border = min(height, width)
    if min_border < esp:
        if height >= width:
            new_width = esp
            new_height = height * esp // width
        else:
            new_height = esp
            new_width = width * esp // height

        return cv2.resize(input_image, (new_width, new_height), interpolation=cv2.INTER_AREA), new_height / height

    else:
        return input_image, 1


def detect_distance(value, crop_heigh, max=0.06, min=0.04):
    """
    检测人头顶与照片顶部的距离是否在适当范围内。
    输入：与顶部的差值
    输出：(status, move_value)
    status=0 不动
    status=1 人脸应向上移动（裁剪框向下移动）
    status-2 人脸应向下移动（裁剪框向上移动）
    ---------------------------------------
    value：头顶与照片顶部的距离·
    crop_heigh: 裁剪框的高度
    max: 距离的最大值
    min: 距离的最小值
    ---------------------------------------
    """
    value = value / crop_heigh  # 头顶往上的像素占图像的比例
    if min <= value <= max:
        return 0, 0
    elif value > max:
        # 头顶往上的像素比例高于max
        move_value = value - max
        move_value = int(move_value * crop_heigh)
        # print("上移{}".format(move_value))
        return 1, move_value
    else:
        # 头顶往上的像素比例低于min
        move_value = min - value
        move_value = int(move_value * crop_heigh)
        # print("下移{}".format(move_value))
        return -1, move_value


def draw_picture_dots(image, dots, pen_size=10, pen_color=(0, 0, 255)):
    """
    给一张照片上绘制点。
    image: Opencv图像矩阵
    dots: 一堆点,形如[(100,100),(150,100)]
    pen_size: 画笔的大小
    pen_color: 画笔的颜色
    """
    if isinstance(dots, dict):
        dots = [v for u, v in dots.items()]
    image = image.copy()
    for x, y in dots:
        cv2.circle(image, (int(x), int(y)), pen_size, pen_color, -1)
    return image


def draw_picture_rectangle(image, bbox, pen_size=2, pen_color=(0, 0, 255)):
    image = image.copy()
    x1 = int(bbox[0])
    y1 = int(bbox[1])
    x2 = int(bbox[2])
    y2 = int(bbox[3])
    cv2.rectangle(image, (x1,y1), (x2, y2), pen_color, pen_size)
    return image


def generate_gradient(start_color, width, height, mode="updown"):
    # 定义背景颜色
    end_color = (255, 255, 255) # 白色

    # 创建一个空白图像
    r_out = np.zeros((height, width), dtype=int)
    g_out = np.zeros((height, width), dtype=int)
    b_out = np.zeros((height, width), dtype=int)

    if mode == "updown":
        # 生成上下渐变色
        for y in range(height):
            r = int((y / height) * end_color[0] + ((height - y) / height) * start_color[0])
            g = int((y / height) * end_color[1] + ((height - y) / height) * start_color[1])
            b = int((y / height) * end_color[2] + ((height - y) / height) * start_color[2])
            r_out[y, :] = r
            g_out[y, :] = g
            b_out[y, :] = b

    else:
        # 生成中心渐变色
        img = np.zeros((height, width, 3))
        # 定义椭圆中心和半径
        center = (width//2, height//2)
        end_axies = max(height, width)
        # 定义渐变色
        end_color = (255, 255, 255)
        # 绘制椭圆
        for y in range(end_axies):
            axes = (end_axies - y, end_axies - y)
            r = int((y / end_axies) * end_color[0] + ((end_axies - y) / end_axies) * start_color[0])
            g = int((y / end_axies) * end_color[1] + ((end_axies - y) / end_axies) * start_color[1])
            b = int((y / end_axies) * end_color[2] + ((end_axies - y) / end_axies) * start_color[2])

            cv2.ellipse(img, center, axes, 0, 0, 360, (b, g, r), -1)
        b_out, g_out, r_out = cv2.split(np.uint64(img))

    return r_out, g_out, b_out


def add_background(input_image, bgr=(0, 0, 0), mode="pure_color"):
    """
    本函数的功能为为透明图像加上背景。
    :param input_image: numpy.array(4 channels), 透明图像
    :param bgr: tuple, 合成纯色底时的BGR值
    :param new_background: numpy.array(3 channels)，合成自定义图像底时的背景图
    :return: output: 合成好的输出图像
    """
    height, width = input_image.shape[0], input_image.shape[1]
    b, g, r, a = cv2.split(input_image)
    a_cal = a / 255
    if mode == "pure_color":
        # 纯色填充
        b2 = np.full([height, width], bgr[0], dtype=int)
        g2 = np.full([height, width], bgr[1], dtype=int)
        r2 = np.full([height, width], bgr[2], dtype=int)
    elif mode == "updown_gradient":
        b2, g2, r2 = generate_gradient(bgr, width, height, mode="updown")
    else:
        b2, g2, r2 = generate_gradient(bgr, width, height, mode="center")

    output = cv2.merge(((b - b2) * a_cal + b2, (g - g2) * a_cal + g2, (r - r2) * a_cal + r2))

    return output


def rotate_bound(image, angle):
    """
    一个旋转函数，输入一张图片和一个旋转角，可以实现不损失图像信息的旋转。
    - image: numpy.array(3 channels)
    - angle: 旋转角（度）
    """
    (h, w) = image.shape[:2]
    (cX, cY) = (w / 2, h / 2)

    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    return cv2.warpAffine(image, M, (nW, nH)), cos, sin


def rotate_bound_4channels(image, a, angle):
    """
    【rotate_bound_4channels的4通道版本】
    一个旋转函数，输入一张图片和一个旋转角，可以实现不损失图像信息的旋转。
    Inputs:
        - image: numpy.array(3 channels), 输入图像
        - a: numpy.array(1 channels), 输入图像的A矩阵
        - angle: 旋转角（度）
    Returns:
        - input_image: numpy.array(3 channels), 对image进行旋转后的图像
        - result_image: numpy.array(4 channels), 旋转且透明的图像
        - cos: float, 旋转角的余弦值
        - sin: float, 旋转角的正弦值
    """
    input_image, cos, sin = rotate_bound(image, angle)
    new_a, _, _ = rotate_bound(a, angle)  # 对做matte旋转，以便之后merge
    b, g, r = cv2.split(input_image)
    result_image = cv2.merge((b, g, r, new_a))  # 得到抠图结果图的无损旋转结果

    return input_image, result_image, cos, sin


def cover_image(image, background, x, y, mode=1):
    """
    mode = 1: directly cover
    mode = 2: cv2.add
    mode = 3: bgra cover
    """
    image = image.copy()
    background = background.copy()
    height1, width1 = background.shape[0], background.shape[1]
    height2, width2 = image.shape[0], image.shape[1]
    wuqiong_bg_y = height1 + 1
    wuqiong_bg_x = width1 + 1
    wuqiong_img_y = height2 + 1
    wuqiong_img_x = width2 + 1

    def cover_mode(image, background, imgy1=0, imgy2=-1, imgx1=0, imgx2=-1, bgy1=0, bgy2=-1, bgx1=0, bgx2=-1, mode=1):
        if mode == 1:
            background[bgy1:bgy2, bgx1:bgx2] = image[imgy1:imgy2, imgx1:imgx2]
        elif mode == 2:
            background[bgy1:bgy2, bgx1:bgx2] = cv2.add(background[bgy1:bgy2, bgx1:bgx2], image[imgy1:imgy2, imgx1:imgx2])
        elif mode == 3:
            b, g, r, a = cv2.split(image[imgy1:imgy2, imgx1:imgx2])
            b2, g2, r2, a2 = cv2.split(background[bgy1:bgy2, bgx1:bgx2])
            background[bgy1:bgy2, bgx1:bgx2, 0] = b * (a / 255) + b2 * (1 - a / 255)
            background[bgy1:bgy2, bgx1:bgx2, 1] = g * (a / 255) + g2 * (1 - a / 255)
            background[bgy1:bgy2, bgx1:bgx2, 2] = r * (a / 255) + r2 * (1 - a / 255)
            background[bgy1:bgy2, bgx1:bgx2, 3] = cv2.add(a, a2)

        return background

    if x >= 0 and y >= 0:
        x2 = x + width2
        y2 = y + height2

        if x2 <= width1 and y2 <= height1:
            background = cover_mode(image, background,0,wuqiong_img_y,0,wuqiong_img_x,y,y2,x,x2,mode)

        elif x2 > width1 and y2 <= height1:
            # background[y:y2, x:] = image[:, :width1 - x]
            background = cover_mode(image, background, 0, wuqiong_img_y, 0, width1-x, y, y2, x, wuqiong_bg_x,mode)

        elif x2 <= width1 and y2 > height1:
            # background[y:, x:x2] = image[:height1 - y, :]
            background = cover_mode(image, background, 0, height1-y, 0, wuqiong_img_x, y, wuqiong_bg_y, x, x2,mode)
        else:
            # background[y:, x:] = image[:height1 - y, :width1 - x]
            background = cover_mode(image, background, 0, height1-y, 0, width1-x, y, wuqiong_bg_y, x, wuqiong_bg_x,mode)

    elif x < 0 and y >= 0:
        x2 = x + width2
        y2 = y + height2

        if x2 <= width1 and y2 <= height1:
            # background[y:y2, :x + width2] = image[:, abs(x):]
            background = cover_mode(image, background, 0, wuqiong_img_y, abs(x), wuqiong_img_x, y, y2, 0, x+width2,mode)
        elif x2 > width1 and y2 <= height1:
            background = cover_mode(image, background, 0, wuqiong_img_y, abs(x), width1+abs(x), y, y2, 0, wuqiong_bg_x,mode)
        elif x2 <= 0:
            pass
        elif x2 <= width1 and y2 > height1:
            background = cover_mode(image, background, 0, height1-y, abs(x), wuqiong_img_x, y, wuqiong_bg_y, 0, x2, mode)
        else:
            # background[y:, :] = image[:height1 - y, abs(x):width1 + abs(x)]
            background = cover_mode(image, background, 0, height1-y, abs(x), width1+abs(x), y, wuqiong_bg_y, 0, wuqiong_bg_x,mode)

    elif x >= 0 and y < 0:
        x2 = x + width2
        y2 = y + height2
        if y2 <= 0:
            pass
        if x2 <= width1 and y2 <= height1:
            # background[:y2, x:x2] = image[abs(y):, :]
            background = cover_mode(image, background, abs(y), wuqiong_img_y, 0, wuqiong_img_x, 0, y2, x, x2,mode)
        elif x2 > width1 and y2 <= height1:
            # background[:y2, x:] = image[abs(y):, :width1 - x]
            background = cover_mode(image, background, abs(y), wuqiong_img_y, 0, width1-x, 0, y2, x, wuqiong_bg_x,mode)
        elif x2 <= width1 and y2 > height1:
            # background[:, x:x2] = image[abs(y):height1 + abs(y), :]
            background = cover_mode(image, background, abs(y), height1+abs(y), 0, wuqiong_img_x, 0, wuqiong_bg_y, x, x2,mode)
        else:
            # background[:, x:] = image[abs(y):height1 + abs(y), :width1 - abs(x)]
            background = cover_mode(image, background, abs(y), height1+abs(y), 0, width1-abs(x), 0, wuqiong_bg_x, x, wuqiong_bg_x,mode)

    else:
        x2 = x + width2
        y2 = y + height2
        if y2 <= 0 or x2 <= 0:
            pass
        if x2 <= width1 and y2 <= height1:
            # background[:y2, :x2] = image[abs(y):, abs(x):]
            background = cover_mode(image, background, abs(y), wuqiong_img_y, abs(x), wuqiong_img_x, 0, y2, 0, x2,mode)
        elif x2 > width1 and y2 <= height1:
            # background[:y2, :] = image[abs(y):, abs(x):width1 + abs(x)]
            background = cover_mode(image, background, abs(y), wuqiong_img_y, abs(x), width1+abs(x), 0, y2, 0, wuqiong_bg_x,mode)
        elif x2 <= width1 and y2 > height1:
            # background[:, :x2] = image[abs(y):height1 + abs(y), abs(x):]
            background = cover_mode(image, background, abs(y), height1+abs(y), abs(x), wuqiong_img_x, 0, wuqiong_bg_y, 0, x2,mode)
        else:
            # background[:, :] = image[abs(y):height1 - abs(y), abs(x):width1 + abs(x)]
            background = cover_mode(image, background, abs(y), height1-abs(y), abs(x), width1+abs(x), 0, wuqiong_bg_y, 0, wuqiong_bg_x,mode)

    return background


def image2bgr(input_image):
    if len(input_image.shape) == 2:
        input_image = input_image[:, :, None]
    if input_image.shape[2] == 1:
        result_image = np.repeat(input_image, 3, axis=2)
    elif input_image.shape[2] == 4:
        result_image = input_image[:, :, 0:3]
    else:
        result_image = input_image

    return result_image


if __name__ == "__main__":
    image = cv2.imread("./03.png", -1)
    result_image = add_background(image, bgr=(255, 255, 255))
    cv2.imwrite("test.jpg", result_image)