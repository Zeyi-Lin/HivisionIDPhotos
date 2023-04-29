import cv2
import os
import onnxruntime
from .mtcnn_onnx.detector import detect_faces
from .tensor2numpy import *
from PIL import Image
import requests
from os.path import exists


def download_img(img_url, base_dir):
    print("Downloading Onnx Model in:", img_url)
    r = requests.get(img_url, stream=True)
    filename = img_url.split("/")[-1]
    # print(r.status_code) # 返回状态码
    if r.status_code == 200:
        open(f'{base_dir}/{filename}', 'wb').write(r.content) # 将内容写入图片
        print(f"Download Finshed -- {filename}")
    del r

class BBox(object):
    # bbox is a list of [left, right, top, bottom]
    def __init__(self, bbox):
        self.left = bbox[0]
        self.right = bbox[1]
        self.top = bbox[2]
        self.bottom = bbox[3]
        self.x = bbox[0]
        self.y = bbox[2]
        self.w = bbox[1] - bbox[0]
        self.h = bbox[3] - bbox[2]

    # scale to [0,1]
    def projectLandmark(self, landmark):
        landmark_= np.asarray(np.zeros(landmark.shape))
        for i, point in enumerate(landmark):
            landmark_[i] = ((point[0]-self.x)/self.w, (point[1]-self.y)/self.h)
        return landmark_

    # landmark of (5L, 2L) from [0,1] to real range
    def reprojectLandmark(self, landmark):
        landmark_= np.asarray(np.zeros(landmark.shape))
        for i, point in enumerate(landmark):
            x = point[0] * self.w + self.x
            y = point[1] * self.h + self.y
            landmark_[i] = (x, y)
        return landmark_


def face_detect_mtcnn(input_image, color_key=None, filter=None):
    """
    Inputs:
    - input_image: OpenCV Numpy.array
    - color_key: 当color_key等于"RGB"时,将不进行转换操作
    - filter：当filter等于True时，将抛弃掉置信度小于0.98或人脸框面积小于3600的人脸
    return:
    - faces: 带有人脸信息的变量
    - landmarks: face alignment
    """
    if color_key != "RGB":
        input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)

    input_image = Image.fromarray(input_image)
    faces, landmarks = detect_faces(input_image)

    if filter:
        face_clean = []
        for face in faces:
            confidence = face[-1]
            x1 = face[0]
            y1 = face[1]
            x2 = face[2]
            y2 = face[3]
            w = x2 - x1 + 1
            h = y2 - y1 + 1
            measure = w * h
            if confidence >= 0.98 and measure > 3600:
                # 如果检测到的人脸置信度小于0.98或人脸框面积小于3600,则抛弃该人脸
                face_clean.append(face)
        faces = face_clean

    return faces, landmarks


def mtcnn_bbox(face, width, height):
    x1 = face[0]
    y1 = face[1]
    x2 = face[2]
    y2 = face[3]
    w = x2 - x1 + 1
    h = y2 - y1 + 1

    size = int(max([w, h]) * 1.1)
    cx = x1 + w // 2
    cy = y1 + h // 2
    x1 = cx - size // 2
    x2 = x1 + size
    y1 = cy - size // 2
    y2 = y1 + size

    dx = max(0, -x1)
    dy = max(0, -y1)
    x1 = max(0, x1)
    y1 = max(0, y1)

    edx = max(0, x2 - width)
    edy = max(0, y2 - height)
    x2 = min(width, x2)
    y2 = min(height, y2)

    return x1, x2, y1, y2, dx, dy, edx, edy


def mtcnn_cropped_face(face_box, image, width, height):
    x1, x2, y1, y2, dx, dy, edx, edy = mtcnn_bbox(face_box, width, height)
    new_bbox = list(map(int, [x1, x2, y1, y2]))
    new_bbox = BBox(new_bbox)
    cropped = image[new_bbox.top:new_bbox.bottom, new_bbox.left:new_bbox.right]
    if (dx > 0 or dy > 0 or edx > 0 or edy > 0):
        cropped = cv2.copyMakeBorder(cropped, int(dy), int(edy), int(dx), int(edx), cv2.BORDER_CONSTANT, 0)
    return cropped, new_bbox


