"""
@author: cuny
@file: idPhotoCreateService.py
@time: 2022/4/3 18:07
@description: 
证件照制作服务文件
"""
from idPhotoCreateUtils import IdPhotoCreateService

ipcs = IdPhotoCreateService()


def service(msg: dict = None, context=None):
    if "send_msg" not in msg:
        print("冷启动/测试模式，不做任何函数处理")
    else:
        ipcs(msg)
    return "Already invoked a function!"


if __name__ == "__main__":
    # 这个路径为本地日常调试用
    obj_key = "hyyx-wx/certificatePhoto/60a5e13da00e6e0001fd53c8/61ace447bb291a20b30796f1/old-image/1640490682087.png"

    # obj_key = "wx/certificatePhoto/60a5e13da00e6e0001fd53c8/61d70e3ba866f7af5df28a37/old-image/1649428342890.jpeg"
    # obj_key = "wx/certificatePhoto/624fc15ca866f7af5ddcdd10/61d70e3ba866f7af5df28a7d/old-image/test.heif"
    # obj_key = "wx/certificatePhoto/61832a9ce99f3b00016883cb/61d70e3ba866f7af5df28a37/old-image/1650332506715.png"
    msg_ = {"uid": "60a5e13da00e6e0001fd53c8",
            "send_msg": {"index": 1,
                         "platform": "test",
                         "obj_key": obj_key,
                         "template_info": {"height": 413, "width": 295, "name": "一寸"},
                         "size": {"name": "一寸",
                                  "w": 295,
                                  "h": 431},
                         "time": "test",
                         }
            }
    service(msg_)
