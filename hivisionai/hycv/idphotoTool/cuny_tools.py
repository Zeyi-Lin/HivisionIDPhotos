import cv2
import numpy as np
from ..utils import get_box_pro
from ..vision import cover_image, draw_picture_dots


def transformationNeck2(image:np.ndarray, per_to_side:float=0.8)->np.ndarray:
    """
    透视变换脖子函数,输入图像和四个点(矩形框)
    矩形框内的图像可能是不完整的(边角有透明区域)
    我们将根据透视变换将矩形框内的图像拉伸成和矩形框一样的形状.
    算法分为几个步骤: 选择脖子的四个点 -> 选定这四个点拉伸后的坐标 -> 透视变换 -> 覆盖原图
    """
    _, _, _, a = cv2.split(image)  # 这应该是一个四通道的图像
    height, width = a.shape
    def locate_side(image_:np.ndarray, x_:int, y_max:int) -> int:
        # 寻找x=y, 且 y <= y_max 上从下往上第一个非0的点,如果没找到就返回0
        y_ = 0
        for y_ in range(y_max - 1, -1, -1):
            if image_[y_][x_] != 0:
                break
        return y_
    def locate_width(image_:np.ndarray, y_:int, mode, left_or_right:int=None):
        # 从y=y这个水平线上寻找两边的非零点
        # 增加left_or_right的原因在于为下面check_jaw服务
        if mode==1:  # 左往右
            x_ = 0
            if left_or_right is None:
                left_or_right = 0
            for x_ in range(left_or_right, width):
                if image_[y_][x_] != 0:
                    break
        else:  # 右往左
            x_ = width
            if left_or_right is None:
                left_or_right = width - 1
            for x_ in range(left_or_right, -1, -1):
                if image_[y_][x_] != 0:
                    break
        return x_
    def check_jaw(image_:np.ndarray, left_, right_):
        """
        检查选择的点是否与截到下巴,如果截到了,就往下平移一个单位
        """
        f= True # True代表没截到下巴
        # [x, y]
        for x_cell in range(left_[0] + 1, right_[0]):
            if image_[left_[1]][x_cell] == 0:
                f = False
                break
        if f is True:
            return left_, right_
        else:
            y_ = left_[1] + 2
            x_left_ = locate_width(image_, y_, mode=1, left_or_right=left_[0])
            x_right_ = locate_width(image_, y_, mode=2, left_or_right=right_[0])
            left_, right_ = check_jaw(image_, [x_left_, y_], [x_right_, y_])
        return left_, right_
    # 选择脖子的四个点,核心在于选择上面的两个点,这两个点的确定的位置应该是"宽出来的"两个点
    _, _ ,_, a = cv2.split(image)  # 这应该是一个四通道的图像
    ret,a_thresh = cv2.threshold(a,127,255,cv2.THRESH_BINARY)
    y_high, y_low, x_left, x_right = get_box_pro(image=image, model=1) # 直接返回矩阵信息
    y_left_side = locate_side(image_=a_thresh, x_=x_left, y_max=y_low)  # 左边的点的y轴坐标
    y_right_side = locate_side(image_=a_thresh, x_=x_right, y_max=y_low)  # 右边的点的y轴坐标
    y = min(y_left_side, y_right_side)  # 将两点的坐标保持相同
    cell_left_above, cell_right_above = check_jaw(a_thresh,[x_left, y], [x_right, y])
    x_left, x_right = cell_left_above[0], cell_right_above[0]
    # 此时我们寻找到了脖子的"宽出来的"两个点,这两个点作为上面的两个点, 接下来寻找下面的两个点
    if per_to_side >1:
        assert ValueError("per_to_side 必须小于1!")
    # 在后面的透视变换中我会把它拉成矩形, 在这里我先获取四个点的高和宽
    height_ = 150  # 这个值应该是个变化的值,与拉伸的长度有关,但是现在先规定为150
    width_ = x_right - x_left  # 其实也就是 cell_right_above[1] - cell_left_above[1]
    y = int((y_low - y)*per_to_side + y)  # 定位y轴坐标
    cell_left_below, cell_right_bellow = ([locate_width(a_thresh, y_=y, mode=1), y], [locate_width(a_thresh, y_=y, mode=2), y])
    # 四个点全齐,开始透视变换
    # 寻找透视变换后的四个点,只需要变换below的两个点即可
    # cell_left_below_final, cell_right_bellow_final = ([cell_left_above[1], y_low], [cell_right_above[1], y_low])
    # 需要变换的四个点为 cell_left_above, cell_right_above, cell_left_below, cell_right_bellow
    rect = np.array([cell_left_above, cell_right_above, cell_left_below, cell_right_bellow],
                    dtype='float32')
    # 变化后的坐标点
    dst = np.array([[0, 0], [width_, 0], [0 , height_], [width_, height_]],
                    dtype='float32')
    # 计算变换矩阵
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (width_, height_))
    final = cover_image(image=warped, background=image, mode=3, x=cell_left_above[0], y=cell_left_above[1])
    # tmp = np.zeros(image.shape)
    # final = cover_image(image=warped, background=tmp, mode=3, x=cell_left_above[0], y=cell_left_above[1])
    # final = cover_image(image=image, background=final, mode=3, x=0, y=0)
    return final

