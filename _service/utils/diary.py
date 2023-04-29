"""
@author: cuny
@file: diary.py
@time: 2022/7/14 15:40
@description: 
日志收集文件
"""
import os
import json
import datetime
from .cos import CosConf
from .variable import config_path, func_version
local_path = os.path.dirname(__file__)


class FuncDiary(CosConf):
    # 如果碰见的是这几个用户，则不上传文件
    filter_dict = {"60a5e13da00e6e0001fd53c8": "Cuny",
                   "612c290f3a9af4000170faad": "守望平凡",
                   "614de96e1259260001506d6c": "林泽毅-焕影一新"}

    def __init__(self, func_name: str):
        """
        日志类的实例化
        Args:
            func_name: 功能名称，影响了日志投递的路径
        """
        super().__init__()
        # 配置文件路径,默认是函数运行的路径下的conf文件夹
        self.error_dict = json.load(open(os.path.join(config_path, "func_error_conf.json"), "r", encoding="utf8"))
        self.__up: str = f"wx/invokeFunction_c/{datetime.datetime.now().strftime('%Y/%m/%d/%H')}/{func_name}/"  # 上传路径
        self.func_name: str = func_name
        # 下面这个属性是的日志名称的前缀
        self.__start_time = datetime.datetime.now().timestamp()  # 用于
        h_point = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y/%m/%d/%H'), '%Y/%m/%d/%H')
        h_point_timestamp = h_point.timestamp()
        self.__prefix = int(self.__start_time - h_point_timestamp).__str__() + "_"  # 距离整点有多少秒
        self.__uid = "unknown"  # 当uid为unknown的时候，一般情况为接口参数错误
        self.__diary = None

    def __str__(self):
        return f"<{self.func_name}> DIARY for {self.__uid}"

    @property
    def content(self) -> dict:
        return self.__diary

    @content.setter
    def content(self, value: dict):
        """
        我们可以通过content设置日志文件的内容，但是只能设置一次
        Args:
            value: 将content的内容设置为value 字典
        """
        if not isinstance(value, dict):
            self.__diary = {}
            return
        if value is not None and "status_id" in value:
            raise KeyError("status字段已被默认占用，请在日志信息中更换字段名称!")
        if self.__diary is None:
            self.__diary = value
        else:
            raise PermissionError("为了减小日志对整体代码的影响，<content>只能被覆写一次！")

    def uploadDiary_COS(self, status_id: str, uid: str = "", suffix: str = ""):
        """
        上传处理日志
        Args:
            status_id: 为且只为func_error_conf中定义的字段，日志的内容中必然有这个字段
            uid: 用户的uid，默认为""，代表用户uid不存在
            suffix: 日志后缀，可以自定义，如果为""则代表没有后缀
        """
        self.__uid = uid
        if uid in self.filter_dict.keys() or func_version is None:
            print(f"{self}取消上传，开发者模式.")
            return
        if self.__diary is None:
            self.__diary = {"status_id": self.error_dict[status_id]}
        else:
            self.__diary["status_id"] = self.error_dict[status_id]
        self.__up += f"{status_id == '0000'}/{self.__uid}/"  # 如果参数错误则有可能造成命名重复，不过没什么关系
        interval = int(10 * (datetime.datetime.now().timestamp() - self.__start_time))
        prefix = self.__prefix + status_id + "_" + interval.__str__()  # 距离整点的时间_statusId_处理时间
        name = prefix + "_" + suffix if len(suffix) != 0 else prefix  # 日志名称
        self.uploadFile_COS(buffer=json.dumps(self.__diary), key=self.__up + name, bucket="hy-hcy-data-logs-1306602019")
        print(f"{self}上传成功.")
