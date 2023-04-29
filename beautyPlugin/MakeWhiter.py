"""
@author: cuny
@file: MakeWhiter.py
@time: 2022/7/2 14:28
@description: 
美白算法
"""
import os
import cv2
import math
import numpy as np
local_path = os.path.dirname(__file__)


class MakeWhiter(object):
    class __LutWhite:
        """
        美白的内部类
        """

        def __init__(self, lut):
            cube64rows = 8
            cube64size = 64
            cube256size = 256
            cubeScale = int(cube256size / cube64size)  # 4

            reshapeLut = np.zeros((cube256size, cube256size, cube256size, 3))
            for i in range(cube64size):
                tmp = math.floor(i / cube64rows)
                cx = int((i - tmp * cube64rows) * cube64size)
                cy = int(tmp * cube64size)
                cube64 = lut[cy:cy + cube64size, cx:cx + cube64size]  # cube64 in lut(512*512 (512=8*64))
                _rows, _cols, _ = cube64.shape
                if _rows == 0 or _cols == 0:
                    continue
                cube256 = cv2.resize(cube64, (cube256size, cube256size))
                i = i * cubeScale
                for k in range(cubeScale):
                    reshapeLut[i + k] = cube256
            self.lut = reshapeLut

        def imageInLut(self, src):
            arr = src.copy()
            bs = arr[:, :, 0]
            gs = arr[:, :, 1]
            rs = arr[:, :, 2]
            arr[:, :] = self.lut[bs, gs, rs]
            return arr

    def __init__(self, lutImage: np.ndarray = None):
        self.__lutWhiten = None
        if lutImage is not None:
            self.__lutWhiten = self.__LutWhite(lutImage)

    def setLut(self, lutImage: np.ndarray):
        self.__lutWhiten = self.__LutWhite(lutImage)

    @staticmethod
    def generate_identify_color_matrix(size: int = 512, channel: int = 3) -> np.ndarray:
        """
        用于生成一张初始的查找表
        Args:
            size: 查找表尺寸，默认为512
            channel: 查找表通道数，默认为3

        Returns:
            返回生成的查找表图像
        """
        img = np.zeros((size, size, channel), dtype=np.uint8)
        for by in range(size // 64):
            for bx in range(size // 64):
                for g in range(64):
                    for r in range(64):
                        x = r + bx * 64
                        y = g + by * 64
                        img[y][x][0] = int(r * 255.0 / 63.0 + 0.5)
                        img[y][x][1] = int(g * 255.0 / 63.0 + 0.5)
                        img[y][x][2] = int((bx + by * 8.0) * 255.0 / 63.0 + 0.5)
        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR).clip(0, 255).astype('uint8')

    def run(self, src: np.ndarray, strength: int) -> np.ndarray:
        """
        美白图像
        Args:
            src: 原图
            strength: 美白强度，0 - 10
        Returns:
            美白后的图像
        """
        dst = src.copy()
        strength = min(10, int(strength)) / 10.
        if strength <= 0:
            return dst
        self.setLut(cv2.imread(f"{local_path}/lut_image/3.png", -1))
        _, _, c = src.shape
        img = self.__lutWhiten.imageInLut(src[:, :, :3])
        dst[:, :, :3] = cv2.addWeighted(src[:, :, :3], 1 - strength, img, strength, 0)
        return dst


if __name__ == "__main__":
    # makeLut = MakeWhiter()
    # cv2.imwrite("lutOrigin.png", makeLut.generate_identify_color_matrix())
    input_image = cv2.imread("test_image/7.jpg", -1)
    lut_image = cv2.imread("lut_image/3.png")
    makeWhiter = MakeWhiter(lut_image)
    output_image = makeWhiter.run(input_image, 10)
    cv2.imwrite("makeWhiterCompare.png", np.hstack((input_image, output_image)))