def transformationNeck(image:np.ndarray, cutNeckHeight:int, neckBelow:int,
                       toHeight:int,per_to_side:float=0.75) -> np.ndarray:
    """
    脖子扩充算法, 其实需要输入的只是脖子扣出来的部分以及需要被扩充的高度/需要被扩充成的高度.
    """
    height, width, channels = image.shape
    _, _, _, a = cv2.split(image)  # 这应该是一个四通道的图像
    ret, a_thresh = cv2.threshold(a, 127, 255, cv2.THRESH_BINARY)  # 将透明图层二值化
    def locate_width(image_:np.ndarray, y_:int, mode, left_or_right:int=None):
        # 从y=y这个水平线上寻找两边的非零点
        # 增加left_or_right的原因在于为下面check_jaw服务
        if mode==1:  # 左往右
            x_ = 0
            if left_or_right is None:
                left_or_right = 0
            for x_ in range(left_or_right, width):
                if image_[y_][x_] != 0:
                    break
        else:  # 右往左
            x_ = width
            if left_or_right is None:
                left_or_right = width - 1
            for x_ in range(left_or_right, -1, -1):
                if image_[y_][x_] != 0:
                    break
        return x_
    def check_jaw(image_:np.ndarray, left_, right_):
        """
        检查选择的点是否与截到下巴,如果截到了,就往下平移一个单位
        """
        f= True # True代表没截到下巴
        # [x, y]
        for x_cell in range(left_[0] + 1, right_[0]):
            if image_[left_[1]][x_cell] == 0:
                f = False
                break
        if f is True:
            return left_, right_
        else:
            y_ = left_[1] + 2
            x_left_ = locate_width(image_, y_, mode=1, left_or_right=left_[0])
            x_right_ = locate_width(image_, y_, mode=2, left_or_right=right_[0])
            left_, right_ = check_jaw(image_, [x_left_, y_], [x_right_, y_])
        return left_, right_
    x_left = locate_width(image_=a_thresh, mode=1, y_=cutNeckHeight)
    x_right = locate_width(image_=a_thresh, mode=2, y_=cutNeckHeight)
    # 在这里我们取消了对下巴的检查,原因在于输入的imageHeight并不能改变
    # cell_left_above, cell_right_above = check_jaw(a_thresh, [x_left, imageHeight], [x_right, imageHeight])
    cell_left_above, cell_right_above = [x_left, cutNeckHeight], [x_right, cutNeckHeight]
    toWidth = x_right - x_left  # 矩形宽
    # 此时我们寻找到了脖子的"宽出来的"两个点,这两个点作为上面的两个点, 接下来寻找下面的两个点
    if per_to_side >1:
        assert ValueError("per_to_side 必须小于1!")
    y_below = int((neckBelow - cutNeckHeight) * per_to_side + cutNeckHeight)  # 定位y轴坐标
    cell_left_below = [locate_width(a_thresh, y_=y_below, mode=1), y_below]
    cell_right_bellow = [locate_width(a_thresh, y_=y_below, mode=2), y_below]
    # 四个点全齐,开始透视变换
    # 需要变换的四个点为 cell_left_above, cell_right_above, cell_left_below, cell_right_bellow
    rect = np.array([cell_left_above, cell_right_above, cell_left_below, cell_right_bellow],
                    dtype='float32')
    # 变化后的坐标点
    dst = np.array([[0, 0], [toWidth, 0], [0 , toHeight], [toWidth, toHeight]],
                    dtype='float32')
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (toWidth, toHeight))
    # 将变换后的图像覆盖到原图上
    final = cover_image(image=warped, background=image, mode=3, x=cell_left_above[0], y=cell_left_above[1])
    return final

