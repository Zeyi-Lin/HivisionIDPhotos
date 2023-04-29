"""
定义hycv的一些错误类型，其实和hyService大致相同
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