def face_landmark_56(input_image, faces_box=None):
    basedir = os.path.dirname(os.path.realpath(__file__)).split("mtcnn.py")[0]
    mean = np.asarray([0.485, 0.456, 0.406])
    std = np.asarray([0.229, 0.224, 0.225])
    base_url = "https://linimages.oss-cn-beijing.aliyuncs.com/"

    if not exists(f"{basedir}/mtcnn_onnx/weights/landmark_detection_56_se_external.onnx"):
        # download onnx model
        download_img(img_url=base_url + "landmark_detection_56_se_external.onnx",
                     base_dir=f"{basedir}/mtcnn_onnx/weights")

    ort_session = onnxruntime.InferenceSession(f"{basedir}/mtcnn_onnx/weights/landmark_detection_56_se_external.onnx")
    out_size = 56

    height, width, _ = input_image.shape
    if faces_box is None:
        faces_box, _ = face_detect_mtcnn(input_image)

    if len(faces_box) == 0:
        print('NO face is detected!')
        return None
    else:
        landmarks = []
        for face_box in faces_box:
            cropped, new_bbox = mtcnn_cropped_face(face_box, input_image, width, height)
            cropped_face = cv2.resize(cropped, (out_size, out_size))

            test_face = NNormalize(cropped_face, mean=mean, std=std)
            test_face = NTo_Tensor(test_face)
            test_face = NUnsqueeze(test_face)

            ort_inputs = {ort_session.get_inputs()[0].name: test_face}
            ort_outs = ort_session.run(None, ort_inputs)

            landmark = ort_outs[0]

            landmark = landmark.reshape(-1, 2)
            landmark = new_bbox.reprojectLandmark(landmark)
            landmarks.append(landmark)

        return landmarks



REFERENCE_FACIAL_POINTS = [
    [30.29459953, 51.69630051],
    [65.53179932, 51.50139999],
    [48.02519989, 71.73660278],
    [33.54930115, 92.3655014],
    [62.72990036, 92.20410156]
]

DEFAULT_CROP_SIZE = (96, 112)


def _umeyama(src, dst, estimate_scale=True, scale=1.0):
    """Estimate N-D similarity transformation with or without scaling.
    Parameters
    ----------
    src : (M, N) array
        Source coordinates.
    dst : (M, N) array
        Destination coordinates.
    estimate_scale : bool
        Whether to estimate scaling factor.
    Returns
    -------
    T : (N + 1, N + 1)
        The homogeneous similarity transformation matrix. The matrix contains
        NaN values only if the problem is not well-conditioned.
    References
    ----------
    .. [1] "Least-squares estimation of transformation parameters between two
            point patterns", Shinji Umeyama, PAMI 1991, :DOI:`10.1109/34.88573`
    """

    num = src.shape[0]
    dim = src.shape[1]

    # Compute mean of src and dst.
    src_mean = src.mean(axis=0)
    dst_mean = dst.mean(axis=0)

    # Subtract mean from src and dst.
    src_demean = src - src_mean
    dst_demean = dst - dst_mean

    # Eq. (38).
    A = dst_demean.T @ src_demean / num

    # Eq. (39).
    d = np.ones((dim,), dtype=np.double)
    if np.linalg.det(A) < 0:
        d[dim - 1] = -1

    T = np.eye(dim + 1, dtype=np.double)

    U, S, V = np.linalg.svd(A)

    # Eq. (40) and (43).
    rank = np.linalg.matrix_rank(A)
    if rank == 0:
        return np.nan * T
    elif rank == dim - 1:
        if np.linalg.det(U) * np.linalg.det(V) > 0:
            T[:dim, :dim] = U @ V
        else:
            s = d[dim - 1]
            d[dim - 1] = -1
            T[:dim, :dim] = U @ np.diag(d) @ V
            d[dim - 1] = s
    else:
        T[:dim, :dim] = U @ np.diag(d) @ V

    if estimate_scale:
        # Eq. (41) and (42).
        scale = 1.0 / src_demean.var(axis=0).sum() * (S @ d)
    else:
        scale = scale

    T[:dim, dim] = dst_mean - scale * (T[:dim, :dim] @ src_mean.T)
    T[:dim, :dim] *= scale

    return T, scale


