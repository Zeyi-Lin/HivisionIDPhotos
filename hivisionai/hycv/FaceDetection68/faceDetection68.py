"""
@author: cuny
@fileName: faceDetection68.py
@create_time: 2022/01/03 下午10:20
@introduce:
人脸68关键点检测主文件,以类的形式封装
"""
from hivisionai.hyService.cloudService import GetConfig
import os
import cv2
import dlib
import numpy as np
local_file = os.path.dirname(__file__)
PREDICTOR_PATH = f"{local_file}/weights/shape_predictor_68_face_landmarks.dat"  # 关键点检测模型路径
MODULE3D_PATH = f"{local_file}/weights/68_points_3D_model.txt"  # 3d的68点配置文件路径

# 定义一个人脸检测错误的错误类
class FaceError(Exception):
    def __init__(self, err):
        super().__init__(err)
        self.err = err
    def __str__(self):
        return self.err

class FaceConfig68(object):
    face_area:list = None  # 一些其他的参数,在本类中实际没啥用
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
    def __init__(self, model_path:str=None, default_download:bool=False, *args, **kwargs):
        # 初始化,检查并下载模型
        self.model_path = PREDICTOR_PATH if model_path is None else model_path
        if not os.path.exists(self.model_path) or default_download:  # 下载配置
            gc = GetConfig()
            gc.load_file(cloud_path="weights/shape_predictor_68_face_landmarks.dat",
                         local_path=self.model_path)
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
    def draw_face(img:np.ndarray, dets:dlib.rectangles, *args, **kwargs):
        # 画人脸检测框, 为了一些兼容操作我没有设置默认显示,可以在运行完本函数后将返回值进行self.cv_show()
        tmp = img.copy()
        for face in dets:
            # 左上角(x1,y1)，右下角(x2,y2)
            x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()
            # print(x1, y1, x2, y2)
            cv2.rectangle(tmp, (x1, y1), (x2, y2), (0, 255, 0), 2)
        return tmp

    @staticmethod
    def draw_points(img:np.ndarray, landmarks:np.matrix, if_num:int=False, *args, **kwargs):
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

    def facesPoints(self, img:np.ndarray, esp:int=None, det_num:int=1,*args, **kwargs):
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

    def facePoints(self, img:np.ndarray, esp:int=None, det_num:int=1, *args, **kwargs):
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
        if font_color=="red":
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

