"""
@author: cuny
@file: aliyun_api.py
@time: 2022/7/21 13:41
@description:
本部分会保存一些阿里云的api接口，并且也会写好重试机制，方便使用。
"""
from hivisionai.hycv.utils import CV2Bytes
from hivisionai.hyService.error import ProcessError
import requests
from alibabacloud_imageseg20191230.client import Client as imageseg20191230Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_imageseg20191230 import models as imageseg_20191230_models
import Tea.exceptions
import oss2
import time
import json
from .__config import HUMAN_MATTING_CONFIG_PATH
import random


class AliyunUser(object):
    def __init__(self, user_config_path: str = None):
        if user_config_path is None:
            self.__userConfig: dict = json.load(open(HUMAN_MATTING_CONFIG_PATH, "r", encoding="utf8"))
        else:
            self.__userConfig: dict = json.load(open(user_config_path, "r", encoding="utf8"))
        self.userNameList = list(self.__userConfig.keys())

    @property
    def userAll(self):
        return self.__userConfig

    @property
    def userRandom(self):
        x = random.randint(0, len(self.userNameList) - 1)
        # tmp = self.userNameList[x]
        return self.__userConfig[self.userNameList[x]]


class ApiError(ProcessError):
    def __init__(self, err, diary=None, status_id: str = "1500"):
        super().__init__(err)
        if diary is None:
            self.diary = diary
        else:
            self.diary = diary
        self.err = err
        self.status_id = status_id