def bestJunctionCheck_beta(image:np.ndarray, stepSize:int=4, if_per:bool=False):
    """
    最优衔接点检测算法, 去寻找脖子的"拐点"
    """
    point_k = 1
    _, _, _, a = cv2.split(image)  # 这应该是一个四通道的图像
    height, width = a.shape
    ret, a_thresh = cv2.threshold(a, 127, 255, cv2.THRESH_BINARY)  # 将透明图层二值化
    y_high, y_low, x_left, x_right = get_box_pro(image=image, model=1)  # 直接返回矩阵信息
    def scan(y_:int, max_num:int=2):
        num = 0
        left = False
        right = False
        for x_ in range(width):
            if a_thresh[y_][x_] != 0:
                if x_ < width // 2 and left is False:
                    num += 1
                    left = True
                elif x_ > width // 2 and right is False:
                    num += 1
                    right = True
        return True if num >= max_num else False
    def locate_neck_above():
        """
        定位脖子的尖尖脚
        """
        for y_ in range( y_high - 2, height):
            if scan(y_):
                return y_, y_
    y_high_left, y_high_right = locate_neck_above()
    def locate_width_pro(image_:np.ndarray, y_:int, mode):
        """
        这会是一个生成器,用于生成脖子两边的轮廓
        x_, y_ 是启始点的坐标,每一次寻找都会让y_+1
        mode==1说明是找左边的边,即,image_[y_][x_] == 0 且image_[y_][x_ + 1] !=0 时跳出;
            否则 当image_[y_][x_] != 0 时, x_ - 1; 当image_[y_][x_] == 0 且 image_[y_][x_ + 1] ==0 时x_ + 1
        mode==2说明是找右边的边,即,image_[y_][x_] == 0 且image_[y_][x_ - 1] !=0 时跳出
            否则 当image_[y_][x_] != 0 时, x_ + 1; 当image_[y_][x_] == 0 且 image_[y_][x_ - 1] ==0 时x_ - 1
        """
        y_ += 1
        if mode == 1:
            x_ = 0
            while 0 <= y_ < height and 0 <= x_ < width:
                while image_[y_][x_] != 0 and x_ >= 0:
                    x_ -= 1
                while image_[y_][x_] == 0 and image_[y_][x_ + 1] == 0 and x_ < width - 2:
                    x_ += 1
                yield [y_, x_]
                y_ += 1
        elif mode == 2:
            x_ = width-1
            while 0 <= y_ < height and 0 <= x_ < width:
                while image_[y_][x_] != 0  and x_ < width - 2: x_ += 1
                while image_[y_][x_] == 0 and image_[y_][x_ - 1] == 0 and x_ >= 0: x_ -= 1
                yield [y_, x_]
                y_ += 1
        yield False
    def kGenerator(image_:np.ndarray, mode):
        """
        导数生成器,用来生成每一个点对应的导数
        """
        y_ = y_high_left if mode == 1 else y_high_right
        c_generator = locate_width_pro(image_=image_, y_=y_, mode=mode)
        for cell in c_generator:
            nc = locate_width_pro(image_=image_, y_=cell[0] + stepSize, mode=mode)
            nextCell = next(nc)
            if nextCell is False:
                yield False, False
            else:
                k = (cell[1] - nextCell[1]) / stepSize
                yield k, cell
    def findPt(image_:np.ndarray, mode):
        k_generator = kGenerator(image_=image_, mode=mode)
        k, cell = next(k_generator)
        k_next, cell_next = next(k_generator)
        if k is False:
            raise ValueError("无法找到拐点!")
        while k_next is not False:
            k_next, cell_next = next(k_generator)
            if (k_next < - 1 / stepSize) or k_next > point_k:
                break
            cell = cell_next
        # return int(cell[0] + stepSize / 2)
        return cell[0]
    # 先找左边的拐点:
    pointY_left = findPt(image_=a_thresh, mode=1)
    # 再找右边的拐点:
    pointY_right = findPt(image_=a_thresh, mode=2)
    point = (pointY_left + pointY_right) // 2
    if if_per is True:
        point = (pointY_left + pointY_right) // 2
        return point / (y_low - y_high)
    pointX_left = next(locate_width_pro(image_=a_thresh, y_= point - 1, mode=1))[1]
    pointX_right = next(locate_width_pro(image_=a_thresh, y_=point- 1, mode=2))[1]
    return [pointX_left, point], [pointX_right, point]


