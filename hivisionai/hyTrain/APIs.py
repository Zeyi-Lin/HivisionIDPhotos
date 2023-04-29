import requests, os
import json
import hashlib, base64, hmac
import sys
import oss2
from aliyunsdkimageseg.request.v20191230.SegmentBodyRequest import SegmentBodyRequest
from aliyunsdkimageseg.request.v20191230.SegmentSkinRequest import SegmentSkinRequest
from aliyunsdkfacebody.request.v20191230.DetectFaceRequest import DetectFaceRequest
from aliyunsdkcore.client import AcsClient

# 头像抠图参数配置
def params_of_head(photo_base64, photo_type):
    print ('测试头像抠图接口 ...')
    host = 'https://person.market.alicloudapi.com'
    uri = '/segment/person/headrgba' # 头像抠图返回透明PNG图
    # uri = '/segment/person/head'   # 头像抠图返回alpha图
    # uri = '/segment/person/headborder' # 头像抠图返回带白边的透明PNG图
    return host, uri, {
        'photo': photo_base64,
        'type': photo_type,
        'face_required': 0, # 可选，检测是否必须带有人脸才进行抠图处理，0为检测，1为不检测，默认为0
        'border_ratio': 0.3, # 可选，仅带白边接口可用，
                             # 在头像边缘增加白边（或者其他颜色）宽度，取值为0-0.5，
                             # 这个宽度是相对于图片宽度和高度最大值的比例，
                             # 比如原图尺寸为640x480，border_ratio为0.2，
                             # 则添加的白边的宽度为：max(640,480) * 0.2 = 96个像素
        'margin_color': '#ff0000' # 可选，仅带白边接口可用，
                                  # 在头像边缘增加边框的颜色，默认为白色

    }

# 头像抠图API
def wanxing_get_head_api(file_name='/home/parallels/Desktop/change_cloth/input_image/03.jpg',
                     output_path="./head.png",
                     app_key='204014294',
                     secret="pI2uo7AhCFjnaZWYrCCAEjmsZJbK6vzy",
                     stage='RELEASE'):
    info = sys.version_info
    if info[0] < 3:
        is_python3 = False
    else:
        is_python3 = True

    with open(file_name, 'rb') as fp:
        photo_base64 = base64.b64encode(fp.read())
    if is_python3:
        photo_base64 = photo_base64.decode('utf8')

    _, photo_type = os.path.splitext(file_name)
    photo_type = photo_type.lstrip('.')
    # print(photo_type)
    # print(photo_base64)

    # host, uri, body_json = params_of_portrait_matting(photo_base64, photo_type)
    # host, uri, body_json = params_of_object_matting(photo_base64)
    # host, uri, body_json = params_of_idphoto(photo_base64, photo_type)
    host, uri, body_json = params_of_head(photo_base64, photo_type)
    # host, uri,  body_json = params_of_crop(photo_base64)
    api = host + uri

    body = json.dumps(body_json)
    md5lib = hashlib.md5()
    if is_python3:
        md5lib.update(body.encode('utf8'))
    else:
        md5lib.update(body)
    body_md5 = md5lib.digest()
    body_md5 = base64.b64encode(body_md5)
    if is_python3:
        body_md5 = body_md5.decode('utf8')

    method = 'POST'
    accept = 'application/json'
    content_type = 'application/octet-stream; charset=utf-8'
    date_str = ''
    headers = ''

    string_to_sign = method + '\n' \
                    + accept + '\n' \
                    + body_md5 + '\n' \
                    + content_type + '\n' \
                    + date_str + '\n' \
                    + headers \
                    + uri
    if is_python3:
        signed = hmac.new(secret.encode('utf8'),
                          string_to_sign.encode('utf8'),
                          digestmod=hashlib.sha256).digest()
    else:
        signed = hmac.new(secret, string_to_sign, digestmod=hashlib.sha256).digest()
    signed = base64.b64encode(signed)
    if is_python3:
        signed = signed.decode('utf8')

    headers = {
        'Accept': accept,
        'Content-MD5': body_md5,
        'Content-Type': content_type,
        'X-Ca-Key': app_key,
        'X-Ca-Stage': stage,
        'X-Ca-Signature': signed
    }
    #print signed


    resp = requests.post(api, data=body, headers=headers)
    # for u,v in resp.headers.items():
    #     print(u+": " + v)
    try:
        res = resp.content
        res = json.loads(res)
        # print ('res:', res)
        if str(res['status']) == '0':
            # print ('成功!')
            file_object = requests.get(res["data"]["result"])
            # print(file_object)
            with open(output_path, 'wb') as local_file:
                local_file.write(file_object.content)

            # image = cv2.imread("./test_head.png", -1)
            # return image
        else:
            pass
            # print ('失败!')
    except:
        print('failed parse:', resp)

