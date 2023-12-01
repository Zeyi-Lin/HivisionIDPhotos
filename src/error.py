"""
@author: cuny
@file: error.py
@time: 2022/4/7 15:50
@description: 
定义证件照制作的错误类
"""
from hivisionai.hyService.error import ProcessError


class IDError(ProcessError):
    def __init__(self, err, diary=None, face_num=-1, status_id: str = "1500"):
        """
        用于报错
        Args:
            err: 错误描述
            diary: 函数运行日志，默认为None
            face_num: 告诉此时识别到的人像个数，如果为-1则说明为未知错误
        """
        super().__init__(err)
        if diary is None:
            diary = {}
        self.err = err
        self.diary = diary
        self.face_num = face_num
        self.status_id = status_id

