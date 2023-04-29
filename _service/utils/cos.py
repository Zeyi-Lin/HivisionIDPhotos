"""
@author: cuny
@file: cos.py
@time: 2022/7/14 15:45
@description: 
腾讯云cos服务文件，对腾讯云服务进行二次封装
"""
import os
import json

try:  # 加上这个try的原因在于本地环境和云函数端的import形式有所不同
    from qcloud_cos import CosConfig
    from qcloud_cos import CosS3Client
except ImportError:
    try:
        from qcloud_cos_v5 import CosConfig
        from qcloud_cos_v5 import CosS3Client
    except ImportError:
        raise ImportError("本地调用COS库时，请下载腾讯云COS相关代码包:pip install cos-python-sdk-v5")
from .variable import config_path


class CosConf(object):
    """
    从安全的角度出发,将一些默认配置文件不会保存在git中，而是在Notion中。
    关于配置文件的配置方式，详见Notion
    配置文件用于用于连接cos存储桶,下载配置文件.
    那么就不用再次下载了,也不用输入id和key
    事实上这只需要运行一次,因为配置文件将会被下载至源码文件夹中
    如果要自定义路径,请在继承的子类中编写__init__函数,将service_path定向到指定路径
    """

    def __init__(self) -> None:
        # 下面这些参数是类的共享参数
        self.__SECRET_ID = None  # 服务的id
        self.__SECRET_KEY = None  # 服务的key
        self.__REGION = None  # 服务的存储桶地区
        self.__TOKEN = None  # 服务的token,目前一直是None
        self.__SCHEME = None  # 服务的访问协议,默认实际上是https
        self.__BUCKET = None  # 服务的存储桶
        self.__SERVICE_CONFIG = None  # 服务的配置文件对象，以dict形式呈现
        self.__HOST = None  # websocket连接
        self.service_path = os.path.join(config_path, "service_config.json")  # 配置文件路径
        self.service_default_download = False  # 是否在每次访问配置的时候都重新下载文件

    @property
    def service_config(self) -> dict:
        if self.__SERVICE_CONFIG is None:
            with open(self.service_path, "r", encoding="utf8") as f:
                self.__SERVICE_CONFIG = json.load(f)
        return self.__SERVICE_CONFIG

    @property
    def client(self):
        client_config = CosConfig(Region=self.region,
                                  SecretId=self.secret_id,
                                  SecretKey=self.secret_key,
                                  Token=self.token,
                                  Scheme=self.scheme)
        return CosS3Client(client_config)

    def get_key(self, key: str):
        try:
            data = self.service_config[key]
            if data == "None":
                return None
            else:
                return data
        except KeyError:
            print(f"\033[31m没有对应键值{key},默认返回None\033[0m")
            return None

    @property
    def secret_id(self):
        if self.__SECRET_ID is None:
            self.__SECRET_ID = self.get_key("SECRET_ID")
        return self.__SECRET_ID

    @secret_id.setter
    def secret_id(self, value: str):
        self.__SECRET_ID = value

    @property
    def secret_key(self):
        if self.__SECRET_KEY is None:
            self.__SECRET_KEY = self.get_key("SECRET_KEY")
        return self.__SECRET_KEY

    @secret_key.setter
    def secret_key(self, value: str):
        self.__SECRET_KEY = value

    @property
    def region(self):
        if self.__REGION is None:
            self.__REGION = self.get_key("REGION")
        return self.__REGION

    @region.setter
    def region(self, value: str):
        self.__REGION = value

    @property
    def token(self):
        # if self.__TOKEN is None:
        #     self.__TOKEN = self.get_key("TOKEN")
        # 这里可以注释掉
        return self.__TOKEN

    @token.setter
    def token(self, value: str):
        self.__TOKEN = value

    @property
    def scheme(self):
        if self.__SCHEME is None:
            self.__SCHEME = self.get_key("SCHEME")
        return self.__SCHEME

    @scheme.setter
    def scheme(self, value: str):
        self.__SCHEME = value

    @property
    def bucket(self):
        if self.__BUCKET is None:
            self.__BUCKET = self.get_key("BUCKET")
        return self.__BUCKET

    @bucket.setter
    def bucket(self, value):
        self.__BUCKET = value

    @property
    def sendBackHost(self):
        if self.__HOST is None:
            self.__HOST = self.get_key("HOST")
        return self.__HOST

    @sendBackHost.setter
    def sendBackHost(self, value):
        self.__HOST = value

    def downloadFile_COS(self, key, bucket: str = None, if_read: bool = False):
        """
        从COS下载对象(二进制数据), 如果下载失败就返回None
        """
        CosBucket = self.bucket if bucket is None else bucket
        try:
            # 将本类的Debug继承给抛弃了
            # self.debug_print(f"Download from {CosBucket}", font_color="blue")
            obj = self.client.get_object(
                Bucket=CosBucket,
                Key=key
            )
            if if_read is True:
                data = obj["Body"].get_raw_stream().read()  # byte
                return data
            else:
                return obj
        except Exception as e:
            print(f"\033[31m下载失败! 错误描述:{e}\033[0m")
            return None

    def showFileList_COS_base(self, key, bucket, marker: str = ""):
        """
        返回cos存储桶内部的某个文件夹的内部名称
        :param key: cos云端的存储路径
        :param bucket: cos存储桶名称，如果没指定名称（None）就会寻找默认的存储桶
        :param marker: 标记,用于记录上次查询到哪里了
        ps:如果需要修改默认的存储桶配置，请在代码运行的时候加入代码 s.bucket = 存储桶名称 （s是对象实例）
        返回的内容存储在response["Content"]，不过返回的数据大小是有限制的，具体内容还是请看官方文档。
        """
        response = self.client.list_objects(
            Bucket=bucket,
            Prefix=key,
            Marker=marker
        )
        return response

    def showFileList_COS(self, key, bucket: str = None) -> list:
        """
        实现查询存储桶中所有对象的操作，因为cos的sdk有返回数据包大小的限制，所以我们需要进行一定的改动
        """
        marker = ""
        file_list = []
        CosBucket = self.bucket if bucket is None else bucket
        while True:  # 轮询
            response = self.showFileList_COS_base(key, CosBucket, marker)
            try:
                file_list.extend(response["Contents"])
            except KeyError:
                pass
            if response['IsTruncated'] == 'false':  # 接下来没有数据了,就退出
                break
            file_list.extend(response["Contents"])
            marker = response['NextMarker']
        return file_list

    def uploadFile_COS(self, buffer, key, bucket: str = None):
        """
        从COS上传数据,需要注意的是必须得是二进制文件
        """
        CosBucket = self.bucket if bucket is None else bucket
        self.client.put_object(
            Bucket=CosBucket,
            Body=buffer,
            Key=key
        )
        return True