def bestJunctionCheck(image:np.ndarray, offset:int, stepSize:int=4):
    """
    最优点检测算算法输入一张脖子图片(无论这张图片是否已经被二值化,我都认为没有被二值化),输出一个小数(脖子最上方与衔接点位置/脖子图像长度)
    与beta版不同的是它新增了一个阈值限定内容.
    对于脖子而言,我我们首先可以定位到上面的部分,然后根据上面的这个点向下进行遍历检测.
    与beta版类似,我们使用一个stepSize来用作斜率的检测
    但是对于遍历检测而言,与beta版不同的是,我们需要对遍历的地方进行一定的限制.
    限制的标准是,如果当前遍历的点的横坐标和起始点横坐标的插值超过了某个阈值,则认为是越界.
    """
    point_k = 1
    _, _, _, a = cv2.split(image)  # 这应该是一个四通道的图像
    height, width = a.shape
    ret, a_thresh = cv2.threshold(a, 127, 255, cv2.THRESH_BINARY)  # 将透明图层二值化
    # 直接返回脖子的位置信息, 修正系数为0, get_box_pro内部也封装了二值化,所以直接输入原图
    y_high, y_low, _, _ = get_box_pro(image=image, model=1, correction_factor=0)
    # 真正有用的只有上下y轴的两个值...
    # 首先当然是确定起始点的位置,我们用同样的scan扫描函数进行行遍历.
    def scan(y_:int, max_num:int=2):
        num = 0
        # 设定两个值,分别代表脖子的左边和右边
        left = False
        right = False
        for x_ in range(width):
            if a_thresh[y_][x_] != 0:
                # 检测左边
                if x_ < width // 2 and left is False:
                    num += 1
                    left = True
                # 检测右边
                elif x_ > width // 2 and right is False:
                    num += 1
                    right = True
        return True if num >= max_num else False
    def locate_neck_above():
        """
        定位脖子的尖尖脚
        """
        # y_high就是脖子的最高点
        for y_ in range(y_high, height):
            if scan(y_):
                return y_
    y_start = locate_neck_above()  # 得到遍历的初始高度
    if y_low - y_start < stepSize: assert ValueError("脖子太小!")
    # 然后获取一下初始的坐标点
    x_left, x_right = 0, width
    for x_left_ in range(0, width):
        if a_thresh[y_start][x_left_] != 0:
            x_left = x_left_
            break
    for x_right_  in range(width -1 , -1, -1):
        if a_thresh[y_start][x_right_] != 0:
            x_right = x_right_
            break
    # 接下来我定义两个生成器,首先是脖子轮廓(向下寻找的)生成器,每进行一次next,生成器会返回y+1的脖子轮廓点
    def contoursGenerator(image_:np.ndarray, y_:int, mode):
        """
        这会是一个生成器,用于生成脖子两边的轮廓
        y_ 是启始点的y坐标,每一次寻找都会让y_+1
        mode==1说明是找左边的边,即,image_[y_][x_] == 0 且image_[y_][x_ + 1] !=0 时跳出;
            否则 当image_[y_][x_] != 0 时, x_ - 1; 当image_[y_][x_] == 0 且 image_[y_][x_ + 1] ==0 时x_ + 1
        mode==2说明是找右边的边,即,image_[y_][x_] == 0 且image_[y_][x_ - 1] !=0 时跳出
            否则 当image_[y_][x_] != 0 时, x_ + 1; 当image_[y_][x_] == 0 且 image_[y_][x_ - 1] ==0 时x_ - 1
        """
        y_ += 1
        try:
            if mode == 1:
                x_ = 0
                while 0 <= y_ < height and 0 <= x_ < width:
                    while image_[y_][x_] != 0 and x_ >= 0: x_ -= 1
                    # 这里其实会有bug,不过可以不管
                    while x_ < width and image_[y_][x_] == 0 and image_[y_][x_ + 1] == 0: x_ += 1
                    yield [y_, x_]
                    y_ += 1
            elif mode == 2:
                x_ = width-1
                while 0 <= y_ < height and 0 <= x_ < width:
                    while x_ < width and image_[y_][x_] != 0: x_ += 1
                    while x_ >= 0 and image_[y_][x_] == 0 and image_[y_][x_ - 1] == 0: x_ -= 1
                    yield [y_, x_]
                    y_ += 1
        # 当处理失败则返回False
        except IndexError:
            yield False
    # 然后是斜率生成器,这个生成器依赖子轮廓生成器,每一次生成轮廓后会计算斜率,另一个点的选取和stepSize有关
    def kGenerator(image_: np.ndarray, mode):
        """
        导数生成器,用来生成每一个点对应的导数
        """
        y_ = y_start
        # 对起始点建立一个生成器, mode=1时是左边轮廓,mode=2时是右边轮廓
        c_generator = contoursGenerator(image_=image_, y_=y_, mode=mode)
        for cell in c_generator:
            # 寻找距离当前cell距离为stepSize的轮廓点
            kc = contoursGenerator(image_=image_, y_=cell[0] + stepSize, mode=mode)
            kCell = next(kc)
            if kCell is False:
                # 寻找失败
                yield False, False
            else:
                # 寻找成功,返回当坐标点和斜率值
                # 对于左边而言,斜率必然是前一个点的坐标减去后一个点的坐标
                # 对于右边而言,斜率必然是后一个点的坐标减去前一个点的坐标
                k = (cell[1] - kCell[1]) / stepSize if mode == 1 else (kCell[1] - cell[1]) / stepSize
                yield k, cell
    # 接着开始写寻找算法,需要注意的是我们是分两边选择的
    def findPt(image_:np.ndarray, mode):
        x_base = x_left if mode == 1 else x_right
        k_generator = kGenerator(image_=image_, mode=mode)
        k, cell = k_generator.__next__()
        if k is False:
            raise ValueError("无法找到拐点!")
        k_next, cell_next = k_generator.__next__()
        while k_next is not False:
            cell = cell_next
            if cell[1] > x_base and mode == 2:
                x_base = cell[1]
            elif cell[1] < x_base and mode == 1:
                x_base = cell[1]
            # 跳出循环的方式一:斜率超过了某个值
            if k_next > point_k:
                print("K out")
                break
            # 跳出循环的方式二:超出阈值
            elif abs(cell[1] - x_base) > offset:
                print("O out")
                break
            k_next, cell_next = k_generator.__next__()
        if abs(cell[1] - x_base) > offset:
            cell[0] = cell[0] - offset - 1
        return cell[0]
    # 先找左边的拐点:
    pointY_left = findPt(image_=a_thresh, mode=1)
    # 再找右边的拐点:
    pointY_right = findPt(image_=a_thresh, mode=2)
    point = min(pointY_right, pointY_left)
    per = (point - y_high) / (y_low - y_high)
    # pointX_left = next(contoursGenerator(image_=a_thresh, y_= point- 1, mode=1))[1]
    # pointX_right = next(contoursGenerator(image_=a_thresh, y_=point - 1, mode=2))[1]
    # return [pointX_left, point], [pointX_right, point]
    return per


