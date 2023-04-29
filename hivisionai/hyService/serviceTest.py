"""
用于测试云端或者本地服务的运行是否成功
"""
import requests
import functools
import cv2
import time

def httpPostTest(url, msg:dict):
    """
    以post请求访问api,携带msg(dict)信息
    """
    re = requests.post(url=url, json=msg)
    print(re.text)
    return re


def localTestImageFunc(path):
    """
    在本地端测试算法,需要注意的是本装饰器只支持测试和图像相关算法
    path代表测试图像的路径,其余参数请写入被装饰的函数中,并且只支持标签形式输入
    被测试的函数的第一个输入参数必须为图像矩阵(以cv2读入)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(**kwargs):
            start = time.time()
            image = cv2.imread(path)
            image_out = func(image) if len(kwargs) == 0 else func(image, kwargs)
            print("END.\n处理时间(不计算加载模型时间){}秒:".format(round(time.time()-start, 2)))
            cv2.imshow("test", image_out)
            cv2.waitKey(0)
        return wrapper
    return decorator
