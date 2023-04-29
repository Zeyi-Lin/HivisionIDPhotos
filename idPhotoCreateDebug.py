"""
@author: cuny
@file: idPhotoCreateDebug.py
@time: 2022/4/25 17:43
@description: 
证件照制作的本地调试文件
"""
import time
import cv2
from hivisionai.hyService.utils import Debug
from hivisionai.hycv.vision import resize_image_esp
from idPhotoCreateUtils import IdPhotoCreateService

cbs = IdPhotoCreateService()
db = Debug()
msg = {"uid": "60a5e13da00e6e0001fd53c8",
       "send_msg": {"index": 1,
                    "platform": "test",
                    "obj_key": "wx/certificatePhoto/62b31e4fa866f7af5d361390/61d70e3ba866f7af5df28a3b/old-image/xyz165621950.png",
                    "template_info": {"height": 192, "width": 144, "name": "一寸"},
                    "cloth_number": "girl02",
                    "size": {"name": "一寸",
                             "w": 144,
                             "h": 192},
                    "time": "test",
                    "uid": "60a5e13da00e6e0001fd53c8",
                    }
       }

# ----------------- 本地调试方式 ----------------- #

image_byte = open("../idPhotoCreate/test_image/21.jpg", "rb").read()
# ---------------------------------------------- #
# 开始从云端下载图像，首先获取一些基本数据，这一行基本别动
(w, h, name), (download_path, upload_path_hd, upload_path_common), image_name, send_msg, \
    (uid, connectionID) = cbs.checkKey(msg)
print("upload_path_common", upload_path_common)
# 在这一步我们获得到了用户的数据1
image_pre = cbs.byte_cv2(image_byte, flags=cv2.IMREAD_COLOR)
image_pre = resize_image_esp(image_pre, esp=2000)
# 数据图片下载完毕，开始功能处理
db.debug_print("INFO: processing...", font_color="yellow")
# 开始处理
db.debug_print("INFO: 取消上传照片...", font_color="yellow")
start = time.time()
result_image_HD, result_image, typography_arr, typography_rotate, relative_x, relative_y, w, h, id_temp_info = \
    cbs.process(image_pre=image_pre,
                oss_image_name=image_name,
                w=w,
                h=h,
                beauty=False,
                upload_path_hd=upload_path_hd,
                upload_path_common=upload_path_common,
                if_upload=False)

db.debug_print(f"INFO: 图像处理时间: {round(time.time() - start, 2)}秒", font_color="blue")
db.debug_print("INFO: success.", font_color="green")
# cv2.imshow("test", result_image)
# cv2.waitKey(0)
# ---------------------------------------------- #
cv2.imwrite("result_image_standard.png", result_image)
cv2.imwrite("result_image_HD.png", result_image_HD)
