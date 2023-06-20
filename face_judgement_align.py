import math
import cv2
import numpy as np
from hivisionai.hycv.face_tools import face_detect_mtcnn
from hivisionai.hycv.utils import get_box_pro, CV2Bytes
from hivisionai.hycv.vision import resize_image_esp, IDphotos_cut, add_background, calTime, resize_image_by_min, \
    rotate_bound_4channels
import onnxruntime
from EulerZ import eulerZ
from beautyPlugin import makeBeautiful
from error import IDError
from imageTransform import standard_photo_resize, hollowOutFix, get_modnet_matting, draw_picture_dots, detect_distance
from layoutCreate import generate_layout_photo
from move_image import move

testImages = []


class LinearFunction_TwoDots(object):
    """
    通过两个坐标点构建线性函数
    """

    def __init__(self, dot1, dot2):
        self.d1 = dot1
        self.d2 = dot2
        self.mode = "normal"
        if self.d2.x != self.d1.x:
            self.k = (self.d2.y - self.d1.y) / max((self.d2.x - self.d1.x), 1)
            self.b = self.d2.y - self.k * self.d2.x
        else:
            self.mode = "x=1"

    def forward(self, input_, mode="x"):
        if mode == "x":
            if self.mode == "normal":
                return self.k * input_ + self.b
            else:
                return 0
        elif mode == "y":
            if self.mode == "normal":
                return (input_ - self.b) / self.k
            else:
                return self.d1.x

    def forward_x(self, x):
        if self.mode == "normal":
            return self.k * x + self.b
        else:
            return 0

    def forward_y(self, y):
        if self.mode == "normal":
            return (y - self.b) / self.k
        else:
            return self.d1.x


