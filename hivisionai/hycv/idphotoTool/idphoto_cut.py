import cv2
import math
from ..utils import get_box_pro
from ..face_tools import face_detect_mtcnn
from ..vision import IDphotos_cut, detect_distance, resize_image_esp, draw_picture_dots
from ..matting_tools import get_modnet_matting
from .move_image import move
from src.hivisionai.hyTrain.APIs import aliyun_face_detect_api
import numpy as np
import json


def get_max(height, width, d1, d2, d3, d4, rotation_flag):
    if rotation_flag:
        height1 = height
        height2 = height - int(d1.y) # d2
        height3 = int(d4.y) # d3
        height4 = int(d4.y) - int(d1.x)

        width1 = width
        width2 = width - int(d3.x)
        width3 = int(d2.x)
        width4 = int(d2.x) - int(d3.x)

    else:
        height1 = height
        height2 = height - int(d2.y)
        height3 = int(d3.y)
        height4 = int(d3.y) - int(d2.y)

        width1 = width
        width2 = width - int(d1.x)
        width3 = int(d4.x)
        width4 = int(d4.x) - int(d1.x)

    height_list = [height1, height2, height3, height4]
    width_list = [width1, width2, width3, width4]

    background_height = max(height_list)
    status_height = height_list.index(background_height)

    background_width = max(width_list)
    status_width = width_list.index(background_width)

    height_change = 0
    width_change = 0
    height_change2 = 0
    width_change2 = 0
    if status_height == 1 or status_height == 3:
        if rotation_flag:
            height_change = abs(d1.y)
            height_change2 = d1.y
        else:
            height_change = abs(d2.y)
            height_change2 = d2.y

    if status_width == 1 or status_width == 3:
        if rotation_flag:
            width_change = abs(d3.x)
            width_change2 = d3.x
        else:
            width_change = abs(d1.x)
            width_change2 = d1.x

    return background_height, status_height, background_width, status_width, height_change, width_change,\
           height_change2, width_change2

class LinearFunction_TwoDots(object):
    """
    通过两个坐标点构建线性函数
    """
    def __init__(self, dot1, dot2):
        self.d1 = dot1
        self.d2 = dot2
        self.k = (self.d2.y - self.d1.y) / (self.d2.x - self.d1.x)
        self.b = self.d2.y - self.k * self.d2.x

    def forward(self, input, mode="x"):
        if mode == "x":
            return self.k * input + self.b
        elif mode == "y":
            return (input - self.b) / self.k

    def forward_x(self, x):
        return self.k * x + self.b

    def forward_y(self, y):
        return (y - self.b) / self.k

