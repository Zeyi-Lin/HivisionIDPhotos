"""
@author: cuny
@fileName: utils.py
@create_time: 2021/12/29 下午 1:29
@introduce:
焕影服务的一些工具函数，涉及两类：
1. 开发 debug 时候的工具函数
2. 初始化 COS 配置时的工具函数
"""
import cv2
from .error import WrongImageType
import numpy as np

class Debug(object):
    color_dir:dict = {
        "red":"31m",
        "green":"32m",
        "yellow":"33m",
        "blue":"34m",
        "common":"38m"
    }  # 颜色值
    __DEBUG:bool = True

    @property
    def debug(self):
        return self.__DEBUG

    @debug.setter
    def debug(self, value):
        if not isinstance(value, bool):
            raise TypeError("你必须设定 debug 的值为 bool 的 True 或者 False")
        print(f"设置 debug 为：{value}")
        self.__DEBUG = value

    def debug_print(self, text, **kwargs):
        if self.debug is True:
            key = self.color_dir["common"] if "font_color" not in kwargs else self.color_dir[kwargs["font_color"]]
            print(f"\033[{key}{text}\033[0m")

    @staticmethod
    def resize_image_esp(input_image, esp=2000):
        """
        输入：
        input_path：numpy 图片
        esp：限制的最大边长
        """
        # resize 函数=>可以让原图压缩到最大边为 esp 的尺寸 (不改变比例)
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

    def cv_show(self, *args, **kwargs):
        def check_images(img):
            # 判断是否是矩阵类型
            if not isinstance(img, np.ndarray):
                raise WrongImageType("输入的图像必须是 np.ndarray 类型！")
        if self.debug is True:
            size = 500 if "size" not in kwargs else kwargs["size"]  # 默认缩放尺寸为最大边 500 像素点
            if len(args) == 0:
                raise ProcessError("你必须传入若干图像信息！")
            flag = False
            base = None
            for image in args:
                check_images(image)
                if flag is False:
                    image = self.resize_image_esp(image, size)
                    h, w = image.shape[0], image.shape[1]
                    flag = (w, h)
                    base = image
                else:
                    image = cv2.resize(image, flag)
                    base = np.hstack((base, image))
            title = "cv_show" if "winname" not in kwargs else kwargs["winname"]
            cv2.imshow(title, base)
            cv2.waitKey(0)
        else:
            pass
