import numpy as np
import cv2
import functools
import time
from hivisionai.hycv.matting_tools import read_modnet_image


def calTime(mark):
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


def standard_photo_resize(input_image: np.array, size):
    """
    input_image: 输入图像,即高清照
    size: 标准照的尺寸
    """
    resize_ratio = input_image.shape[0] / size[0]
    resize_item = int(round(input_image.shape[0] / size[0]))
    if resize_ratio >= 2:
        for i in range(resize_item - 1):
            if i == 0:
                result_image = cv2.resize(input_image,
                                          (size[1] * (resize_item - i - 1), size[0] * (resize_item - i - 1)),
                                          interpolation=cv2.INTER_AREA)
            else:
                result_image = cv2.resize(result_image,
                                          (size[1] * (resize_item - i - 1), size[0] * (resize_item - i - 1)),
                                          interpolation=cv2.INTER_AREA)
    else:
        result_image = cv2.resize(input_image, (size[1], size[0]), interpolation=cv2.INTER_AREA)

    return result_image


def hollowOutFix(src: np.ndarray) -> np.ndarray:
    b, g, r, a = cv2.split(src)
    src_bgr = cv2.merge((b, g, r))
    # -----------padding---------- #
    add_area = np.zeros((10, a.shape[1]), np.uint8)
    a = np.vstack((add_area, a, add_area))
    add_area = np.zeros((a.shape[0], 10), np.uint8)
    a = np.hstack((add_area, a, add_area))
    # -------------end------------ #
    _, a_threshold = cv2.threshold(a, 127, 255, 0)
    a_erode = cv2.erode(a_threshold, kernel=cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)), iterations=3)
    contours, hierarchy = cv2.findContours(a_erode, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contours = [x for x in contours]
    # contours = np.squeeze(contours)
    contours.sort(key=lambda c: cv2.contourArea(c), reverse=True)
    a_contour = cv2.drawContours(np.zeros(a.shape, np.uint8), contours[0], -1, 255, 2)
    # a_base = a_contour[1:-1, 1:-1]
    h, w = a.shape[:2]
    mask = np.zeros([h + 2, w + 2], np.uint8)  # mask必须行和列都加2，且必须为uint8单通道阵列
    cv2.floodFill(a_contour, mask=mask, seedPoint=(0, 0), newVal=255)
    a = cv2.add(a, 255 - a_contour)
    return cv2.merge((src_bgr, a[10:-10, 10:-10]))


def resize_image_by_min(input_image, esp=600):
    """
    将图像缩放为最短边至少为600的图像。
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


def rotate_bound(image, angle):
    """
    一个旋转函数，输入一张图片和一个旋转角，可以实现不损失图像信息的旋转。
    """
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w / 2, h / 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH)), cos, sin


def rotate_bound_4channels(image, a, angle):
    """
    一个旋转函数，输入一张图片和一个旋转角，可以实现不损失图像信息的旋转。
    """
    input_image, cos, sin = rotate_bound(image, angle)
    new_a, _, _ = rotate_bound(a, angle)  # 对做matte旋转，以便之后merge
    b, g, r = cv2.split(input_image)
    result_image = cv2.merge((b, g, r, new_a))  # 得到抠图结果图的无损旋转结果

    # perform the actual rotation and return the image
    return input_image, result_image, cos, sin


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
    dots = list(dots)
    for dot in dots:
        # print("dot: ", dot)
        x = dot[0]
        y = dot[1]
        cv2.circle(image, (int(x), int(y)), pen_size, pen_color, -1)
    return image


def get_modnet_matting(input_image, sess, ref_size=512):
    """
    使用modnet模型对图像进行抠图处理。
    :param input_image: 输入图像（opencv矩阵）
    :param sess: onnxruntime推理主体
    :param ref_size: 缩放参数
    :return: 抠图后的图像
    """
    input_name = sess.get_inputs()[0].name
    output_name = sess.get_outputs()[0].name

    im, width, length = read_modnet_image(input_image=input_image, ref_size=ref_size)

    matte = sess.run([output_name], {input_name: im})
    matte = (matte[0] * 255).astype('uint8')
    matte = np.squeeze(matte)
    mask = cv2.resize(matte, (width, length), interpolation=cv2.INTER_AREA)
    b, g, r = cv2.split(np.uint8(input_image))

    output_image = cv2.merge((b, g, r, mask))

    return output_image


def detect_distance(value, crop_heigh, max=0.06, min=0.04):
    """
    检测人头顶与照片顶部的距离是否在适当范围内。
    输入：与顶部的差值
    输出：(status, move_value)
    status=0 不动
    status=1 人脸应向上移动（裁剪框向下移动）
    status-2 人脸应向下移动（裁剪框向上移动）
    ---------------------------------------
    value：头顶与照片顶部的距离
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
