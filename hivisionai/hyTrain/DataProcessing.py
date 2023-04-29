import cv2
import random
from scipy.ndimage import grey_erosion, grey_dilation
import numpy as np
from glob import glob
import random


def make_a_and_trimaps(input_image, resize=(512, 512)):
    image = cv2.resize(input_image, resize)
    b, g, r, a = cv2.split(image)

    a_scale_resize = a / 255
    trimap = (a_scale_resize >= 0.95).astype("float32")
    not_bg = (a_scale_resize > 0).astype("float32")
    d_size = a.shape[0] // 256 * random.randint(10, 20)
    e_size = a.shape[0] // 256 * random.randint(10, 20)
    trimap[np.where((grey_dilation(not_bg, size=(d_size, d_size))
                    - grey_erosion(trimap, size=(e_size, e_size))) != 0)] = 0.5

    return a, trimap*255


def get_filedir_filelist(input_path):
    return glob(input_path+"/*")


def extChange(filedir, ext="png"):
    ext_origin = str(filedir).split(".")[-1]
    return filedir.replace(ext_origin, ext)

def random_image_crop(input_image:np.array, crop_size=(512,512)):
    height, width = input_image.shape[0], input_image.shape[1]
    crop_height, crop_width = crop_size[0], crop_size[1]
    x = random.randint(0, width-crop_width)
    y = random.randint(0, height-crop_height)
    return input_image[y:y+crop_height, x:x+crop_width]