class Coordinate(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "({}, {})".format(self.x, self.y)

def IDphotos_create(input_image, size=(413, 295), head_measure_ratio=0.2, head_height_ratio=0.45,
                    checkpoint_path="checkpoint/ModNet1.0.onnx", align=True):
    """
    input_path: 输入图像路径
    output_path: 输出图像路径
    size: 裁剪尺寸,格式应该如(413,295),竖直距离在前,水平距离在后
    head_measure_ratio: 人头面积占照片面积的head_ratio
    head_height_ratio: 人头中心处于照片从上到下的head_height
    align: 是否进行人脸矫正
    """

    input_image = resize_image_esp(input_image, 2000)  # 将输入图片压缩到最大边长为2000
    # cv2.imwrite("./temp_input_image.jpg", input_image)
    origin_png_image = get_modnet_matting(input_image, checkpoint_path)
    # cv2.imwrite("./test_image/origin_png_image.png", origin_png_image)
    _, _, _, a = cv2.split(origin_png_image)
    width_length_ratio = size[0]/size[1]  # 长宽比
    rotation = aliyun_face_detect_api("./temp_input_image.jpg")

    # 如果旋转角过小，则不进行矫正
    if abs(rotation) < 0.025:
        align=False

    if align:
        print("开始align")
        if rotation > 0:
            rotation_flag = 0  # 逆时针旋转
        else:
            rotation_flag = 1  # 顺时针旋转
        width, height, channels = input_image.shape

        p_list = [(0, 0), (0, height), (width, 0), (width, height)]
        rotate_list = []
        rotate = cv2.getRotationMatrix2D((height * 0.5, width * 0.5), rotation, 0.75)
        for p in p_list:
            p_m = np.array([[p[1]], [p[0]], [1]])
            rotate_list.append(np.dot(rotate[:2], p_m))
        # print("旋转角的四个顶点", rotate_list)

        input_image = cv2.warpAffine(input_image, rotate, (height, width), flags=cv2.INTER_AREA)
        new_a = cv2.warpAffine(a, rotate, (height, width), flags=cv2.INTER_AREA)
        # cv2.imwrite("./test_image/rotation.jpg", input_image)

        # ===================== 开始人脸检测 ===================== #
        faces, _ = face_detect_mtcnn(input_image, filter=True)
        face_num = len(faces)
        print("检测到的人脸数目为:", len(faces))
        # ===================== 人脸检测结束 ===================== #

        if face_num == 1:
            face_rect = faces[0]
            x, y = face_rect[0], face_rect[1]
            w, h = face_rect[2] - x + 1, face_rect[3] - y + 1
        elif face_num == 0:
            print("无人脸，返回0!!!")
            return 0
        else:
            print("太多人脸，返回2!!!")
            return 2

        d1, d2, d3, d4 = rotate_list[0], rotate_list[1], rotate_list[2], rotate_list[3]
        d1 = Coordinate(int(d1[0]), int(d1[1]))
        d2 = Coordinate(int(d2[0]), int(d2[1]))
        d3 = Coordinate(int(d3[0]), int(d3[1]))
        d4 = Coordinate(int(d4[0]), int(d4[1]))
        print("d1:", d1)
        print("d2:", d2)
        print("d3:", d3)
        print("d4:", d4)

        background_height, status_height, background_width, status_width,\
            height_change, width_change, height_change2, width_change2 = get_max(width, height, d1, d2, d3, d4, rotation_flag)

        print("background_height:", background_height)
        print("background_width:", background_width)
        print("status_height:", status_height)
        print("status_width:", status_width)
        print("height_change:", height_change)
        print("width_change:", width_change)

        background = np.zeros([background_height, background_width, 3])
        background_a = np.zeros([background_height, background_width])

        background[height_change:height_change+width, width_change:width_change+height] = input_image
        background_a[height_change:height_change+width, width_change:width_change+height] = new_a
        d1 = Coordinate(int(d1.x)-width_change2, int(d1.y)-height_change2)
        d2 = Coordinate(int(d2.x)-width_change2, int(d2.y)-height_change2)
        d3 = Coordinate(int(d3.x)-width_change2, int(d3.y)-height_change2)
        d4 = Coordinate(int(d4.x)-width_change2, int(d4.y)-height_change2)
        print("d1:", d1)
        print("d2:", d2)
        print("d3:", d3)
        print("d4:", d4)

        if rotation_flag:
            f13 = LinearFunction_TwoDots(d1, d3)
            d5 = Coordinate(max(0, d3.x), f13.forward_x(max(0, d3.x)))
            print("d5:", d5)

            f42 = LinearFunction_TwoDots(d4, d2)
            d7 = Coordinate(f42.forward_y(d5.y), d5.y)
            print("d7", d7)

            background_draw = draw_picture_dots(background, dots=[(d1.x, d1.y),
                                                                  (d2.x, d2.y),
                                                                  (d3.x, d3.y),
                                                                  (d4.x, d4.y),
                                                                  (d5.x, d5.y),
                                                                  (d7.x, d7.y)])
            # cv2.imwrite("./test_image/rotation_background.jpg", background_draw)

            if x<d5.x or x+w>d7.x:
                print("return 6")
                return 6

            background_output = background[:int(d5.y), int(d5.x):int(d7.x)]
            background_a_output = background_a[:int(d5.y), int(d5.x):int(d7.x)]
            # cv2.imwrite("./test_image/rotation_background_cut.jpg", background_output)

        else:
            f34 = LinearFunction_TwoDots(d3, d4)
            d5 = Coordinate(min(width_change+height, d4.x), f34.forward_x(min(width_change+height, d4.x)))
            print("d5:", d5)

            f13 = LinearFunction_TwoDots(d1, d3)
            d7 = Coordinate(f13.forward_y(d5.y), d5.y)
            print("d7", d7)

            if x<d7.x or x+w>d5.x:
                print("return 6")
                return 6

            background_draw = draw_picture_dots(background, dots=[(d1.x, d1.y),
                                                                  (d2.x, d2.y),
                                                                  (d3.x, d3.y),
                                                                  (d4.x, d4.y),
                                                                  (d5.x, d5.y),
                                                                  (d7.x, d7.y)])

            # cv2.imwrite("./test_image/rotation_background.jpg", background_draw)

            background_output = background[:int(d5.y), int(d7.x):int(d5.x)]
            background_a_output = background_a[:int(d5.y), int(d7.x):int(d5.x)]
            # cv2.imwrite("./test_image/rotation_background_cut.jpg", background_output)

        input_image = np.uint8(background_output)
        b, g, r = cv2.split(input_image)
        origin_png_image = cv2.merge((b, g, r, np.uint8(background_a_output)))

    # ===================== 开始人脸检测 ===================== #
    width, length = input_image.shape[0], input_image.shape[1]
    faces, _ = face_detect_mtcnn(input_image, filter=True)
    face_num = len(faces)
    print("检测到的人脸数目为:", len(faces))
    # ===================== 人脸检测结束 ===================== #

    if face_num == 1:

        face_rect = faces[0]
        x, y = face_rect[0], face_rect[1]
        w, h = face_rect[2] - x + 1, face_rect[3] - y + 1

        # x,y,w,h代表人脸框的左上角坐标和宽高

        # 检测头顶下方空隙,如果头顶下方空隙过小,则拒绝
        if y+h >= 0.85*width:
            # print("face bottom too short! y+h={} width={}".format(y+h, width))
            print("在人脸下方的空间太少，返回值3!!!")
            return 3

        # 第一次裁剪
        # 确定裁剪的基本参数
        face_center = (x+w/2, y+h/2)  # 面部中心坐标
        face_measure = w*h  # 面部面积
        crop_measure = face_measure/head_measure_ratio  # 裁剪框面积：为面部面积的5倍
        resize_ratio = crop_measure/(size[0]*size[1])  # 裁剪框缩放率(以输入尺寸为标准)
        resize_ratio_single = math.sqrt(resize_ratio)
        crop_size = (int(size[0]*resize_ratio_single), int(size[1]*resize_ratio_single))  # 裁剪框大小
        print("crop_size:", crop_size)

        # 裁剪规则：x1和y1为裁剪的起始坐标,x2和y2为裁剪的最终坐标
        # y的确定由人脸中心在照片的45%位置决定
        x1 = int(face_center[0]-crop_size[1]/2)
        y1 = int(face_center[1]-crop_size[0]*head_height_ratio)
        y2 = y1+crop_size[0]
        x2 = x1+crop_size[1]

        # 对原图进行抠图,得到透明图img
        print("开始进行抠图")
        # origin_png_image => 对原图的抠图结果
        # cut_image => 第一次裁剪后的图片
        # result_image => 第二次裁剪后的图片/输出图片
        # origin_png_image = get_human_matting(input_image, get_file_dir(checkpoint_path))

        cut_image = IDphotos_cut(x1, y1, x2, y2, origin_png_image)
        # cv2.imwrite("./temp.png", cut_image)
        # 对裁剪得到的图片temp_path,我们将image=temp_path resize为裁剪框大小,这样方便进行后续计算
        cut_image = cv2.resize(cut_image, (crop_size[1], crop_size[0]))
        y_top, y_bottom, x_left, x_right = get_box_pro(cut_image, model=2)  # 得到透明图中人像的上下左右距离信息
        print("y_top:{}, y_bottom:{}, x_left:{}, x_right:{}".format(y_top, y_bottom, x_left, x_right))

        # 判断左右是否有间隙
        if x_left > 0 or x_right > 0:
            # 左右有空隙, 我们需要减掉它
            print("左右有空隙!")
            status_left_right = 1
            cut_value_top = int(((x_left + x_right) * width_length_ratio) / 2)  # 减去左右,为了保持比例,上下也要相应减少cut_value_top
            print("cut_value_top:", cut_value_top)

        else:
            # 左右没有空隙, 则不管
            status_left_right = 0
            cut_value_top = 0
            print("cut_value_top:", cut_value_top)

        # 检测人头顶与照片的顶部是否在合适的距离内
        print("y_top:", y_top)
        status_top, move_value = detect_distance(y_top-int((x_left+x_right)*width_length_ratio/2), crop_size[0])
        # status=0 => 距离合适, 无需移动
        # status=1 => 距离过大, 人像应向上移动
        # status=2 => 距离过小, 人像应向下移动
        # move_value => 上下移动的距离
        print("status_top:", status_top)
        print("move_value:", move_value)

        # 开始第二次裁剪
        if status_top == 0:
        # 如果上下距离合适,则无需移动
            if status_left_right:
                # 如果左右有空隙,则需要用到cut_value_top
                result_image = IDphotos_cut(x1 + x_left,
                             y1 + cut_value_top,
                             x2 - x_right,
                             y2 - cut_value_top,
                             origin_png_image)

            else:
                # 如果左右没有空隙,那么则无需改动
                result_image = cut_image

        elif status_top == 1:
        # 如果头顶离照片顶部距离过大,需要人像向上移动,则需要用到move_value
            if status_left_right:
                # 左右存在距离,则需要cut_value_top
                result_image = IDphotos_cut(x1 + x_left,
                             y1 + cut_value_top + move_value,
                             x2 - x_right,
                             y2 - cut_value_top + move_value,
                             origin_png_image)
            else:
                # 左右不存在距离
                result_image = IDphotos_cut(x1 + x_left,
                             y1 + move_value,
                             x2 - x_right,
                             y2 + move_value,
                             origin_png_image)

        else:
            # 如果头顶离照片顶部距离过小,则需要人像向下移动,则需要用到move_value
            if status_left_right:
                # 左右存在距离,则需要cut_value_top
                result_image = IDphotos_cut(x1 + x_left,
                             y1 + cut_value_top - move_value,
                             x2 - x_right,
                             y2 - cut_value_top - move_value,
                             origin_png_image)
            else:
                # 左右不存在距离
                result_image = IDphotos_cut(x1 + x_left,
                             y1 - move_value,
                             x2 - x_right,
                             y2 - move_value,
                             origin_png_image)

        # 调节头顶位置————防止底部空一块儿
        result_image = move(result_image)

        # 高清保存
        # cv2.imwrite(output_path.replace(".png", "_HD.png"), result_image)

        # 普清保存
        result_image2 = cv2.resize(result_image, (size[1], size[0]), interpolation=cv2.INTER_AREA)
        # cv2.imwrite("./output_image.png", result_image)
        print("完成.返回1")
        return 1, result_image, result_image2

    elif face_num == 0:
        print("无人脸，返回0!!!")
        return 0
    else:
        print("太多人脸，返回2!!!")
        return 2


if __name__ == "__main__":
    with open("./Setting.json") as json_file:
        # file_list = get_filedir_filelist("./input_image")
        setting = json.load(json_file)
        filedir = "../IDPhotos/input_image/linzeyi.jpg"
        file_list = [filedir]
        for filedir in file_list:
            print(filedir)
            # try:
            status_id, result_image, result_image2 = IDphotos_create(cv2.imread(filedir),
                                    size=(setting["size_height"], setting["size_width"]),
                                    head_height_ratio=setting["head_height_ratio"],
                                    head_measure_ratio=setting["head_measure_ratio"],
                                    checkpoint_path=setting["checkpoint_path"],
                                    align=True)
            # cv2.imwrite("./result_image.png", result_image)

            if status_id == 1:
                print("处理完毕!")
            elif status_id == 0:
                print("没有人脸！请重新上传有人脸的照片.")
            elif status_id == 2:
                print("人脸不只一张！请重新上传单独人脸的照片.")
            elif status_id == 3:
                print("人头下方空隙不足！")
            elif status_id == 4:
                print("此照片不能制作该规格！")
            # except Exception as e:
            #     print(e)