class PoseEstimator68(object):
    """
    Estimate head pose according to the facial landmarks
    本类将实现但输入图的人脸姿态检测
    """
    def __init__(self, img:np.ndarray, params_path:str=None, default_download:bool=False):
        self.params_path = MODULE3D_PATH if params_path is None else params_path
        if not os.path.exists(self.params_path) or default_download:
            gc = GetConfig()
            gc.load_file(cloud_path="weights/68_points_3D_model.txt",
                         local_path=self.params_path)
        h, w, c = img.shape
        self.size = (h, w)
        # 3D model points.
        self.model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye left corner
            (225.0, 170.0, -135.0),      # Right eye right corner
            (-150.0, -150.0, -125.0),    # Mouth left corner
            (150.0, -150.0, -125.0)      # Mouth right corner
        ]) / 4.5
        self.model_points_68 = self._get_full_model_points()

        # Camera internals
        self.focal_length = self.size[1]
        self.camera_center = (self.size[1] / 2, self.size[0] / 2)
        self.camera_matrix = np.array(
            [[self.focal_length, 0, self.camera_center[0]],
             [0, self.focal_length, self.camera_center[1]],
             [0, 0, 1]], dtype="double")

        # Assuming no lens distortion
        self.dist_coeefs = np.zeros((4, 1))

        # Rotation vector and translation vector
        self.r_vec = np.array([[0.01891013], [0.08560084], [-3.14392813]])
        self.t_vec = np.array(
            [[-14.97821226], [-10.62040383], [-2053.03596872]])
        # self.r_vec = None
        # self.t_vec = None

    def _get_full_model_points(self):
        """Get all 68 3D model points from file"""
        raw_value = []
        with open(self.params_path) as file:
            for line in file:
                raw_value.append(line)
        model_points = np.array(raw_value, dtype=np.float32)
        model_points = np.reshape(model_points, (3, -1)).T

        # Transform the model into a front view.
        # model_points[:, 0] *= -1
        model_points[:, 1] *= -1
        model_points[:, 2] *= -1
        return model_points

    def show_3d_model(self):
        from matplotlib import pyplot
        from mpl_toolkits.mplot3d import Axes3D
        fig = pyplot.figure()
        ax = Axes3D(fig)

        x = self.model_points_68[:, 0]
        y = self.model_points_68[:, 1]
        z = self.model_points_68[:, 2]

        ax.scatter(x, y, z)
        ax.axis('auto')
        pyplot.xlabel('x')
        pyplot.ylabel('y')
        pyplot.show()

    def solve_pose(self, image_points):
        """
        Solve pose from image points
        Return (rotation_vector, translation_vector) as pose.
        """
        assert image_points.shape[0] == self.model_points_68.shape[0], "3D points and 2D points should be of same number."
        (_, rotation_vector, translation_vector) = cv2.solvePnP(
            self.model_points, image_points, self.camera_matrix, self.dist_coeefs)

        # (success, rotation_vector, translation_vector) = cv2.solvePnP(
        #     self.model_points,
        #     image_points,
        #     self.camera_matrix,
        #     self.dist_coeefs,
        #     rvec=self.r_vec,
        #     tvec=self.t_vec,
        #     useExtrinsicGuess=True)
        return rotation_vector, translation_vector

    def solve_pose_by_68_points(self, image_points):
        """
        Solve pose from all the 68 image points
        Return (rotation_vector, translation_vector) as pose.
        """
        if self.r_vec is None:
            (_, rotation_vector, translation_vector) = cv2.solvePnP(
                self.model_points_68, image_points, self.camera_matrix, self.dist_coeefs)
            self.r_vec = rotation_vector
            self.t_vec = translation_vector

        (_, rotation_vector, translation_vector) = cv2.solvePnP(
            self.model_points_68,
            image_points,
            self.camera_matrix,
            self.dist_coeefs,
            rvec=self.r_vec,
            tvec=self.t_vec,
            useExtrinsicGuess=True)

        return rotation_vector, translation_vector

    # def draw_annotation_box(self, image, rotation_vector, translation_vector, color=(255, 255, 255), line_width=2):
    #     """Draw a 3D box as annotation of pose"""
    #     point_3d = []
    #     rear_size = 75
    #     rear_depth = 0
    #     point_3d.append((-rear_size, -rear_size, rear_depth))
    #     point_3d.append((-rear_size, rear_size, rear_depth))
    #     point_3d.append((rear_size, rear_size, rear_depth))
    #     point_3d.append((rear_size, -rear_size, rear_depth))
    #     point_3d.append((-rear_size, -rear_size, rear_depth))
    #
    #     front_size = 100
    #     front_depth = 100
    #     point_3d.append((-front_size, -front_size, front_depth))
    #     point_3d.append((-front_size, front_size, front_depth))
    #     point_3d.append((front_size, front_size, front_depth))
    #     point_3d.append((front_size, -front_size, front_depth))
    #     point_3d.append((-front_size, -front_size, front_depth))
    #     point_3d = np.array(point_3d, dtype=np.float64).reshape(-1, 3)
    #
    #     # Map to 2d image points
    #     (point_2d, _) = cv2.projectPoints(point_3d,
    #                                       rotation_vector,
    #                                       translation_vector,
    #                                       self.camera_matrix,
    #                                       self.dist_coeefs)
    #     point_2d = np.int32(point_2d.reshape(-1, 2))
    #
    #     # Draw all the lines
    #     cv2.polylines(image, [point_2d], True, color, line_width, cv2.LINE_AA)
    #     cv2.line(image, tuple(point_2d[1]), tuple(
    #         point_2d[6]), color, line_width, cv2.LINE_AA)
    #     cv2.line(image, tuple(point_2d[2]), tuple(
    #         point_2d[7]), color, line_width, cv2.LINE_AA)
    #     cv2.line(image, tuple(point_2d[3]), tuple(
    #         point_2d[8]), color, line_width, cv2.LINE_AA)
    #
    # def draw_axis(self, img, R, t):
    #     points = np.float32(
    #         [[30, 0, 0], [0, 30, 0], [0, 0, 30], [0, 0, 0]]).reshape(-1, 3)
    #
    #     axisPoints, _ = cv2.projectPoints(
    #         points, R, t, self.camera_matrix, self.dist_coeefs)
    #
    #     img = cv2.line(img, tuple(axisPoints[3].ravel()), tuple(
    #         axisPoints[0].ravel()), (255, 0, 0), 3)
    #     img = cv2.line(img, tuple(axisPoints[3].ravel()), tuple(
    #         axisPoints[1].ravel()), (0, 255, 0), 3)
    #     img = cv2.line(img, tuple(axisPoints[3].ravel()), tuple(
    #         axisPoints[2].ravel()), (0, 0, 255), 3)

    def draw_axes(self, img, R, t):
        """
        OX is drawn in red, OY in green and OZ in blue.
        """
        return cv2.drawFrameAxes(img, self.camera_matrix, self.dist_coeefs, R, t, 30)

    @staticmethod
    def get_pose_marks(marks):
        """Get marks ready for pose estimation from 68 marks"""
        pose_marks = [marks[30], marks[8], marks[36], marks[45], marks[48], marks[54]]
        return pose_marks

    @staticmethod
    def rot_params_rm(R):
        from math import pi,atan2,asin, fabs
        # x轴
        pitch  = (180 * atan2(-R[2][1], R[2][2]) / pi)
        f = (0 > pitch) - (0 < pitch)
        pitch = f * (180 - fabs(pitch))
        # y轴
        yaw = -(180 * asin(R[2][0]) / pi)
        # z轴
        roll = (180 * atan2(-R[1][0], R[0][0]) / pi)
        f = (0 > roll) - (0 < roll)
        roll = f * (180 - fabs(roll))
        if not fabs(roll) < 90.0:
            roll = f * (180 - fabs(roll))
        rot_params = [pitch, yaw, roll]
        return rot_params

    @staticmethod
    def rot_params_rv(rvec_):
        from math import pi, atan2, asin, fabs
        R = cv2.Rodrigues(rvec_)[0]
        # x轴
        pitch  = (180 * atan2(-R[2][1], R[2][2]) / pi)
        f = (0 > pitch) - (0 < pitch)
        pitch = f * (180 - fabs(pitch))
        # y轴
        yaw = -(180 * asin(R[2][0]) / pi)
        # z轴
        roll = (180 * atan2(-R[1][0], R[0][0]) / pi)
        f = (0 > roll) - (0 < roll)
        roll = f * (180 - fabs(roll))
        rot_params = [pitch, yaw, roll]
        return rot_params

    def imageEulerAngle(self, img_points):
        # 这里的img_points对应的是facePoints的第三个返回值,注意是facePoints而非facesPoints
        # 对于facesPoints而言,需要把第三个返回值逐一取出再输入
        # 把列表转为矩阵,且编码形式为float64
        img_points = np.array(img_points, dtype=np.float64)
        rvec, tvec = self.solve_pose_by_68_points(img_points)
        # 旋转向量转旋转矩阵
        R = cv2.Rodrigues(rvec)[0]
        # theta = np.linalg.norm(rvec)
        # r = rvec / theta
        # R_ = np.array([[0, -r[2][0], r[1][0]],
        #                [r[2][0], 0, -r[0][0]],
        #                [-r[1][0], r[0][0], 0]])
        # R = np.cos(theta) * np.eye(3) + (1 - np.cos(theta)) * r * r.T + np.sin(theta) * R_
        # 旋转矩阵转欧拉角
        eulerAngle = self.rot_params_rm(R)
        # 返回一个元组和欧拉角列表
        return (rvec, tvec, R), eulerAngle


# if __name__ == "__main__":
#     # 示例
#     from hyService.utils import Debug
#     dg = Debug()
#     image_input = cv2.imread("./test.jpg")  # 读取一张图片, 必须是三通道或者灰度图
#     fd68 = FaceDetection68()  # 初始化人脸关键点检测类
#     dets_, landmark_, point_list_ = fd68.facePoints(image_input)  # 输入图片. 检测单张人脸
#     # dets_, landmark_, point_list_ = fd68.facesPoints(input_image)  # 输入图片. 检测多张人脸
#     img = fd68.draw_points(image_input, landmark_)
#     dg.cv_show(img)
#     pe = PoseEstimator68(image_input)
#     _, ea = pe.imageEulerAngle(point_list_)  # 输入关键点列表, 如果要使用facesPoints,则输入的是point_list_[i]
#     print(ea)  # 结果