def checkSharpCorner(image:np.ndarray):
    _, _, _, a = cv2.split(image)  # 这应该是一个四通道的图像
    height, width = a.shape
    ret, a_thresh = cv2.threshold(a, 127, 255, cv2.THRESH_BINARY)  # 将透明图层二值化
    # 直接返回脖子的位置信息, 修正系数为0, get_box_pro内部也封装了二值化,所以直接输入原图
    y_high, y_low, _, _ = get_box_pro(image=image, model=1, correction_factor=0)
    def scan(y_:int, max_num:int=2):
        num = 0
        # 设定两个值,分别代表脖子的左边和右边
        left = False
        right = False
        for x_ in range(width):
            if a_thresh[y_][x_] != 0:
                # 检测左边
                if x_ < width // 2 and left is False:
                    num += 1
                    left = True
                # 检测右边
                elif x_ > width // 2 and right is False:
                    num += 1
                    right = True
        return True if num >= max_num else False
    def locate_neck_above():
        """
        定位脖子的尖尖脚
        """
        # y_high就是脖子的最高点
        for y_ in range(y_high, height):
            if scan(y_):
                return y_
    y_start = locate_neck_above()
    return y_start

def checkJaw(image:np.ndarray, y_start:int):
    # 寻找"马鞍点"
    _, _, _, a = cv2.split(image)  # 这应该是一个四通道的图像
    height, width = a.shape
    ret, a_thresh = cv2.threshold(a, 127, 255, cv2.THRESH_BINARY)  # 将透明图层二值化
    if width <=1: raise TypeError("图像太小!")
    x_left, x_right = 0, width - 1
    for x_left in range(width):
        if a_thresh[y_start][x_left] != 0:
            while a_thresh[y_start][x_left] != 0: x_left += 1
            break
    for x_right in range(width-1, -1, -1):
        if a_thresh[y_start][x_right] != 0:
            while a_thresh[y_start][x_right] != 0: x_right -= 1
            break
    point_list_y = []
    point_list_x = []
    for x in range(x_left, x_right):
        y = y_start
        while a_thresh[y][x] == 0: y += 1
        point_list_y.append(y)
        point_list_x.append(x)
    y = max(point_list_y)
    x = point_list_x[point_list_y.index(y)]
    return x, y


