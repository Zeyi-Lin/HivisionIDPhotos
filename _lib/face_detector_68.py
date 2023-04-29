"""
@author: cuny
@file: face_detector_68.py
@time: 2022/7/21 14:04
@description: 
整合人脸检测库
"""
import cv2
import dlib
import numpy as np
from .__config import FACE_PREDICTOR_68_PATH


# 定义一个人脸检测错误的错误类
class FaceError(Exception):
    def __init__(self, err):
        super().__init__(err)
        self.err = err

    def __str__(self):
        return self.err


class FaceConfig68(object):
    face_area: list = None  # 一些其他的参数,在本类中实际没啥用
    FACE_POINTS = list(range(17, 68))  # 人脸轮廓点索引
    MOUTH_POINTS = list(range(48, 61))  # 嘴巴点索引
    RIGHT_BROW_POINTS = list(range(17, 22))  # 右眉毛索引
    LEFT_BROW_POINTS = list(range(22, 27))  # 左眉毛索引
    RIGHT_EYE_POINTS = list(range(36, 42))  # 右眼索引
    LEFT_EYE_POINTS = list(range(42, 48))  # 左眼索引
    NOSE_POINTS = list(range(27, 35))  # 鼻子索引
    JAW_POINTS = list(range(0, 17))  # 下巴索引
    LEFT_FACE = list(range(42, 48)) + list(range(22, 27))  # 左半边脸索引
    RIGHT_FACE = list(range(36, 42)) + list(range(17, 22))  # 右半边脸索引
    JAW_END = 17  # 下巴结束点
    FACE_START = 0  # 人脸识别开始
    FACE_END = 68  # 人脸识别结束
    # 下面这个是整张脸的mark点,可以用:
    # for group in self.OVERLAY_POINTS:
    #     cv2.fillConvexPoly(face_mask, cv2.convexHull(dst_matrix[group]), (255, 255, 255))
    # 来形成人脸蒙版
    OVERLAY_POINTS = [
        JAW_POINTS,
        LEFT_FACE,
        RIGHT_FACE
    ]


