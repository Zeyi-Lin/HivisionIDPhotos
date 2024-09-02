"""
有一些 png 图像下部也会有一些透明的区域，使得图像无法对其底部边框
本程序实现移动图像，使其下部与 png 图像实际大小相对齐
"""
import os
import cv2
import numpy as np
from hivisionai.hycv.utils import get_box_pro

path_pre = os.path.join(os.getcwd(), 'pre')
path_final = os.path.join(os.getcwd(), 'final')


def merge(boxes):
    """
    生成的边框可能不止只有一个，需要将边框合并
    """
    x, y, h, w = boxes[0]
    # x 和 y 应该是整个 boxes 里面最小的值
    if len(boxes) > 1:
        for tmp in boxes:
            x_tmp, y_tmp, h_tmp, w_tmp = tmp
            if x > x_tmp:
                x_max = x_tmp + w_tmp if x_tmp + w_tmp > x + w else x + w
                x = x_tmp
                w = x_max - x
            if y > y_tmp:
                y_max = y_tmp + h_tmp if y_tmp + h_tmp > y + h else y + h
                y = y_tmp
                h = y_max - y
    return tuple((x, y, h, w))


def get_box(png_img):
    """
    获取矩形边框最终返回一个元组 (x,y,h,w)，分别对应矩形左上角的坐标和矩形的高和宽
    """
    r,  g,  b , a = cv2.split(png_img)
    gray_img = a
    th, binary = cv2.threshold(gray_img, 127 , 255, cv2.THRESH_BINARY)  # 二值化
    # cv2.imshow("name", binary)
    # cv2.waitKey(0)
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # 得到轮廓列表 contours
    bounding_boxes = merge([cv2.boundingRect(cnt) for cnt in contours])  # 轮廓合并
    # print(bounding_boxes)
    return bounding_boxes


def get_box_2(png_img):
    """
    不用 opencv 内置算法生成矩形了，改用自己的算法（for 循环）
    """
    _, _, _, a = cv2.split(png_img)
    _, a = cv2.threshold(a, 127, 255, cv2.THRESH_BINARY)
    # 将 r，g，b 通道丢弃，只留下透明度通道
    # cv2.imshow("name", a)
    # cv2.waitKey(0)
    # 在透明度矩阵中，0 代表完全透明
    height,width=a.shape  # 高和宽
    f=0
    tmp1 = 0

    """
    获取上下
    """
    for tmp1 in range(0,height):
        tmp_a_high= a[tmp1:tmp1+1,:][0]
        for tmp2 in range(width):
            # a = tmp_a_low[tmp2]
            if tmp_a_high[tmp2]!=0:
                f=1
        if f == 1:
            break
    delta_y_high = tmp1 + 1
    f = 0
    for tmp1 in range(height,-1, -1):
        tmp_a_low= a[tmp1-1:tmp1+1,:][0]
        for tmp2 in range(width):
            # a = tmp_a_low[tmp2]
            if tmp_a_low[tmp2]!=0:
                f=1
        if f == 1:
            break
    delta_y_bottom = height - tmp1 + 3
    """
    获取左右
    """
    f = 0
    for tmp1 in range(width):
        tmp_a_left = a[:, tmp1:tmp1+1]
        for tmp2 in range(height):
            if tmp_a_left[tmp2] != 0:
                f = 1
        if f==1:
            break
    delta_x_left = tmp1 + 1
    f = 0
    for tmp1 in range(width, -1, -1):
        tmp_a_left = a[:, tmp1-1:tmp1]
        for tmp2 in range(height):
            if tmp_a_left[tmp2] != 0:
                f = 1
        if f==1:
            break
    delta_x_right = width - tmp1 + 1
    return  delta_y_high, delta_y_bottom, delta_x_left, delta_x_right


def move(input_image):
    """
    裁剪主函数，输入一张 png 图像，该图像周围是透明的
    """
    png_img = input_image  # 获取图像

    height, width, channels = png_img.shape  # 高 y、宽 x
    y_low,y_high, _, _ = get_box_pro(png_img, model=2)  # for 循环
    base = np.zeros((y_high, width, channels),dtype=np.uint8)  # for 循环
    png_img = png_img[0:height - y_high, :, :]  # for 循环
    png_img = np.concatenate((base, png_img), axis=0)
    return png_img, y_high


def main():
    if not os.path.exists(path_pre):
        os.makedirs(path_pre)
    if not os.path.exists(path_final):
        os.makedirs(path_final)
    for name in os.listdir(path_pre):
        pass
        # move(name)


if __name__ == "__main__":
    main()