def checkHairLOrR(cloth_image_input_cut,
                  input_a,
                  neck_a,
                  cloth_image_input_top_y,
                  cutbar_top=0.4,
                  cutbar_bottom=0.5,
                  threshold=0.3):
    """
    本函数用于检测衣服是否被头发遮挡,当前只考虑左右是否被遮挡,即"一刀切"
    返回int
    0代表没有被遮挡
    1代表左边被遮挡
    2代表右边被遮挡
    3代表全被遮挡了
    约定,输入的图像是一张灰度图,且被二值化过.
    """
    def per_darkPoint(img:np.ndarray) -> int:
        """
        用于遍历相加图像上的黑点.
        然后返回黑点数/图像面积
        """
        h, w = img.shape
        sum_darkPoint = 0
        for y in range(h):
            for x in range(w):
                if img[y][x] == 0:
                    sum_darkPoint += 1
        return sum_darkPoint / (h * w)

    if threshold < 0 or threshold > 1: raise TypeError("阈值设置必须在0和1之间!")

    # 裁出cloth_image_input_cut按高度40%～50%的区域-cloth_image_input_cutbar，并转换为A矩阵，做二值化
    cloth_image_input_height = cloth_image_input_cut.shape[0]
    _, _, _, cloth_image_input_cutbar = cv2.split(cloth_image_input_cut[
                                                  int(cloth_image_input_height * cutbar_top):int(
                                                      cloth_image_input_height * cutbar_bottom), :])
    _, cloth_image_input_cutbar = cv2.threshold(cloth_image_input_cutbar, 127, 255, cv2.THRESH_BINARY)

    # 裁出input_image、neck_image的A矩阵的对应区域，并做二值化
    input_a_cutbar = input_a[cloth_image_input_top_y + int(cloth_image_input_height * cutbar_top):
                             cloth_image_input_top_y + int(cloth_image_input_height * cutbar_bottom), :]
    _, input_a_cutbar = cv2.threshold(input_a_cutbar, 127, 255, cv2.THRESH_BINARY)
    neck_a_cutbar = neck_a[cloth_image_input_top_y + int(cloth_image_input_height * cutbar_top):
                           cloth_image_input_top_y + int(cloth_image_input_height * cutbar_bottom), :]
    _, neck_a_cutbar = cv2.threshold(neck_a_cutbar, 50, 255, cv2.THRESH_BINARY)

    # 将三个cutbar合到一起-result_a_cutbar
    input_a_cutbar = np.uint8(255 - input_a_cutbar)
    result_a_cutbar = cv2.add(input_a_cutbar, cloth_image_input_cutbar)
    result_a_cutbar = cv2.add(result_a_cutbar, neck_a_cutbar)

    if_mask = 0
    # 我们将图像 一刀切,分为左边和右边
    height, width = result_a_cutbar.shape  # 一通道图像
    left_image = result_a_cutbar[:, :width//2]
    right_image = result_a_cutbar[:, width//2:]
    if per_darkPoint(left_image) > threshold:
        if_mask = 1
    if per_darkPoint(right_image) > threshold:
        if_mask = 3 if if_mask == 1 else 2
    return if_mask


if __name__ == "__main__":
    for i in range(1, 8):
        img = cv2.imread(f"./neck_temp/neck_image{i}.png", cv2.IMREAD_UNCHANGED)
        # new = transformationNeck(image=img, cutNeckHeight=419,neckBelow=472, toHeight=150)
        # point_list = bestJunctionCheck(img, offset=5, stepSize=3)
        # per = bestJunctionCheck(img, offset=5, stepSize=3)
        # # 返回一个小数的形式, 接下来我将它处理为两个点
        point_list = []
        # y_high_, y_low_, _, _ = get_box_pro(image=img, model=1, conreection_factor=0)
        # _y = y_high_ + int((y_low_ - y_high_) * per)
        # _, _, _, a_ = cv2.split(img)  # 这应该是一个四通道的图像
        # h, w = a_.shape
        # r, a_t = cv2.threshold(a_, 127, 255, cv2.THRESH_BINARY)  # 将透明图层二值化
        # _x = 0
        # for _x in range(w):
        #     if a_t[_y][_x] != 0:
        #         break
        # point_list.append([_x, _y])
        # for _x in range(w - 1, -1, -1):
        #     if a_t[_y][_x] != 0:
        #         break
        # point_list.append([_x, _y])
        y = checkSharpCorner(img)
        point = checkJaw(image=img, y_start=y)
        point_list.append(point)
        new = draw_picture_dots(img, point_list, pen_size=2)
        cv2.imshow(f"{i}", new)
    cv2.waitKey(0)

def find_black(image):
    """
    找黑色点函数，遇到输入矩阵中的第一个黑点，返回它的y值
    """
    height, width = image.shape[0], image.shape[1]
    for i in range(height):
        for j in range(width):
            if image[i, j] < 127:
                return i
    return None

def convert_black_array(image):
    height, width = image.shape[0], image.shape[1]
    mask = np.zeros([height, width])
    for j in range(width):
        for i in range(height):
            if image[i, j] > 127:
                mask[i:, j] = 1
                break
    return mask

def checkLongHair(neck_image, head_bottom_y, neck_top_y):
    """
    长发检测函数，输入为head/neck图像，通过下巴是否为最低点，来判断是否为长发
    :return 0 : 短发
    :return 1 : 长发
    """
    jaw_y = neck_top_y + checkJaw(neck_image, y_start=checkSharpCorner(neck_image))[1]
    if jaw_y >= head_bottom_y-3:
        return 0
    else:
        return 1

def checkLongHair2(head_bottom_y, cloth_top_y):
    if head_bottom_y > cloth_top_y+10:
        return 1
    else:
        return 0


