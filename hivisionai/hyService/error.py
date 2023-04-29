"""
@author: cuny
@fileName: error.py
@create_time: 2022/03/10 下午3:14
@introduce:
保存一些定义的错误类型
"""
class ProcessError(Exception):
    def __init__(self, err):
        super().__init__(err)
        self.err = err
    def __str__(self):
        return self.err

class WrongImageType(TypeError):
    def __init__(self, err):
        super().__init__(err)
        self.err = err
    def __str__(self):
        return self.err