class FaceDetection68(FaceConfig68):
    """
    人脸68关键点检测主类,当然使用的是dlib开源包
    """
    def __init__(self, model_path: str = None):
        # 初始化,检查并下载模型
        self.model_path = FACE_PREDICTOR_68_PATH if model_path is None else model_path
        self.__detector = None
        self.__predictor = None

    @property
    def detector(self):
        if self.__detector is None:
            self.__detector = dlib.get_frontal_face_detector()  # 获取人脸分类器
        return self.__detector

    @property
    def predictor(self):
        if self.__predictor is None:
            self.__predictor = dlib.shape_predictor(self.model_path)  # 输入模型,构建特征提取器
        return self.__predictor

    @staticmethod
    def draw_face(img: np.ndarray, dets: dlib.rectangles, *args, **kwargs):
        # 画人脸检测框, 为了一些兼容操作我没有设置默认显示,可以在运行完本函数后将返回值进行self.cv_show()
        tmp = img.copy()
        for face in dets:
            # 左上角(x1,y1)，右下角(x2,y2)
            x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()
            # print(x1, y1, x2, y2)
            cv2.rectangle(tmp, (x1, y1), (x2, y2), (0, 255, 0), 2)
        return tmp

    @staticmethod
    def draw_points(img: np.ndarray, landmarks: np.matrix, if_num: int = False):
        """
        画人脸关键点, 为了一些兼容操作我没有设置默认显示,可以在运行完本函数后将返回值进行self.cv_show()
        :param img: 输入的是人脸检测的图,必须是3通道或者灰度图
        :param if_num: 是否在画关键点的同时画上编号
        :param landmarks: 输入的关键点矩阵信息
        """
        tmp = img.copy()
        h, w, c = tmp.shape
        r = int(h / 100) - 2 if h > w else int(w / 100) - 2
        for idx, point in enumerate(landmarks):
            # 68点的坐标
            pos = (point[0, 0], point[0, 1])
            # 利用cv2.circle给每个特征点画一个圈，共68个
            cv2.circle(tmp, pos, r, color=(0, 0, 255), thickness=-1)  # bgr
            if if_num is True:
                # 利用cv2.putText输出1-68
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(tmp, str(idx + 1), pos, font, 0.8, (0, 0, 255), 1, cv2.LINE_AA)
        return tmp

    @staticmethod
    def resize_image_esp(input_image_, esp=2000):
        """
        输入：
        input_path：numpy图片
        esp：限制的最大边长
        """
        # resize函数=>可以让原图压缩到最大边为esp的尺寸(不改变比例)
        width = input_image_.shape[0]

        length = input_image_.shape[1]
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
            im_resize = cv2.resize(input_image_, (length, width), interpolation=cv2.INTER_AREA)
            return im_resize
        else:
            return input_image_

    def facesPoints(self, img: np.ndarray, esp: int = None, det_num: int = 1):
        """
        :param img: 输入的是人脸检测的图,必须是3通道或者灰度图
        :param esp: 如果输入了具体数值,会将图片的最大边长缩放至esp,另一边等比例缩放
        :param det_num: 人脸检测的迭代次数, 采样次数越多,越有利于检测到更多的人脸
        :return
        返回人脸检测框对象dets, 人脸关键点矩阵列表(列表中每个元素为一个人脸的关键点矩阵), 人脸关键点元组列表(列表中每个元素为一个人脸的关键点列表)
        """
        # win = dlib.image_window()
        # win.clear_overlay()
        # win.set_image(img)
        # dlib的人脸检测装置
        if esp is not None:
            img = self.resize_image_esp(input_image_=img, esp=esp)
        dets = self.detector(img, det_num)
        # self.draw_face(img, dets)
        # font_color = "green" if len(dets) == 1 else "red"
        # dg.debug_print("Number of faces detected: {}".format(len(dets)), font_color=font_color)
        landmarkList = []
        pointsList = []
        for d in dets:
            shape = self.predictor(img, d)
            landmark = np.matrix([[p.x, p.y] for p in shape.parts()])
            landmarkList.append(landmark)
            point_list = []
            for p in landmark.tolist():
                point_list.append((p[0], p[1]))
            pointsList.append(point_list)
        # dg.debug_print("Key point detection SUCCESS.", font_color="green")
        return dets, landmarkList, pointsList

    def facePoints(self, img: np.ndarray, esp: int = None, det_num: int = 1):
        """
        本函数与facesPoints大致类似,主要区别在于本函数默认只能返回一个人脸关键点参数
        """
        # win = dlib.image_window()
        # win.clear_overlay()
        # win.set_image(img)
        # dlib的人脸检测装置, 参数1表示对图片进行上采样一次，采样次数越多,越有利于检测到更多的人脸
        if esp is not None:
            img = self.resize_image_esp(input_image_=img, esp=esp)
        dets = self.detector(img, det_num)
        # self.draw_face(img, dets)
        font_color = "green" if len(dets) == 1 else "red"
        # dg.debug_print("Number of faces detected: {}".format(len(dets)), font_color=font_color)
        if font_color == "red":
            # 本检测函数必然只能检测出一张人脸
            raise FaceError("Face detection error!!!")
        d = dets[0]  # 唯一人脸
        shape = self.predictor(img, d)
        landmark = np.matrix([[p.x, p.y] for p in shape.parts()])
        # print("face_landmark:", landmark)  # 打印关键点矩阵
        # shape = predictor(img, )
        # dlib.hit_enter_to_continue()
        # 返回关键点矩阵,关键点,
        point_list = []
        for p in landmark.tolist():
            point_list.append((p[0], p[1]))
        # dg.debug_print("Key point detection SUCCESS.", font_color="green")
        # 最后的一个返回参数只会被计算一次，用于标明脸部框的位置
        # [人脸框左上角纵坐标（top），左上角横坐标（left），人脸框宽度（width），人脸框高度（height）]
        return dets, landmark, point_list