# 阿里云抠图API
def aliyun_human_matting_api(input_path, output_path, type="human"):
    auth = oss2.Auth('LTAI5tP2NxdzSFfpKYxZFCuJ', 'VzbGdUbRawuMAitekP3ORfrw0i3NEX')
    bucket = oss2.Bucket(auth, 'https://oss-cn-shanghai.aliyuncs.com', 'huanying-api')
    key = os.path.basename(input_path)
    origin_image = input_path
    try:
        bucket.put_object_from_file(key, origin_image, headers={"Connection":"close"})
    except Exception as e:
        print(e)

    url = bucket.sign_url('GET', key, 10 * 60)
    client = AcsClient('LTAI5tP2NxdzSFfpKYxZFCuJ', 'VzbGdUbRawuMAitekP3ORfrw0i3NEX', 'cn-shanghai')
    if type == "human":
        request = SegmentBodyRequest()
    elif type == "skin":
        request = SegmentSkinRequest()
    request.set_accept_format('json')
    request.set_ImageURL(url)

    try:
        response = client.do_action_with_exception(request)
        response_dict = eval(str(response, encoding='utf-8'))
        if type == "human":
            output_url = response_dict['Data']['ImageURL']
        elif type == "skin":
            output_url = response_dict['Data']['Elements'][0]['URL']
        file_object = requests.get(output_url)
        with open(output_path, 'wb') as local_file:
            local_file.write(file_object.content)
            bucket.delete_object(key)
    except Exception as e:
        print(e)
        response = client.do_action_with_exception(request)
        response_dict = eval(str(response, encoding='utf-8'))
        print(response_dict)
        output_url = response_dict['Data']['ImageURL']
        file_object = requests.get(output_url)
        with open(output_path, 'wb') as local_file:
            local_file.write(file_object.content)
            bucket.delete_object(key)

# 阿里云人脸检测API
def aliyun_face_detect_api(input_path, type="human"):
    auth = oss2.Auth('LTAI5tP2NxdzSFfpKYxZFCuJ', 'VzbGdUbRawuMAitekP3ORfrw0i3NEX')
    bucket = oss2.Bucket(auth, 'https://oss-cn-shanghai.aliyuncs.com', 'huanying-api')
    key = os.path.basename(input_path)
    origin_image = input_path
    try:
        bucket.put_object_from_file(key, origin_image, headers={"Connection":"close"})
    except Exception as e:
        print(e)

    url = bucket.sign_url('GET', key, 10 * 60)
    client = AcsClient('LTAI5tP2NxdzSFfpKYxZFCuJ', 'VzbGdUbRawuMAitekP3ORfrw0i3NEX', 'cn-shanghai')
    if type == "human":
        request = DetectFaceRequest()
    request.set_accept_format('json')
    request.set_ImageURL(url)
    try:
        response = client.do_action_with_exception(request)
        response_json = json.loads(str(response, encoding='utf-8'))
        print(response_json["Data"]["PoseList"][-1])
        bucket.delete_object(key)
        return response_json["Data"]["PoseList"][-1]
    except Exception as e:
        print(e)

if __name__ == "__main__":
    wanxing_get_head_api()