class AliyunHumanMatting(object):
    def __init__(self, input_image_bytes, key: str, user_conf, b_r_max: int = 5, a_r_max: int = 3):
        """
        初始化类
        Args:
            input_image_bytes: 需要被上传的图像字节流
            key: 图像路径
            user_conf: api用户配置
            b_r_max: bucket最大重试次数
            a_r_max: api请求最大次数
        """
        self.user_conf = user_conf
        self.key = key
        self.data = input_image_bytes
        self.b_r_max = b_r_max
        self.a_r_max = a_r_max
        self.access_id = None
        self.access_key = None
        self.bucket_name = None
        self.bucket = None
        self.api_diary = {"status": False,  # True为处理成功，False为处理失败
                          "bucket_put_times": 0,  # oss请求放置文件次数
                          "bucket_sign_times": 0,  # oss请求sign文件次数
                          "bucket_delete_times": 0,  # oss请求删除文件次数
                          "api_request_times": 0,  # 请求抠图api的次数
                          "error_dec": []  # 错误描述列表，代表的是每一次请求（如果失败）的描述
                          }

    def init_conf(self):
        # 初始化一些配置信息，并将data上传至bucket
        user = self.user_conf.userRandom
        self.access_id = user["secretId"]
        self.access_key = user["secretKey"]
        auth = oss2.Auth(user["secretId"], user["secretKey"])
        self.bucket_name = user['oss_bucket']
        self.bucket = oss2.Bucket(auth, 'https://oss-cn-shanghai.aliyuncs.com', user['oss_bucket'])
        self.bucket_retry("put")
        return self.bucket_retry("sign")

    def bucket_retry(self, method: str):
        """
        封装oss的存储桶对象的方法，分为三种：
        put_object，放置对象
        delete_object, 删除对象
        sign_url，生成url
        作为一个闭包函数，只是单纯用于减少代码量。
        Args:
            method: 方法
        """
        # 定义参数
        if method == "put":
            method = "put_object"
            diary_key = "bucket_put_times"
            kwargs = {"key": self.key, "data":self.data}
        elif method == "delete":
            method = "delete_object"
            diary_key = "bucket_delete_times"
            kwargs = {"key": self.key}
        else:
            method = "sign_url"
            diary_key = "bucket_sign_times"
            kwargs = {"key": self.key, "method": "GET", "expires": 60}
        m = getattr(self.bucket, method)  # 获取对象方法，需要注意的是三个方法中传入的参数也是不一样的
        for j in range(self.b_r_max):
            self.api_diary[diary_key] += 1
            try:
                return_data = m(**kwargs)
                print(f"[{method} success]，请求次数：{self.api_diary['bucket_put_times']}")
                return return_data
            except oss2.exceptions.RequestError:  # 上传失败，重试
                time.sleep(0.1)

    def run(self):
        """
        请求阿里云api，需要经过以下几步：
        1. 配置信息，生成bucket对象
        2. 上传图片，获得url
        3. 生成api的client，请求api
        4. 重试机制
        5. 获得图像/报错
        Returns:
            PNG图像
        """
        image_url = self.init_conf()  # 1和2
        while self.api_diary["api_request_times"] < self.a_r_max:
            # 生成open_api客户端
            config = open_api_models.Config(access_key_id=self.access_id, access_key_secret=self.access_key)
            # 访问的域名
            config.endpoint = f'imageseg.cn-shanghai.aliyuncs.com'
            client = imageseg20191230Client(config)
            # 如果下面增加一个return_form参数，则可以填mask（返回单通道黑白图）；
            # crop，则返回裁剪之后的四通道PNG图（裁掉边缘空白区域）
            # 如果设置为whiteBK，则返回白底图
            # 此外如果不设置或者设置为其他值，则返回原尺寸的四通道PNG
            # 需要注意的是输入的图像的最大边长不能超过2k
            # 多个人像似乎并没有什么错误
            segment_body_request = imageseg_20191230_models.SegmentBodyRequest(image_url=image_url)
            self.api_diary["api_request_times"] += 1
            try:
                # 下面这句将有可能会触发流控
                result_body = client.segment_body(segment_body_request).body
                result_image = CV2Bytes.byte_cv2(requests.get(result_body.data.image_url).content, -1)
                # 得到最终图像，删除在oss中的原本图像，结束
                print(f"[api require success]，请求次数：{self.api_diary['api_request_times']}")
                self.bucket_retry("delete")
                self.api_diary["status"] = True
                return result_image, self.api_diary  # 函数唯一出口
            except Tea.exceptions.UnretryableException as e:  # 出现这个错误似乎无法通过单纯的重试解决
                print(type(e), f", 尝试切换accessId， 次数：{self.api_diary['api_request_times']}")
                self.bucket_retry("delete")  # 删除原本存储桶的数据
                time.sleep(0.1)
                image_url = self.init_conf()
            except Tea.exceptions.TeaException as e:  # 触发流控，qps超限制
                # 触发错误，这里的错误主要分为两类，一类是"无人像"另一类是"流控"
                if e.code == 'InvalidFile.Content':  # 无人像，或者函数出错
                    print(e)
                    self.api_diary["error_dec"].append(str(e))
                    raise ApiError("阿里云api请求出错，图片无人像!", self.api_diary, "1101")
                elif e.code == 'Throttling':  # 流控，触发重试机制
                    self.api_diary["error_dec"].append(str(e))
                    time.sleep(0.5)
                else:  # 未知错误，抛出异常，再次重试
                    print("未知错误! ")
                    print(type(e), e)
                    self.api_diary["error_dec"].append(str(e))
                    time.sleep(0.1)
                    # raise ApiError("阿里云api请求出错，未知错误!", api_diary)
        self.bucket_retry("delete")
        print("请求失败!重试次数过多!")
        print(self.api_diary)
        raise ApiError("阿里云api请求出错，重试超时!", self.api_diary, "1204")


def aliyun_human_matting_api(input_image_bytes, key: str, user_conf=None, b_r_max: int = 4, a_r_max: int = 4):
    """
    利用阿里云api进行人像抠图，首先需要注意的是，阿里云的api必须与oss进行联动，
    我们往oss中上传文件以后，需要获取图像的url，然后再利用api得到值
    需要注意的是几乎所有的错误都可以通过重试解决，但是有一个错误似乎需要通过重新配置client解决。
    此函数只有一个唯一出口，其余接口都会报错
    Args:
        input_image_bytes: 输入的图像，为字节流形式
        key: 上传的图像名称
        user_conf: 用户类，里面包含所有的可以使用的用户信息，可以不输入，不输入的话会使用默认配置
        a_r_max: 请求api的最大次数
        b_r_max: 请求bucket的最大次数
    Returns:
        处理后的图片
    """
    if user_conf is None:
        user_conf = AliyunUser()
    ahm = AliyunHumanMatting(input_image_bytes, key, user_conf, b_r_max, a_r_max)
    return ahm.run()

