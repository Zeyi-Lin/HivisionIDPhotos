# _lib本身不绑定任何第三方依赖，我们可以按照需求进行绑定
from .__config import HY_HUMAN_MATTING_WEIGHTS_PATH, HY_HEADNECK_MATTING_WEIGHTS_PATH, HY_HEAD_MATTING_WEIGHTS_PATH

# 对于一些依赖包，只要没有使用到，都是可以省略的
# 人脸关键点检测，省略dlib
try:
    from .face_detector_68 import FaceDetection68, FaceError
    from .utils import draw_face_points
except ImportError as e:
    print(e)
    pass

# 阿里云api，省略aliyun-sdk
try:
    from .aliyun_api import aliyun_human_matting_api, AliyunUser, ApiError
except ImportError as e:
    print(e)
    pass

# face++ api，省略numpy/opencv
try:
    from .megvii_api import megvii_face_detector, MEGVIIFace83
except ImportError as e:
    print(e)
    pass
