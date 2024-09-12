"""
@author: cuny
@file: ThinFace.py
@time: 2022/7/2 15:50
@description:
瘦脸算法，用到了图像局部平移法
先使用人脸关键点检测，然后再使用图像局部平移法
需要注意的是，这部分不会包含dlib人脸关键点检测，因为考虑到模型载入的问题
"""

import cv2
import math
import numpy as np


class TranslationWarp(object):
    """
    本类包含瘦脸算法，由于瘦脸算法包含了很多个版本，所以以类的方式呈现
    前两个算法没什么好讲的，网上资料很多
    第三个采用numpy内部的自定义函数处理，在处理速度上有一些提升
    最后采用cv2.map算法，处理速度大幅度提升
    """

    # 瘦脸
    @staticmethod
    def localTranslationWarp(srcImg, startX, startY, endX, endY, radius):
        # 双线性插值法
        def BilinearInsert(src, ux, uy):
            w, h, c = src.shape
            if c == 3:
                x1 = int(ux)
                x2 = x1 + 1
                y1 = int(uy)
                y2 = y1 + 1
                part1 = (
                    src[y1, x1].astype(np.float64) * (float(x2) - ux) * (float(y2) - uy)
                )
                part2 = (
                    src[y1, x2].astype(np.float64) * (ux - float(x1)) * (float(y2) - uy)
                )
                part3 = (
                    src[y2, x1].astype(np.float64) * (float(x2) - ux) * (uy - float(y1))
                )
                part4 = (
                    src[y2, x2].astype(np.float64) * (ux - float(x1)) * (uy - float(y1))
                )
                insertValue = part1 + part2 + part3 + part4
                return insertValue.astype(np.int8)

        ddradius = float(radius * radius)  # 圆的半径
        copyImg = srcImg.copy()  # copy后的图像矩阵
        # 计算公式中的|m-c|^2
        ddmc = (endX - startX) * (endX - startX) + (endY - startY) * (endY - startY)
        H, W, C = srcImg.shape  # 获取图像的形状
        for i in range(W):
            for j in range(H):
                # # 计算该点是否在形变圆的范围之内
                # # 优化，第一步，直接判断是会在（startX,startY)的矩阵框中
                if math.fabs(i - startX) > radius and math.fabs(j - startY) > radius:
                    continue
                distance = (i - startX) * (i - startX) + (j - startY) * (j - startY)
                if distance < ddradius:
                    # 计算出（i,j）坐标的原坐标
                    # 计算公式中右边平方号里的部分
                    ratio = (ddradius - distance) / (ddradius - distance + ddmc)
                    ratio = ratio * ratio
                    # 映射原位置
                    UX = i - ratio * (endX - startX)
                    UY = j - ratio * (endY - startY)

                    # 根据双线性插值法得到UX，UY的值
                    # start_ = time.time()
                    value = BilinearInsert(srcImg, UX, UY)
                    # print(f"双线性插值耗时;{time.time() - start_}")
                    # 改变当前 i ，j的值
                    copyImg[j, i] = value
        return copyImg

    # 瘦脸pro1, 限制了for循环的遍历次数
    @staticmethod
    def localTranslationWarpLimitFor(
        srcImg, startP: np.matrix, endP: np.matrix, radius: float
    ):
        startX, startY = startP[0, 0], startP[0, 1]
        endX, endY = endP[0, 0], endP[0, 1]

        # 双线性插值法
        def BilinearInsert(src, ux, uy):
            w, h, c = src.shape
            if c == 3:
                x1 = int(ux)
                x2 = x1 + 1
                y1 = int(uy)
                y2 = y1 + 1
                part1 = (
                    src[y1, x1].astype(np.float64) * (float(x2) - ux) * (float(y2) - uy)
                )
                part2 = (
                    src[y1, x2].astype(np.float64) * (ux - float(x1)) * (float(y2) - uy)
                )
                part3 = (
                    src[y2, x1].astype(np.float64) * (float(x2) - ux) * (uy - float(y1))
                )
                part4 = (
                    src[y2, x2].astype(np.float64) * (ux - float(x1)) * (uy - float(y1))
                )
                insertValue = part1 + part2 + part3 + part4
                return insertValue.astype(np.int8)

        ddradius = float(radius * radius)  # 圆的半径
        copyImg = srcImg.copy()  # copy后的图像矩阵
        # 计算公式中的|m-c|^2
        ddmc = (endX - startX) ** 2 + (endY - startY) ** 2
        # 计算正方形的左上角起始点
        startTX, startTY = (
            startX - math.floor(radius + 1),
            startY - math.floor((radius + 1)),
        )
        # 计算正方形的右下角的结束点
        endTX, endTY = (
            startX + math.floor(radius + 1),
            startY + math.floor((radius + 1)),
        )
        # 剪切srcImg
        srcImg = srcImg[startTY : endTY + 1, startTX : endTX + 1, :]
        # db.cv_show(srcImg)
        # 裁剪后的图像相当于在x,y都减少了startX - math.floor(radius + 1)
        # 原本的endX, endY在切后的坐标点
        endX, endY = (
            endX - startX + math.floor(radius + 1),
            endY - startY + math.floor(radius + 1),
        )
        # 原本的startX, startY剪切后的坐标点
        startX, startY = (math.floor(radius + 1), math.floor(radius + 1))
        H, W, C = srcImg.shape  # 获取图像的形状
        for i in range(W):
            for j in range(H):
                # 计算该点是否在形变圆的范围之内
                # 优化，第一步，直接判断是会在（startX,startY)的矩阵框中
                # if math.fabs(i - startX) > radius and math.fabs(j - startY) > radius:
                #     continue
                distance = (i - startX) * (i - startX) + (j - startY) * (j - startY)
                if distance < ddradius:
                    # 计算出（i,j）坐标的原坐标
                    # 计算公式中右边平方号里的部分
                    ratio = (ddradius - distance) / (ddradius - distance + ddmc)
                    ratio = ratio * ratio
                    # 映射原位置
                    UX = i - ratio * (endX - startX)
                    UY = j - ratio * (endY - startY)

                    # 根据双线性插值法得到UX，UY的值
                    # start_ = time.time()
                    value = BilinearInsert(srcImg, UX, UY)
                    # print(f"双线性插值耗时;{time.time() - start_}")
                    # 改变当前 i ，j的值
                    copyImg[j + startTY, i + startTX] = value
        return copyImg

    # # 瘦脸pro2,采用了numpy自定义函数做处理
    # def localTranslationWarpNumpy(self, srcImg, startP: np.matrix, endP: np.matrix, radius: float):
    #     startX , startY = startP[0, 0], startP[0, 1]
    #     endX, endY = endP[0, 0], endP[0, 1]
    #     ddradius = float(radius * radius)  # 圆的半径
    #     copyImg = srcImg.copy()  # copy后的图像矩阵
    #     # 计算公式中的|m-c|^2
    #     ddmc = (endX - startX)**2 + (endY - startY)**2
    #     # 计算正方形的左上角起始点
    #     startTX, startTY = (startX - math.floor(radius + 1), startY - math.floor((radius + 1)))
    #     # 计算正方形的右下角的结束点
    #     endTX, endTY = (startX + math.floor(radius + 1), startY + math.floor((radius + 1)))
    #     # 剪切srcImg
    #     self.thinImage = srcImg[startTY : endTY + 1, startTX : endTX + 1, :]
    #     # s = self.thinImage
    #     # db.cv_show(srcImg)
    #     # 裁剪后的图像相当于在x,y都减少了startX - math.floor(radius + 1)
    #     # 原本的endX, endY在切后的坐标点
    #     endX, endY = (endX - startX + math.floor(radius + 1), endY - startY + math.floor(radius + 1))
    #     # 原本的startX, startY剪切后的坐标点
    #     startX ,startY = (math.floor(radius + 1), math.floor(radius + 1))
    #     H, W, C = self.thinImage.shape  # 获取图像的形状
    #     index_m = np.arange(H * W).reshape((H, W))
    #     triangle_ufunc = np.frompyfunc(self.process, 9, 3)
    #     # start_ = time.time()
    #     finalImgB, finalImgG, finalImgR = triangle_ufunc(index_m, self, W, ddradius, ddmc, startX, startY, endX, endY)
    #     finaleImg = np.dstack((finalImgB, finalImgG, finalImgR)).astype(np.uint8)
    #     finaleImg = np.fliplr(np.rot90(finaleImg, -1))
    #     copyImg[startTY: endTY + 1, startTX: endTX + 1, :] = finaleImg
    #     # print(f"图像处理耗时;{time.time() - start_}")
    #     # db.cv_show(copyImg)
    #     return copyImg

    # 瘦脸pro3,采用opencv内置函数
    @staticmethod
    def localTranslationWarpFastWithStrength(
        srcImg, startP: np.matrix, endP: np.matrix, radius, strength: float = 100.0
    ):
        """
        采用opencv内置函数
        Args:
            srcImg: 源图像
            startP: 起点位置
            endP: 终点位置
            radius: 处理半径
            strength: 瘦脸强度，一般取100以上

        Returns:

        """
        startX, startY = startP[0, 0], startP[0, 1]
        endX, endY = endP[0, 0], endP[0, 1]
        ddradius = float(radius * radius)
        # copyImg = np.zeros(srcImg.shape, np.uint8)
        # copyImg = srcImg.copy()

        maskImg = np.zeros(srcImg.shape[:2], np.uint8)
        cv2.circle(maskImg, (startX, startY), math.ceil(radius), (255, 255, 255), -1)

        K0 = 100 / strength

        # 计算公式中的|m-c|^2
        ddmc_x = (endX - startX) * (endX - startX)
        ddmc_y = (endY - startY) * (endY - startY)
        H, W, C = srcImg.shape

        mapX = np.vstack([np.arange(W).astype(np.float32).reshape(1, -1)] * H)
        mapY = np.hstack([np.arange(H).astype(np.float32).reshape(-1, 1)] * W)

        distance_x = (mapX - startX) * (mapX - startX)
        distance_y = (mapY - startY) * (mapY - startY)
        distance = distance_x + distance_y
        K1 = np.sqrt(distance)
        ratio_x = (ddradius - distance_x) / (ddradius - distance_x + K0 * ddmc_x)
        ratio_y = (ddradius - distance_y) / (ddradius - distance_y + K0 * ddmc_y)
        ratio_x = ratio_x * ratio_x
        ratio_y = ratio_y * ratio_y

        UX = mapX - ratio_x * (endX - startX) * (1 - K1 / radius)
        UY = mapY - ratio_y * (endY - startY) * (1 - K1 / radius)

        np.copyto(UX, mapX, where=maskImg == 0)
        np.copyto(UY, mapY, where=maskImg == 0)
        UX = UX.astype(np.float32)
        UY = UY.astype(np.float32)
        copyImg = cv2.remap(srcImg, UX, UY, interpolation=cv2.INTER_LINEAR)
        return copyImg