class FaceWarpException(Exception):
    def __str__(self):
        return 'In File {}:{}'.format(
            __file__, super.__str__(self))


def get_reference_facial_points_5(output_size=None,
                                inner_padding_factor=0.0,
                                outer_padding=(0, 0),
                                default_square=False):
    tmp_5pts = np.array(REFERENCE_FACIAL_POINTS)
    tmp_crop_size = np.array(DEFAULT_CROP_SIZE)

    # 0) make the inner region a square
    if default_square:
        size_diff = max(tmp_crop_size) - tmp_crop_size
        tmp_5pts += size_diff / 2
        tmp_crop_size += size_diff

    if (output_size and
            output_size[0] == tmp_crop_size[0] and
            output_size[1] == tmp_crop_size[1]):
        print('output_size == DEFAULT_CROP_SIZE {}: return default reference points'.format(tmp_crop_size))
        return tmp_5pts

    if (inner_padding_factor == 0 and
            outer_padding == (0, 0)):
        if output_size is None:
            print('No paddings to do: return default reference points')
            return tmp_5pts
        else:
            raise FaceWarpException(
                'No paddings to do, output_size must be None or {}'.format(tmp_crop_size))

    # check output size
    if not (0 <= inner_padding_factor <= 1.0):
        raise FaceWarpException('Not (0 <= inner_padding_factor <= 1.0)')

    if ((inner_padding_factor > 0 or outer_padding[0] > 0 or outer_padding[1] > 0)
            and output_size is None):
        output_size = tmp_crop_size * \
                      (1 + inner_padding_factor * 2).astype(np.int32)
        output_size += np.array(outer_padding)
        print('              deduced from paddings, output_size = ', output_size)

    if not (outer_padding[0] < output_size[0]
            and outer_padding[1] < output_size[1]):
        raise FaceWarpException('Not (outer_padding[0] < output_size[0]'
                                'and outer_padding[1] < output_size[1])')

    # 1) pad the inner region according inner_padding_factor
    # print('---> STEP1: pad the inner region according inner_padding_factor')
    if inner_padding_factor > 0:
        size_diff = tmp_crop_size * inner_padding_factor * 2
        tmp_5pts += size_diff / 2
        tmp_crop_size += np.round(size_diff).astype(np.int32)

    # print('              crop_size = ', tmp_crop_size)
    # print('              reference_5pts = ', tmp_5pts)

    # 2) resize the padded inner region
    # print('---> STEP2: resize the padded inner region')
    size_bf_outer_pad = np.array(output_size) - np.array(outer_padding) * 2
    # print('              crop_size = ', tmp_crop_size)
    # print('              size_bf_outer_pad = ', size_bf_outer_pad)

    if size_bf_outer_pad[0] * tmp_crop_size[1] != size_bf_outer_pad[1] * tmp_crop_size[0]:
        raise FaceWarpException('Must have (output_size - outer_padding)'
                                '= some_scale * (crop_size * (1.0 + inner_padding_factor)')

    scale_factor = size_bf_outer_pad[0].astype(np.float32) / tmp_crop_size[0]
    # print('              resize scale_factor = ', scale_factor)
    tmp_5pts = tmp_5pts * scale_factor
    #    size_diff = tmp_crop_size * (scale_factor - min(scale_factor))
    #    tmp_5pts = tmp_5pts + size_diff / 2
    tmp_crop_size = size_bf_outer_pad
    # print('              crop_size = ', tmp_crop_size)
    # print('              reference_5pts = ', tmp_5pts)

    # 3) add outer_padding to make output_size
    reference_5point = tmp_5pts + np.array(outer_padding)
    tmp_crop_size = output_size
    # print('---> STEP3: add outer_padding to make output_size')
    # print('              crop_size = ', tmp_crop_size)
    # print('              reference_5pts = ', tmp_5pts)
    #
    # print('===> end get_reference_facial_points\n')

    return reference_5point


