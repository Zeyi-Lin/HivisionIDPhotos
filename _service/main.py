"""
@author: cuny
@file: main.py
@time: 2022/7/14 15:27
@description: 
服务部署框架的主程序。
我们会将服务框架的功能分为
1. 接收消息，检查参数是否完整
2. 函数运行日志收集，并发送日志
    日志格式规范参见https://www.notion.so/5425320981d945079ebddfe498480447
3. 提供函数调用接口
4. 接入消息接收方，发送消息

此外，我会设计一个本地仿造云端运行环境的方案，方便调试

在函数部署时，需要将_service文件夹一并引入
在这次更新中，我将不再使用HY-sdk中的封装函数，这边决定重新写一遍
"""
from abc import abstractmethod
from .utils import *
import requests
import json


class Service(CosConf):
    def __init__(self):
        """
        类的初始化
        """
        super().__init__()
        # print(type(self).__name__)
        if func_version is None:
            self.host = None  # 本地运行
            print("本地运行...")
        elif func_version == "$LATEST":
            self.host = "socketio-test.hy.hivisionai.com"  # 测试版本的host
            self.bucket = "aifixer-image-test-1306602019"
            print("socket.io 测试版本")
        else:
            self.host = "socketio.hy.hivisionai.com"  # 上线版本host和bucket还没有确定
            self.bucket = "aifixer-image-1306602019"
            print("socket.io 线上版本")
        self.networkProtocol = "https"

    @abstractmethod
    def checkKey(self, msg):
        """
        进行接口校验的函数，如果出错应该抛出ParameterError错误
        Args:
            msg: 前端传入的消息

        Returns:
            校验后的参数，由msg生成必要的参数文件
        此为抽象方法，每个功能函数都不一样
        """
        pass

    @abstractmethod
    def process(self, *args, **kwargs):
        """
        函数运行接口，在这里可以运行自定义的函数
        需要注意的是在这一块需要将异常捕获处理好，供后续的处理
        """
        pass

    def __call__(self, msg: dict, *args, **kwargs):
        """
        服务入口，前端传入的消息以此为入口开始处理。
        """
        pass

    @abstractmethod
    def createMsg(self, status, msg, *args, **kwargs) -> dict:
        """
        通过status和msg生成返回的消息
        Args:
            status: 1或者-1，代表处理成功或者失败
            msg: 传入的消息

        Returns:
            回传dict
        """
        msg['status'] = True if status >= 1 else False  # 最好还是用bool
        msg['id'] = "async-back-msg"
        # ----------------下面的参数为必须存在但是需要修改的-------------------- #
        msg['type'] = None
        msg["format"] = None
        # ---------------------------------------------------------------- #
        return msg

    def sendMsg(self, message,  connect_info: tuple):
        """
        往前端发送处理信息，json格式
        作为后端架构的过渡版本，目前发送发送消息同时兼容websocket和socket.IO两种。
        考虑到尽量不改功能函数中的部署代码，传入的参数被改为tuple形式，返回checkKey中的(uid, connectionID)字段
        Args:
            message: 处理信息
            connect_info: (uid, connectionID)，两者不同时为None
        Returns:
            None
        """
        uid, connectionID = connect_info
        assert (uid is not None or connectionID is not None), "(uid, connectionID)，两者不同时为None"
        print("[环境变量 SCF_FUNCTIONVERSION] ", func_version)
        # 有两种发送方式，分别是websocket发送和socket.IO发送，我们会根据传入的
        if connectionID is None:  # socket.IO发送
            url = f"{self.networkProtocol}://{self.host}/api/emit/user/{uid}?type=call"  # query需要传入一个type字段，字段值固定为call
            req = requests.post(url, json=message)  # 以post方式发送
        else:  # websocket发送
            retmsg = {'websocket': {}}
            retmsg['websocket']['action'] = "data send"
            retmsg['websocket']['secConnectionID'] = connect_info[1]
            retmsg['websocket']['dataType'] = 'text'
            retmsg['websocket']['data'] = json.dumps(message)
            req = requests.post(self.sendBackHost, json=retmsg)
        print("回传消息:", req)
        return req

    def load_sess_generator(self, sess_obj_name: str):
        """
        模型生成器，我们可以通过本方法返回的对象进行模型的加载
        与常规模型加载不同的是，在调用本方法以后返回的是一个生成器，并不会直接加载模型，当再次调用时（使用魔术方法__next__()）,才会进行模型加载。
        这种情况比较适合调用api时使用本地调用的方案，一般情况下这是无感的。
        当然，本生成器需要和匿名对象装饰器 @property 进行连用
        Args:
            sess_obj_name: 对象名称，为被 @property 修饰的方法名称

        Returns:
            加载好的模型对象
        """
        while True:
            yield getattr(self, sess_obj_name)

