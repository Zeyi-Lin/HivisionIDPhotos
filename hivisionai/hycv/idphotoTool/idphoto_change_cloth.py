import cv2
import numpy as np
from ..utils import get_box_pro, cut_BiggestAreas, locate_neck, get_cutbox_image
from .move_image import move
from ..vision import add_background, cover_image
from ..matting_tools import get_modnet_matting
from .neck_processing import transformationNeck
from .cuny_tools import checkSharpCorner, checkJaw, checkHairLOrR,\
                        checkLongHair, checkLongHair2, convert_black_array, find_black

test_image_path = "./supple_image/"

def change_cloth(input_image:np.array,
                 cloth_model,
                 CLOTH_WIDTH,
                 CLOTH_X,
                 CLOTH_WIDTH_CHANGE,
                 CLOTH_X_CHANGE,
                 CLOTH_Y,
                 neck_ratio=0.2,
                 space_adjust=None,
                 hair_front=True
                 ):

    # ============= 1. 得到头脖子图、纯头图、纯脖子图的相关信息 =============== #
    # 1.1 获取原图input_image属性
    input_height, input_width = input_image.shape[0], input_image.shape[1]
    # print("input_height:", input_height)
    # print("input_width", input_width)
    b, g, r, input_a = cv2.split(input_image)

    # 1.2 得到头脖子图headneck_image、纯头图head_image
    input_image = add_background(input_image, bgr=(255, 255, 255))
    headneck_image = get_modnet_matting(input_image, checkpoint_path="./checkpoint/huanying_headneck3.onnx")
    head_image = get_modnet_matting(input_image, checkpoint_path="./checkpoint/huanying_head3.onnx")

    # 1.3 得到优化后的脖子图neck_threshold_image
    _, _, _, headneck_a = cv2.split(headneck_image)
    _, _, _, head_a = cv2.split(head_image)
    neck_a = cv2.subtract(headneck_a, head_a)
    _, neck_threshold_a = cv2.threshold(neck_a, 180, 255, cv2.THRESH_BINARY)
    neck_threshold_image = cut_BiggestAreas(cv2.merge(
        (np.uint8(b), np.uint8(g), np.uint8(r), np.uint8(neck_threshold_a))))

    # 1.4 得到优化后的头脖子图headneck_threshold_image
    _, headneck_threshold_a = cv2.threshold(headneck_a, 180, 255, cv2.THRESH_BINARY)
    headneck_threshold_image = cut_BiggestAreas(
        cv2.merge((np.uint8(b), np.uint8(g), np.uint8(r), np.uint8(headneck_threshold_a))))

    # 1.5 获取脖子图、头脖子图的A矩阵
    _, _, _, neck_threshold_a2 = cv2.split(neck_threshold_image)
    _, _, _, headneck_threshold_a2 = cv2.split(headneck_threshold_image)

    # 1.6 获取头发的底部坐标信息，以及头的左右坐标信息
    _, headneck_y_bottom, headneck_x_left, headneck_x_right = get_box_pro(headneck_threshold_image,
                                                                            model=2, correction_factor=0)
    headneck_y_bottom = input_height-headneck_y_bottom
    headneck_x_right = input_width-headneck_x_right



    # ============= 2. 得到原来的衣服的相关信息 =============== #
    # 2.1 抠出原来衣服cloth_image_input
    cloth_origin_image_a = cv2.subtract(np.uint8(input_a), np.uint8(headneck_a))
    _, cloth_origin_image_a = cv2.threshold(cloth_origin_image_a, 180, 255, cv2.THRESH_BINARY)
    cloth_image_input = cut_BiggestAreas(cv2.merge((np.uint8(b), np.uint8(g), np.uint8(r), np.uint8(cloth_origin_image_a))))

    # 2.2 对cloth_image_input做裁剪（减去上面的大片透明区域）
    cloth_image_input_top_y, _, _, _ = get_box_pro(cloth_image_input, model=2)
    cloth_image_input_cut = cloth_image_input[cloth_image_input_top_y:, :]



    # ============= 3.计算脖子的衔接点信息，为新服装拼接作准备 ===============#
    # 3.1 得到裁剪透明区域后的脖子图neck_cut_image，以及它的坐标信息
    neck_y_top, neck_y_bottom, neck_x_left, neck_x_right = get_box_pro(neck_threshold_image, model=2)
    neck_cut_image = get_cutbox_image(neck_threshold_image)
    neck_height = input_height - (neck_y_top + neck_y_bottom)
    neck_width = input_width - (neck_x_right + neck_x_left)

    # 3.2 对neck_cut_image做“尖尖”检测，得到较低的“尖尖”对于脖子高度的比率y_neck_corner_ratio
    y_neck_corner = checkSharpCorner(neck_cut_image)
    y_neck_corner_ratio = y_neck_corner / neck_height

    # 3.3 取y_neck_corner_ratio与新衣服预先设定好的neck_ratio的最大值，作为最终的neck_ratio
    neck_ratio = max(neck_ratio, y_neck_corner_ratio)

    # 3.4 计算在neck_ratio下的脖子左衔接点坐标neck_left_x_byRatio，neck_left_y_byRatio、宽度neck_width_byRatio
    neck_coordinate1, neck_coordinate2, neck_width_byRatio = locate_neck(neck_cut_image, float(neck_ratio))
    neck_width_byRatio = neck_width_byRatio + CLOTH_WIDTH_CHANGE
    neck_left_x_byRatio = neck_x_left + neck_coordinate1[1] + CLOTH_X_CHANGE
    neck_left_y_byRatio = neck_y_top + neck_coordinate1[0]



    # ============= 4.读取新衣服图，调整大小 =============== #
    # 4.1 得到新衣服图片的拼贴坐标x, y以及脖子最底部的坐标y_neckline
    CLOTH_HEIGHT = CLOTH_Y
    RESIZE_RATIO = neck_width_byRatio / CLOTH_WIDTH
    x, y = int(neck_left_x_byRatio - CLOTH_X * RESIZE_RATIO), neck_left_y_byRatio
    y_neckline = y + int(CLOTH_HEIGHT * RESIZE_RATIO)

    # 4.2 读取新衣服,并进行缩放
    cloth = cv2.imread(cloth_model, -1)
    cloth_height, cloth_width = cloth.shape[0], cloth.shape[1]
    cloth = cv2.resize(cloth, (int(cloth_width * RESIZE_RATIO),
                    int(cloth_height * RESIZE_RATIO)), interpolation=cv2.INTER_AREA)

    # 4.3 获得新衣服的A矩阵
    _, _, _, cloth_a = cv2.split(cloth)



    # ============= 5. 判断头发的前后关系，以及对于长发的背景填充、判定是否为长发等 =============== #
    # 5.1 根据hair_number, 判断是0:头发披在后面、1:左前右后、2:左后右前还是3:都在前面
    hair_number = checkHairLOrR(cloth_image_input_cut, input_a, neck_a, cloth_image_input_top_y)

    # 5.2 对于长发的背景填充-将原衣服区域的部分变成黑色，并填充到最终图片作为背景
    cloth_image_input_save = cloth_origin_image_a[:int(y+cloth_height*RESIZE_RATIO),
                             max(0, headneck_x_left-1):min(headneck_x_right+1, input_width)]
    headneck_threshold_a_save = headneck_a[:int(y+cloth_height*RESIZE_RATIO),
                             max(0, headneck_x_left-1):min(headneck_x_right+1, input_width)]
    headneck_mask = convert_black_array(headneck_threshold_a_save)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    cloth_image_input_save = cv2.dilate(cloth_image_input_save, kernel)
    cloth_image_input_save = np.uint8(cloth_image_input_save*headneck_mask)

    # 5.3 检测是否为长发
    head_bottom_y = input_height - get_box_pro(head_image, model=2, correction_factor=0)[1]
    isLongHair01 = checkLongHair(neck_cut_image, head_bottom_y, neck_top_y=neck_y_top)
    isLongHair02 = checkLongHair2(head_bottom_y, cloth_image_input_top_y)
    isLongHair = isLongHair01 and isLongHair02



    # ============= 6.第一轮服装拼贴 =============== #
    # 6.1 创建一个空白背景background
    background = np.uint8((np.zeros([input_height, input_width, 4])))

    # 6.2 盖上headneck_image
    result_headneck_image = cover_image(headneck_image, background, 0, 0, mode=3)

    # 6.3 如果space_adjust开启的话，background的底部将增加一些行数
    if space_adjust is not None:
        insert_array = np.uint8(np.zeros((space_adjust, input_width, 4)))
        result_headneck_image = np.r_[result_headneck_image, insert_array]

    # 6.4 盖上新衣服
    result_cloth_image = cover_image(cloth, result_headneck_image, x, y, mode=3)

    # 6.5 截出脖子与衣服交接的区域neck_cloth_image，以及它的A矩阵neck_cloth_a
    neck_cloth_image = result_cloth_image[y:y_neckline,
                       neck_left_x_byRatio:neck_left_x_byRatio+neck_width_byRatio]
    _, _, _, neck_cloth_a = cv2.split(neck_cloth_image)
    _, neck_cloth_a = cv2.threshold(neck_cloth_a, 127, 255, cv2.THRESH_BINARY)



    # ============= 7.第二轮服装拼贴 =============== #
    # 7.1 检测neck_cloth_a中是否有黑点（即镂空区域）
    # 如果black_dots_y不为None，说明存在镂空区域——需要进行脖子拉伸；反而则不存在，不需要
    black_dots_y = find_black(neck_cloth_a)
    # cv2.imwrite(test_image_path+"neck_cloth_a.jpg", neck_cloth_a)

    # flag: 用于指示是否进行拉伸
    flag = 0

    # 7.2 如果存在镂空区域，则进行拉伸
    if black_dots_y != None:
        flag = 1
        # cutNeckHeight：要拉伸的区域的顶部y值
        # neckBelow：脖子底部的y值
        # toHeight：拉伸区域的高度
        cutNeckHeight = black_dots_y + y - 6
        # if cutNeckHeight < neck_y_top+checkJaw(neck_cut_image, y_start=checkSharpCorner(neck_cut_image))[1]:
        #     print("拒绝！！！！！！")
        #     return 0, 0, 0, 0, 0

        neckBelow = input_height-neck_y_bottom
        toHeight = y_neckline-cutNeckHeight
        print("cutNeckHeight:", cutNeckHeight)
        print("toHeight:", toHeight)
        print("neckBelow:", neckBelow)
        # cv2.imwrite(test_image_path+"neck_image.png", neck_threshold_image)

        # 对原有的脖子做拉伸，得到new_neck_image
        new_neck_image = transformationNeck(neck_threshold_image,
                                            cutNeckHeight=cutNeckHeight,
                                            neckBelow=neckBelow,
                                            toHeight=toHeight)
        # cv2.imwrite(test_image_path+"new_neck_image.png", new_neck_image)


        # 重新进行拼贴
        result_headneck_image = cover_image(new_neck_image, result_headneck_image, 0, 0, mode=3)
        result_headneck_image = cover_image(head_image, result_headneck_image, 0, 0, mode=3)
        result_cloth_image = cover_image(cloth, result_headneck_image, x, y, mode=3)

        _, _, _, neck_a = cv2.split(new_neck_image)


    # 7.3 下面是对最终图的A矩阵进行处理
    # 首先将neck_a与新衣服衔接点的左边两边区域删去，得到neck_a_leftright
    neck_a_copy = neck_a.copy()
    neck_a_copy[neck_left_y_byRatio:, :max(0, neck_left_x_byRatio-4)] = 0
    neck_a_copy[neck_left_y_byRatio:,
            min(input_width, neck_left_x_byRatio + neck_width_byRatio - CLOTH_X_CHANGE+4):] = 0
    n_a_leftright = cv2.subtract(neck_a, neck_a_copy)

    # 7.4 如果存在镂空区域，则对headneck_a做进一步处理
    if black_dots_y != None:
        neck_a = cv2.subtract(neck_a, n_a_leftright)
        # 得到去掉脖子两翼的新的headneck_a
        headneck_a = cv2.subtract(headneck_a, n_a_leftright)
        # 将headneck_a覆盖上拉伸后的脖子A矩阵
        headneck_a = np.uint8(cover_image(neck_a, headneck_a, 0, 0, mode=2))
    else:
        headneck_a = cv2.subtract(headneck_a, n_a_leftright)



    # 7.5 如果是长发
    if isLongHair:
        # 在背景加入黑色矩形，填充抠头模型可能会出现的，部分长发没有抠全的部分
        black_background_x1 = int(neck_left_x_byRatio - neck_width_byRatio * 0.1)
        black_background_x2 = int(neck_left_x_byRatio + neck_width_byRatio * 1.1)
        black_background_y1 = int(neck_y_top - neck_height * 0.1)
        black_background_y2 = min(input_height - neck_y_bottom - 3, head_bottom_y)
        headneck_a[black_background_y1:black_background_y2, black_background_x1:black_background_x2] = 255

        # 在背景中，将原本衣服区域置为黑色
        headneck_a = cover_image(cloth_image_input_save, headneck_a, max(0, headneck_x_left-1), 0, mode=2)

    # 7.6 如果space_adjust开启的话，headneck_a的底部将增加一些行数
    if space_adjust is not None:
        insert_array = np.uint8(np.zeros((space_adjust, input_width)))
        headneck_a = np.r_[headneck_a, insert_array]

    # 7.7 盖上新衣服
    new_a = np.uint8(cover_image(cloth_a, headneck_a, x, y, mode=2))

    # neck_cloth_a = new_a[y:y_neckline, neck_left_x_byRatio:neck_left_x_byRatio + neck_width_byRatio]
    # _, neck_cloth_a = cv2.threshold(neck_cloth_a, 127, 255, cv2.THRESH_BINARY)
    # cv2.imwrite(test_image_path + "neck_cloth_a2.jpg", neck_cloth_a)
    #
    # if find_black(neck_cloth_a) != None:
    #     print("拒绝！！！！")
    #     return "拒绝"

    # 7.8 如果有头发披在前面
    if hair_front:
        # 如果头发披在左边
        if hair_number == 1:
            result_cloth_image = cover_image(head_image[:, :head_image.shape[1] // 2], result_cloth_image, 0, 0, mode=3)
        # 如果头发披在右边
        elif hair_number == 2:
            result_cloth_image = cover_image(head_image[:, head_image.shape[1] // 2:], result_cloth_image, head_image.shape[1] // 2, 0, mode=3)
        # 如果头发披在两边
        elif hair_number == 3:
            result_cloth_image = cover_image(head_image, result_cloth_image, 0, 0, mode=3)

    # 7.9 合成最终图片，并做底部空隙的移动
    r, g, b, _ = cv2.split(result_cloth_image)
    result_image = move(cv2.merge((r, g, b, new_a)))

    # 7.10 返回：结果图、是否拉伸、头发前披状态、是否长发
    return 1, result_image, flag, hair_number, isLongHair


if __name__ == "__main__":
    pass