def thinFace(src, landmark, place: int = 0, strength=30.0):
    """
    瘦脸程序接口，输入人脸关键点信息和强度，即可实现瘦脸
    注意处理四通道图像
    Args:
        src: 原图
        landmark: 关键点信息
        place: 选择瘦脸区域，为0-4之间的值
        strength: 瘦脸强度，输入值在0-10之间，如果小于或者等于0，则不瘦脸

    Returns:
        瘦脸后的图像
    """
    strength = min(100.0, strength * 10.0)
    if strength <= 0.0:
        return src
    # 也可以设置瘦脸区域
    place = max(0, min(4, int(place)))
    left_landmark = landmark[4 + place]
    left_landmark_down = landmark[6 + place]
    right_landmark = landmark[13 + place]
    right_landmark_down = landmark[15 + place]
    endPt = landmark[58]
    # 计算第4个点到第6个点的距离作为瘦脸距离
    r_left = math.sqrt(
        (left_landmark[0, 0] - left_landmark_down[0, 0]) ** 2
        + (left_landmark[0, 1] - left_landmark_down[0, 1]) ** 2
    )

    # 计算第14个点到第16个点的距离作为瘦脸距离
    r_right = math.sqrt(
        (right_landmark[0, 0] - right_landmark_down[0, 0]) ** 2
        + (right_landmark[0, 1] - right_landmark_down[0, 1]) ** 2
    )
    # 瘦左边脸
    thin_image = TranslationWarp.localTranslationWarpFastWithStrength(
        src, left_landmark[0], endPt[0], r_left, strength
    )
    # 瘦右边脸
    thin_image = TranslationWarp.localTranslationWarpFastWithStrength(
        thin_image, right_landmark[0], endPt[0], r_right, strength
    )
    return thin_image


# if __name__ == "__main__":
#     import os
#     from hycv.FaceDetection68.faceDetection68 import FaceDetection68

#     local_file = os.path.dirname(__file__)
#     PREDICTOR_PATH = f"{local_file}/weights/shape_predictor_68_face_landmarks.dat"  # 关键点检测模型路径
#     fd68 = FaceDetection68(model_path=PREDICTOR_PATH)
#     input_image = cv2.imread("test_image/4.jpg", -1)
#     _, landmark_, _ = fd68.facePoints(input_image)
#     output_image = thinFace(input_image, landmark_, strength=30.2)
#     cv2.imwrite("thinFaceCompare.png", np.hstack((input_image, output_image)))
