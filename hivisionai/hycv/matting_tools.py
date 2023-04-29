import numpy as np
from PIL import Image
import cv2
import onnxruntime
from .tensor2numpy import NNormalize, NTo_Tensor, NUnsqueeze
from .vision import image2bgr


def read_modnet_image(input_image, ref_size=512):
    im = Image.fromarray(np.uint8(input_image))
    width, length = im.size[0], im.size[1]
    im = np.asarray(im)
    im = image2bgr(im)
    im = cv2.resize(im, (ref_size, ref_size), interpolation=cv2.INTER_AREA)
    im = NNormalize(im, mean=np.array([0.5, 0.5, 0.5]), std=np.array([0.5, 0.5, 0.5]))
    im = NUnsqueeze(NTo_Tensor(im))

    return im, width, length


def get_modnet_matting(input_image, checkpoint_path="./test.onnx", ref_size=512):

    print("checkpoint_path:", checkpoint_path)
    sess = onnxruntime.InferenceSession(checkpoint_path)

    input_name = sess.get_inputs()[0].name
    output_name = sess.get_outputs()[0].name

    im, width, length = read_modnet_image(input_image=input_image, ref_size=ref_size)

    matte = sess.run([output_name], {input_name: im})
    matte = (matte[0] * 255).astype('uint8')
    matte = np.squeeze(matte)
    mask = cv2.resize(matte, (width, length), interpolation=cv2.INTER_AREA)
    b, g, r = cv2.split(np.uint8(input_image))

    output_image = cv2.merge((b, g, r, mask))

    return output_image