class Coordinate(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "({}, {})".format(self.x, self.y)


@calTime
def face_number_and_angle_detection(input_image):
    """
    本函数的功能是利用机器学习算法计算图像中人脸的数目与关键点，并通过关键点信息来计算人脸在平面上的旋转角度。
    当前人脸数目!=1时，将raise一个错误信息并终止全部程序。
    Args:
        input_image: numpy.array(3 channels)，用户上传的原图（经过了一些简单的resize）

    Returns:
        - dets: list，人脸定位信息(x1, y1, x2, y2)
        - rotation: int，旋转角度，正数代表逆时针偏离，负数代表顺时针偏离
        - landmark: list，人脸关键点信息
    """

    # face++人脸检测
    # input_image_bytes = CV2Bytes.cv2_byte(input_image, ".jpg")
    # face_num, face_rectangle, landmarks, headpose = megvii_face_detector(input_image_bytes)
    # print(face_rectangle)

    faces, landmarks = face_detect_mtcnn(input_image)
    face_num = len(faces)

    # 排除不合人脸数目要求（必须是1）的照片
    if face_num == 0 or face_num >= 2:
        if face_num == 0:
            status_id_ = "1101"
        else:
            status_id_ = "1102"
        raise IDError(f"人脸检测出错！检测出了{face_num}张人脸", face_num=face_num, status_id=status_id_)

    # 获得人脸定位坐标
    face_rectangle = []
    for iter, (x1, y1, x2, y2, _) in enumerate(faces):
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        face_rectangle.append({'top': x1, 'left': y1, 'width': x2 - x1, 'height': y2 - y1})

    # 获取人脸定位坐标与关键点信息
    dets = face_rectangle[0]
    # landmark = landmarks[0]
    #
    # # 人脸旋转角度计算
    # rotation = eulerZ(landmark)
    # return dets, rotation, landmark
    return dets

@calTime
def image_matting(input_image, params):
    """
    本函数的功能为全局人像抠图。
    Args:
        - input_image: numpy.array(3 channels)，用户原图

    Returns:
        - origin_png_image: numpy.array(4 channels)， 抠好的图
    """

    print("抠图采用本地模型")
    origin_png_image = get_modnet_matting(input_image, sess=params["modnet"]["human_sess"])

    origin_png_image = hollowOutFix(origin_png_image)  # 抠图洞洞修补
    return origin_png_image


@calTime
def rotation_ajust(input_image, rotation, a, IS_DEBUG=False):
    """
    本函数的功能是根据旋转角对原图进行无损旋转，并返回结果图与附带信息。
    Args:
        - input_image: numpy.array(3 channels), 用户上传的原图（经过了一些简单的resize、美颜）
        - rotation: float, 人的五官偏离"端正"形态的旋转角
        - a: numpy.array(1 channel), matting图的matte
        - IS_DEBUG: DEBUG模式开关

    Returns:
        - result_jpg_image: numpy.array(3 channels), 原图旋转的结果图
        - result_png_image: numpy.array(4 channels), matting图旋转的结果图
        - L1: CLassObject, 根据旋转点连线所构造函数
        - L2: ClassObject, 根据旋转点连线所构造函数
        - dotL3: ClassObject, 一个特殊裁切点的坐标
        - clockwise: int, 表示照片是顺时针偏离还是逆时针偏离
        - drawed_dots_image: numpy.array(3 channels), 在result_jpg_image上标定了4个旋转点的结果图，用于DEBUG模式
    """

    # Step1. 数据准备
    rotation = -1 * rotation  # rotation为正数->原图顺时针偏离，为负数->逆时针偏离
    h, w = input_image.copy().shape[:2]

    # Step2. 无损旋转
    result_jpg_image, result_png_image, cos, sin = rotate_bound_4channels(input_image, a, rotation)

    # Step3. 附带信息计算
    nh, nw = result_jpg_image.shape[:2]  # 旋转后的新的长宽
    clockwise = -1 if rotation < 0 else 1  # clockwise代表时针，即1为顺时针，-1为逆时针
    # 如果逆时针偏离：
    if rotation < 0:
        p1 = Coordinate(0, int(w * sin))
        p2 = Coordinate(int(w * cos), 0)
        p3 = Coordinate(nw, int(h * cos))
        p4 = Coordinate(int(h * sin), nh)
        L1 = LinearFunction_TwoDots(p1, p4)
        L2 = LinearFunction_TwoDots(p4, p3)
        dotL3 = Coordinate(int(0.25 * p2.x + 0.75 * p3.x), int(0.25 * p2.y + 0.75 * p3.y))

    # 如果顺时针偏离：
    else:
        p1 = Coordinate(int(h * sin), 0)
        p2 = Coordinate(nw, int(w * sin))
        p3 = Coordinate(int(w * cos), nh)
        p4 = Coordinate(0, int(h * cos))
        L1 = LinearFunction_TwoDots(p4, p3)
        L2 = LinearFunction_TwoDots(p3, p2)
        dotL3 = Coordinate(int(0.75 * p4.x + 0.25 * p1.x), int(0.75 * p4.y + 0.25 * p1.y))

    # Step4. 根据附带信息进行图像绘制（4个旋转点），便于DEBUG模式验证
    drawed_dots_image = draw_picture_dots(result_jpg_image, [(p1.x, p1.y), (p2.x, p2.y), (p3.x, p3.y),
                                                             (p4.x, p4.y), (dotL3.x, dotL3.y)])
    if IS_DEBUG:
        testImages.append(["drawed_dots_image", drawed_dots_image])

    return result_jpg_image, result_png_image, L1, L2, dotL3, clockwise, drawed_dots_image


@calTime
def face_number_detection_mtcnn(input_image):
    """
    本函数的功能是对旋转矫正的结果图进行基于MTCNN模型的人脸检测。
    Args:
        - input_image: numpy.array(3 channels), 旋转矫正(rotation_adjust)的3通道结果图

    Returns:
        - faces: list, 人脸检测的结果，包含人脸位置信息
    """
    # 如果图像的长或宽>1500px，则对图像进行1/2的resize再做MTCNN人脸检测，以加快处理速度
    if max(input_image.shape[0], input_image.shape[1]) >= 1500:
        input_image_resize = cv2.resize(input_image,
                                        (input_image.shape[1] // 2, input_image.shape[0] // 2),
                                        interpolation=cv2.INTER_AREA)
        faces, _ = face_detect_mtcnn(input_image_resize, filter=True)  # MTCNN人脸检测
        # 如果缩放后图像的MTCNN人脸数目检测结果等于1->两次人脸检测结果没有偏差，则对定位数据x2
        if len(faces) == 1:
            for item, param in enumerate(faces[0]):
                faces[0][item] = param * 2
        # 如果两次人脸检测结果有偏差，则默认缩放后图像的MTCNN检测存在误差，则将原图输入再做一次MTCNN（保险措施）
        else:
            faces, _ = face_detect_mtcnn(input_image, filter=True)
    # 如果图像的长或宽<1500px，则直接进行MTCNN检测
    else:
        faces, _ = face_detect_mtcnn(input_image, filter=True)

    return faces


@calTime
def cutting_rect_pan(x1, y1, x2, y2, width, height, L1, L2, L3, clockwise, standard_size):
    """
    本函数的功能是对旋转矫正结果图的裁剪框进行修正 ———— 解决"旋转三角形"现象。
    Args:
        - x1: int, 裁剪框左上角的横坐标
        - y1: int, 裁剪框左上角的纵坐标
        - x2: int, 裁剪框右下角的横坐标
        - y2: int, 裁剪框右下角的纵坐标
        - width: int, 待裁剪图的宽度
        - height:int, 待裁剪图的高度
        - L1: CLassObject, 根据旋转点连线所构造函数
        - L2: CLassObject, 根据旋转点连线所构造函数
        - L3: ClassObject, 一个特殊裁切点的坐标
        - clockwise: int, 旋转时针状态
        - standard_size: tuple, 标准照的尺寸

    Returns:
        - x1: int, 新的裁剪框左上角的横坐标
        - y1: int, 新的裁剪框左上角的纵坐标
        - x2: int, 新的裁剪框右下角的横坐标
        - y2: int, 新的裁剪框右下角的纵坐标
        - x_bias: int, 裁剪框横坐标方向上的计算偏置量
        - y_bias: int, 裁剪框纵坐标方向上的计算偏置量
    """
    # 用于计算的裁剪框坐标x1_cal,x2_cal,y1_cal,y2_cal(如果裁剪框超出了图像范围，则缩小直至在范围内)
    x1_std = x1 if x1 > 0 else 0
    x2_std = x2 if x2 < width else width
    # y1_std = y1 if y1 > 0 else 0
    y2_std = y2 if y2 < height else height

    # 初始化x和y的计算偏置项x_bias和y_bias
    x_bias = 0
    y_bias = 0

    # 如果顺时针偏转
    if clockwise == 1:
        if y2 > L1.forward_x(x1_std):
            y_bias = int(-(y2_std - L1.forward_x(x1_std)))
        if y2 > L2.forward_x(x2_std):
            x_bias = int(-(x2_std - L2.forward_y(y2_std)))
        x2 = x2_std + x_bias
        if x1 < L3.x:
            x1 = L3.x
    # 如果逆时针偏转
    else:
        if y2 > L1.forward_x(x1_std):
            x_bias = int(L1.forward_y(y2_std) - x1_std)
        if y2 > L2.forward_x(x2_std):
            y_bias = int(-(y2_std - L2.forward_x(x2_std)))
        x1 = x1_std + x_bias
        if x2 > L3.x:
            x2 = L3.x

    # 计算裁剪框的y的变化
    y2 = int(y2_std + y_bias)
    new_cut_width = x2 - x1
    new_cut_height = int(new_cut_width / standard_size[1] * standard_size[0])
    y1 = y2 - new_cut_height

    return x1, y1, x2, y2, x_bias, y_bias


@calTime
def idphoto_cutting(faces, head_measure_ratio, standard_size, head_height_ratio, origin_png_image, origin_png_image_pre,
                    rotation_params, align=False, IS_DEBUG=False, top_distance_max=0.12, top_distance_min=0.10):
    """
    本函数的功能为进行证件照的自适应裁剪，自适应依据Setting.json的控制参数，以及输入图像的自身情况。
    Args:
        - faces: list, 人脸位置信息
        - head_measure_ratio: float, 人脸面积与全图面积的期望比值
        - standard_size: tuple, 标准照尺寸, 如(413, 295)
        - head_height_ratio: float, 人脸中心处在全图高度的比例期望值
        - origin_png_image: numpy.array(4 channels), 经过一系列转换后的用户输入图
        - origin_png_image_pre：numpy.array(4 channels)，经过一系列转换（但没有做旋转矫正）的用户输入图
        - rotation_params：旋转参数字典
            - L1: classObject, 来自rotation_ajust的L1线性函数
            - L2: classObject, 来自rotation_ajust的L2线性函数
            - L3: classObject, 来自rotation_ajust的dotL3点
            - clockwise: int, (顺/逆)时针偏差
            - drawed_image: numpy.array, 红点标定4个旋转点的图像
        - align: bool, 是否图像做过旋转矫正
        - IS_DEBUG: DEBUG模式开关
        - top_distance_max: float, 头距离顶部的最大比例
        - top_distance_min: float, 头距离顶部的最小比例

    Returns:
        - result_image_hd: numpy.array(4 channels), 高清照
        - result_image_standard: numpy.array(4 channels), 标准照
        - clothing_params: json, 换装配置参数，便于后续换装功能的使用

    """
    # Step0. 旋转参数准备
    L1 = rotation_params["L1"]
    L2 = rotation_params["L2"]
    L3 = rotation_params["L3"]
    clockwise = rotation_params["clockwise"]
    drawed_image = rotation_params["drawed_image"]

    # Step1. 准备人脸参数
    face_rect = faces[0]
    x, y = face_rect[0], face_rect[1]
    w, h = face_rect[2] - x + 1, face_rect[3] - y + 1
    height, width = origin_png_image.shape[:2]
    width_height_ratio = standard_size[0] / standard_size[1]  # 高宽比

    # Step2. 计算高级参数
    face_center = (x + w / 2, y + h / 2)  # 面部中心坐标
    face_measure = w * h  # 面部面积
    crop_measure = face_measure / head_measure_ratio  # 裁剪框面积：为面部面积的5倍
    resize_ratio = crop_measure / (standard_size[0] * standard_size[1])  # 裁剪框缩放率
    resize_ratio_single = math.sqrt(resize_ratio)  # 长和宽的缩放率（resize_ratio的开方）
    crop_size = (int(standard_size[0] * resize_ratio_single),
                 int(standard_size[1] * resize_ratio_single))  # 裁剪框大小

    # 裁剪框的定位信息
    x1 = int(face_center[0] - crop_size[1] / 2)
    y1 = int(face_center[1] - crop_size[0] * head_height_ratio)
    y2 = y1 + crop_size[0]
    x2 = x1 + crop_size[1]

    # Step3. 对于旋转矫正图片的裁切处理
    # if align:
    #     y_top_pre, _, _, _ = get_box_pro(origin_png_image.astype(np.uint8), model=2,
    #                                      correction_factor=0)  # 获取matting结果图的顶距
    #     # 裁剪参数重新计算，目标是以最小的图像损失来消除"旋转三角形"
    #     x1, y1, x2, y2, x_bias, y_bias = cutting_rect_pan(x1, y1, x2, y2, width, height, L1, L2, L3, clockwise,
    #                                                       standard_size)
    #     # 这里设定一个拒绝判定条件，如果裁剪框切进了人脸检测框的话，就不进行旋转
    #     if y1 > y_top_pre:
    #         y2 = y2 - (y1 - y_top_pre)
    #         y1 = y_top_pre
    #         # 如何遇到裁剪到人脸的情况，则转为不旋转裁切
    #     if x1 > x or x2 < (x + w) or y1 > y or y2 < (y + h):
    #         return idphoto_cutting(faces, head_measure_ratio, standard_size, head_height_ratio, origin_png_image_pre,
    #                                origin_png_image_pre, rotation_params, align=False, IS_DEBUG=False)
    #
    #     if y_bias != 0:
    #         origin_png_image = origin_png_image[:y2, :]
    #     if x_bias > 0:  # 逆时针
    #         origin_png_image = origin_png_image[:, x1:]
    #         if drawed_image is not None and IS_DEBUG:
    #             drawed_x = x1
    #         x = x - x1
    #         x2 = x2 - x1
    #         x1 = 0
    #     else:  # 顺时针
    #         origin_png_image = origin_png_image[:, :x2]
    #
    #     if drawed_image is not None and IS_DEBUG:
    #         drawed_x = drawed_x if x_bias > 0 else 0
    #         drawed_image = draw_picture_dots(drawed_image, [(x1 + drawed_x, y1), (x1 + drawed_x, y2),
    #                                                         (x2 + drawed_x, y1), (x2 + drawed_x, y2)],
    #                                          pen_color=(255, 0, 0))
    #         testImages.append(["drawed_image", drawed_image])

    # Step4. 对照片的第一轮裁剪
    cut_image = IDphotos_cut(x1, y1, x2, y2, origin_png_image)
    cut_image = cv2.resize(cut_image, (crop_size[1], crop_size[0]))
    y_top, y_bottom, x_left, x_right = get_box_pro(cut_image.astype(np.uint8), model=2,
                                                   correction_factor=0)  # 得到cut_image中人像的上下左右距离信息
    if IS_DEBUG:
        testImages.append(["firstCut", cut_image])

    # Step5. 判定cut_image中的人像是否处于合理的位置，若不合理，则处理数据以便之后调整位置
    # 检测人像与裁剪框左边或右边是否存在空隙
    if x_left > 0 or x_right > 0:
        status_left_right = 1
        cut_value_top = int(((x_left + x_right) * width_height_ratio) / 2)  # 减去左右,为了保持比例,上下也要相应减少cut_value_top
    else:
        status_left_right = 0
        cut_value_top = 0

    """
        检测人头顶与照片的顶部是否在合适的距离内：
        - status==0: 距离合适, 无需移动
        - status=1: 距离过大, 人像应向上移动
        - status=2: 距离过小, 人像应向下移动
    """
    status_top, move_value = detect_distance(y_top - cut_value_top, crop_size[0], max=top_distance_max,
                                             min=top_distance_min)

    # Step6. 对照片的第二轮裁剪
    if status_left_right == 0 and status_top == 0:
        result_image = cut_image
    else:
        result_image = IDphotos_cut(x1 + x_left,
                                    y1 + cut_value_top + status_top * move_value,
                                    x2 - x_right,
                                    y2 - cut_value_top + status_top * move_value,
                                    origin_png_image)
    if IS_DEBUG:
        testImages.append(["result_image_pre", result_image])

    # 换装参数准备
    relative_x = x - (x1 + x_left)
    relative_y = y - (y1 + cut_value_top + status_top * move_value)

    # Step7. 当照片底部存在空隙时，下拉至底部
    result_image, y_high = move(result_image.astype(np.uint8))
    relative_y = relative_y + y_high  # 更新换装参数

    # cv2.imwrite("./temp_image.png", result_image)

    # Step8. 标准照与高清照转换
    result_image_standard = standard_photo_resize(result_image, standard_size)
    result_image_hd, resize_ratio_max = resize_image_by_min(result_image, esp=max(600, standard_size[1]))

    # Step9. 参数准备-为换装服务
    clothing_params = {
        "relative_x": relative_x * resize_ratio_max,
        "relative_y": relative_y * resize_ratio_max,
        "w": w * resize_ratio_max,
        "h": h * resize_ratio_max
    }

    return result_image_hd, result_image_standard, clothing_params


@calTime
def debug_mode_process(testImages):
    for item, (text, imageItem) in enumerate(testImages):
        channel = imageItem.shape[2]
        (height, width) = imageItem.shape[:2]
        if channel == 4:
            imageItem = add_background(imageItem, bgr=(255, 255, 255))
            imageItem = np.uint8(imageItem)
        if item == 0:
            testHeight = height
            result_image_test = imageItem
            result_image_test = cv2.putText(result_image_test, text, (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1.0,
                                            (200, 100, 100), 3)
        else:
            imageItem = cv2.resize(imageItem, (int(width * testHeight / height), testHeight))
            imageItem = cv2.putText(imageItem, text, (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1.0, (200, 100, 100),
                                    3)
            result_image_test = cv2.hconcat([result_image_test, imageItem])
        if item == len(testImages) - 1:
            return result_image_test


@calTime("主函数")
def IDphotos_create(input_image,
                    mode="ID",
                    size=(413, 295),
                    head_measure_ratio=0.2,
                    head_height_ratio=0.45,
                    align=False,
                    beauty=True,
                    fd68=None,
                    human_sess=None,
                    IS_DEBUG=False,
                    top_distance_max=0.12,
                    top_distance_min=0.10):
    """
    证件照制作主函数
    Args:
        input_image: 输入图像矩阵
        size: (h, w)
        head_measure_ratio: 头部占比？
        head_height_ratio: 头部高度占比？
        align: 是否进行人脸矫正（roll），默认为True（是）
        fd68: 人脸68关键点检测类，详情参见hycv.FaceDetection68.faceDetection68
        human_sess: 人像抠图模型类，由onnx载入（不与下面两个参数连用）
        oss_image_name: 阿里云api需要的参数，实际上是上传到oss的路径
        user: 阿里云api的accessKey配置对象
        top_distance_max: float, 头距离顶部的最大比例
        top_distance_min: float, 头距离顶部的最小比例
    Returns:
        result_image(高清版), result_image(普清版), api请求日志，
    排版照参数(list)，排版照是否旋转参数，照片尺寸（x， y）
        在函数不出错的情况下，函数会因为一些原因主动抛出异常：
        1. 无人脸（或者只有半张，dlib无法检测出来），抛出IDError异常，内部参数face_num为0
        2. 人脸数量超过1，抛出IDError异常，内部参数face_num为2
        3. 抠图api请求失败，抛出IDError异常，内部参数face_num为-1
    """

    # Step0. 数据准备/图像预处理
    matting_params = {"modnet": {"human_sess": human_sess}}
    rotation_params = {"L1": None, "L2": None, "L3": None, "clockwise": None, "drawed_image": None}
    input_image = resize_image_esp(input_image, 2000)  # 将输入图片resize到最大边长为2000

    # Step1. 人脸检测
    # dets, rotation, landmark = face_number_and_angle_detection(input_image)
    # dets = face_number_and_angle_detection(input_image)

    # Step2. 美颜
    # if beauty:
    #     input_image = makeBeautiful(input_image, landmark, 2, 2, 5, 4)

    # Step3. 抠图
    origin_png_image = image_matting(input_image, matting_params)
    if mode == "只换底":
        return origin_png_image, origin_png_image, None, None, None, None, None, None, 1

    origin_png_image_pre = origin_png_image.copy()  # 备份一下现在抠图结果图，之后在iphoto_cutting函数有用

    # Step4. 旋转矫正
    # 如果旋转角不大于2, 则不做旋转
    # if abs(rotation) <= 2:
    #     align = False
    # # 否则，进行旋转矫正
    # if align:
    #     input_image_candidate, origin_png_image_candidate, L1, L2, L3, clockwise, drawed_image \
    #         = rotation_ajust(input_image, rotation, cv2.split(origin_png_image)[-1], IS_DEBUG=IS_DEBUG)  # 图像旋转
    #
    #     origin_png_image_pre = origin_png_image.copy()
    #     input_image = input_image_candidate.copy()
    #     origin_png_image = origin_png_image_candidate.copy()
    #
    #     rotation_params["L1"] = L1
    #     rotation_params["L2"] = L2
    #     rotation_params["L3"] = L3
    #     rotation_params["clockwise"] = clockwise
    #     rotation_params["drawed_image"] = drawed_image

    # Step5. MTCNN人脸检测
    faces = face_number_detection_mtcnn(input_image)

    # Step6. 证件照自适应裁剪
    face_num = len(faces)
    # 报错MTCNN检测结果不等于1的图片
    if face_num != 1:
        return None, None, None, None, None, None, None, None, 0
    # 符合条件的进入下一环
    else:
        result_image_hd, result_image_standard, clothing_params = \
            idphoto_cutting(faces, head_measure_ratio, size, head_height_ratio, origin_png_image,
                            origin_png_image_pre, rotation_params, align=align, IS_DEBUG=IS_DEBUG,
                            top_distance_max=top_distance_max, top_distance_min=top_distance_min)

    # Step7. 排版照参数获取
    typography_arr, typography_rotate = generate_layout_photo(input_height=size[0], input_width=size[1])

    return result_image_hd, result_image_standard, typography_arr, typography_rotate, \
           clothing_params["relative_x"], clothing_params["relative_y"], clothing_params["w"], clothing_params["h"], 1


if __name__ == "__main__":
    HY_HUMAN_MATTING_WEIGHTS_PATH = "./hivision_modnet.onnx"
    sess = onnxruntime.InferenceSession(HY_HUMAN_MATTING_WEIGHTS_PATH)

    input_image = cv2.imread("test.jpg")

    result_image_hd, result_image_standard, typography_arr, typography_rotate, \
    _, _, _, _, _ = IDphotos_create(input_image,
                                               size=(413, 295),
                                               head_measure_ratio=0.2,
                                               head_height_ratio=0.45,
                                               align=True,
                                               beauty=True,
                                               fd68=None,
                                               human_sess=sess,
                                               oss_image_name="test_tmping.jpg",
                                               user=None,
                                               IS_DEBUG=False,
                                               top_distance_max=0.12,
                                               top_distance_min=0.10)
    cv2.imwrite("result_image_hd.png", result_image_hd)