def get_affine_transform_matrix(src_pts, dst_pts):
    tfm = np.float32([[1, 0, 0], [0, 1, 0]])
    n_pts = src_pts.shape[0]
    ones = np.ones((n_pts, 1), src_pts.dtype)
    src_pts_ = np.hstack([src_pts, ones])
    dst_pts_ = np.hstack([dst_pts, ones])

    A, res, rank, s = np.linalg.lstsq(src_pts_, dst_pts_)

    if rank == 3:
        tfm = np.float32([
            [A[0, 0], A[1, 0], A[2, 0]],
            [A[0, 1], A[1, 1], A[2, 1]]
        ])
    elif rank == 2:
        tfm = np.float32([
            [A[0, 0], A[1, 0], 0],
            [A[0, 1], A[1, 1], 0]
        ])

    return tfm


def warp_and_crop_face(src_img,
                       facial_pts,
                       reference_pts=None,
                       crop_size=(96, 112),
                       align_type='smilarity'): #smilarity cv2_affine affine
    if reference_pts is None:
        if crop_size[0] == 96 and crop_size[1] == 112:
            reference_pts = REFERENCE_FACIAL_POINTS
        else:
            default_square = False
            inner_padding_factor = 0
            outer_padding = (0, 0)
            output_size = crop_size

            reference_pts = get_reference_facial_points_5(output_size,
                                                        inner_padding_factor,
                                                        outer_padding,
                                                        default_square)

    ref_pts = np.float32(reference_pts)
    ref_pts_shp = ref_pts.shape
    if max(ref_pts_shp) < 3 or min(ref_pts_shp) != 2:
        raise FaceWarpException(
            'reference_pts.shape must be (K,2) or (2,K) and K>2')

    if ref_pts_shp[0] == 2:
        ref_pts = ref_pts.T

    src_pts = np.float32(facial_pts)
    src_pts_shp = src_pts.shape
    if max(src_pts_shp) < 3 or min(src_pts_shp) != 2:
        raise FaceWarpException(
            'facial_pts.shape must be (K,2) or (2,K) and K>2')

    if src_pts_shp[0] == 2:
        src_pts = src_pts.T

    if src_pts.shape != ref_pts.shape:
        raise FaceWarpException(
            'facial_pts and reference_pts must have the same shape')

    if align_type == 'cv2_affine':
        tfm = cv2.getAffineTransform(src_pts[0:3], ref_pts[0:3])
        tfm_inv = cv2.getAffineTransform(ref_pts[0:3], src_pts[0:3])
    elif align_type == 'affine':
        tfm = get_affine_transform_matrix(src_pts, ref_pts)
        tfm_inv = get_affine_transform_matrix(ref_pts, src_pts)
    else:
        params, scale = _umeyama(src_pts, ref_pts)
        tfm = params[:2, :]

        params, _ = _umeyama(ref_pts, src_pts, False, scale=1.0/scale)
        tfm_inv = params[:2, :]

    face_img = cv2.warpAffine(src_img, tfm, (crop_size[0], crop_size[1]), flags=3)

    return face_img, tfm_inv


if __name__ == "__main__":
    image = cv2.imread("/home/parallels/Desktop/IDPhotos/input_image/03.jpg")
    face_detect_mtcnn(image)


