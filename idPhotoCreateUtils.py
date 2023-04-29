"""
@author: cuny
@file: idPhotoCreateUtils.py
@time: 2022/4/4 14:37
@description: 
证件照制作服务类，新增了人脸矫正函数
"""
from _service import *
from hivisionai.hycv.utils import CV2Bytes
from _lib import AliyunUser, HY_HUMAN_MATTING_WEIGHTS_PATH
from face_judgement_align import IDphotos_create
from error import IDError
import onnxruntime
import time
import cv2


class IdPhotoCreateService(Service, CV2Bytes):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置预加载模型参数，dlib、抠头、抠脖子等等
        print("证件照制作对象初始化...")
        start = time.time()
        self.__human_sess = None
        self.fd68 = None  # 为本地人脸检测预留接口
        self.user = AliyunUser()
        print(f"初始化完毕，总耗时{round(time.time() - start, 2)}秒")

    @property
    def human_sess(self):
        if self.__human_sess is None:
            print("加载模型...")
            self.__human_sess = onnxruntime.InferenceSession(HY_HUMAN_MATTING_WEIGHTS_PATH)
        return self.__human_sess

    def createMsg(self, status, msg, *args, **kwargs):
        """
        本方法用于创建一个用于发送到WebSocket客户端的数据
        输入的信息部分,需要有如下几个参数:
        1. id,固定为"return-result"
        2. status,如果输入为1则status=true, 如果输入为-1则status=false
        3. obj_key, 图片的云端路径, 这是输入的msg本身自带的
        """
        msg['status'] = True if status >= 1 else False  # 最好还是用bool
        msg['id'] = "async-back-msg"
        msg['type'] = "certificatePhoto"
        msg["format"] = "png"
        return msg

    def process(self,
                image_pre,
                oss_image_name,
                w=295,
                h=413,
                beauty=False,
                upload_path_hd=None,
                upload_path_common=None,
                if_upload: bool = True):
        """
        处理函数
        Args:
            image_pre: 输入的原图
            oss_image_name: 上传阿里云api的尺寸图像
            w: 证件照尺寸-宽
            h: 证件照尺寸-高
            beauty: 是否美颜
            upload_path_hd: 高清图上传cos路径
            upload_path_common: 标清图上传cos路径
            if_upload: 是否上传，不同选择返回的参数不同

        Returns:
            1. if if_upload is True:
                函数会将图像上传，不返回图像仅返回参数
            2. if if_upload is False:
                函数不会将图像上传，返回图像和一些参数
        """
        print("oss_name:", oss_image_name)
        result_image_HD, result_image, _, \
            typography_arr, typography_rotate, \
            relative_x, relative_y, w, h, id_temp_info = IDphotos_create(image_pre,
                                                                         size=(h, w),
                                                                         head_height_ratio=0.45,
                                                                         head_measure_ratio=0.2,
                                                                         align=True,
                                                                         beauty=beauty,
                                                                         fd68=self.fd68,
                                                                         human_sess=self.load_sess_generator("human_sess"),
                                                                         oss_image_name=oss_image_name,
                                                                         user=self.user)

        if if_upload:
            # 上传图像,云端模式
            print("[图像尺寸]: ", result_image_HD.shape)
            result_image_HD_byte = self.cv2_byte(result_image_HD, imageType=".png")
            self.uploadFile_COS(buffer=result_image_HD_byte, key=upload_path_hd)
            result_image_byte = self.cv2_byte(result_image, imageType=".png")
            self.uploadFile_COS(buffer=result_image_byte, key=upload_path_common)
            print("[image send success]")
            return typography_arr, typography_rotate, relative_x, relative_y, w, h, id_temp_info
        else:
            # 不上传图像，返回处理结果
            return result_image_HD, result_image, typography_arr, typography_rotate, relative_x, relative_y, w, h, id_temp_info

    def checkKey(self, msg):
        print("GET", msg)
        try:
            uid, send_msg = msg["uid"], msg["send_msg"]
            connectionID = None
        except KeyError:
            connectionID, send_msg = msg["connectionID"], msg["send_msg"]
            uid = send_msg["uid"]
        download_path: str = send_msg["obj_key"]  # 获得cos下载路径
        # platform = send_msg["platform"] if "platform" in send_msg else "undefined"  # 换装次数
        # 获取需要被制作的证件照尺寸
        template_info = send_msg["template_info"]
        w, h, name = int(template_info["width"]), int(template_info["height"]), template_info["name"]
        # 获得cos回传传路径
        img_format = send_msg['obj_key'][send_msg['obj_key'].rfind('.') + 1:]
        tr = send_msg['obj_key'].replace(img_format, 'png')
        upload_path_hd: str = tr.replace("old-image", "new-image/hd")
        upload_path_common: str = tr.replace("old-image", "new-image/common")
        image_name = f"{uid}_{upload_path_common.split('/')[-1]}"
        send_msg["hd_key"] = upload_path_hd  # 回传云端结果图片路径（高清照）
        send_msg["common_key"] = upload_path_common  # 回传云端结果图片路径（高清照）
        return (w, h, name), (download_path, upload_path_hd, upload_path_common), image_name, send_msg, (
            uid, connectionID)

    def __call__(self, msg, *args, **kwargs):
        """
        证件照制作算法服务函数
        """
        # --------------初始化一些数据-------------- #
        print(msg)
        backMsg, uid = None, ""
        status_id = "0000"
        funcDiary = FuncDiary("certificatePhoto")
        # noinspection PyBroadException
        try:
            (w, h, name), (download_path, upload_path_hd, upload_path_common), image_name, backMsg, uid = self.checkKey(
                msg)
            # ----------------数据获取完毕-------------- #
            # 开始处理
            print("start...")
            # start = time.time()
            resp = self.downloadFile_COS(download_path, if_read=False)  # 下载图片
            image_byte = resp['Body'].get_raw_stream().read()  # 读取二进制图片
            # 将二进制图片转为cv2格式, 无损格式
            image_pre = self.byte_cv2(image_byte, flags=cv2.IMREAD_COLOR)
            # cv2.imwrite(f"test_image/cloud_img.{img_format}", image_pre)
            # np_arr = np.frombuffer(image_byte, np.uint8)
            # image = cv2.imdecode(np_arr, -1)
            # 数据图片下载完毕，开始功能处理
            print("processing...")
            # 证件照制作
            # 返回的w和h与输入的w和h不是一回事
            backMsg["typography_arr"], backMsg["typography_rotate"], \
                backMsg["relative_x"], backMsg["relative_y"], \
                backMsg["w_create"], backMsg["h_create"], \
                backMsg["id_temp_info"] = self.process(image_pre=image_pre,
                                                       oss_image_name=image_name,
                                                       w=w,
                                                       h=h,
                                                       upload_path_hd=upload_path_hd,
                                                       upload_path_common=upload_path_common)
        except IDError as e:
            # ------------处理失败， 错误类型有两种--------------- #
            # 一是人像错误，这时候用户上传了一张无人像（太糊）或者两个以上人像的照片
            # 此时face_num = 0或者2， back_msg["status"] is True
            # 此外为未知错误，此时face_num 不存在于back_msg
            # back_msg["status"] is False
            # ----------------------------------------------- #
            # print(type(e), e.err)
            status_id = e.status_id
            if e.face_num != -1:
                backMsg["face_num"] = e.face_num
                backMsg = self.createMsg(status=1, msg=backMsg)  # back_msg["status"] is True
            else:
                # 抠图失败
                backMsg = self.createMsg(status=-1, msg=backMsg)
            print("fail!")
        except cv2.error:
            status_id = "1103"
            backMsg = self.createMsg(status=-1, msg=backMsg)
            print("fail!")
        except Exception as e:
            status_id = "1500"
            print("[ERROR]  ", e)
            backMsg["problem"] = str(e)
            backMsg = self.createMsg(status=-1, msg=backMsg)
            print("fail!")
        else:
            # 无错误
            backMsg = self.createMsg(status=1, msg=backMsg)
            # 处理成功,在回传消息中添加成功对应消息
            backMsg["face_num"] = 1  # 人脸个数，处理成功的话必然是1
            print("success!")
        finally:
            # print(back_msg)  # 打印回传数据，方便调试
            self.sendMsg(backMsg, uid)
            # ------------------投递日志------------------- #
            funcDiary.content = backMsg
            funcDiary.uploadDiary_COS(status_id=status_id, uid=uid[0])
            # ------------------投递结束------------------- #
            assert status_id == "0000", f"函数出现异常: {status_id}"


def load_sess(idPhotoCreateService: IdPhotoCreateService):
    while True:
        yield idPhotoCreateService.human_sess
