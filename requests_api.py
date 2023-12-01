import requests
import base64
from PIL import Image
from io import BytesIO


url = "http://127.0.0.1:8080/generate_layout_photos"  # 替换为实际的接口URL

files = {'input_image': (open('downloaded_image_add_background.png', 'rb'))}  # 替换为实际的文件路径和文件名
data = {"size": str((413, 295))}

response = requests.post(url, data=data, files=files)

if response.status_code == 200:
    # 获取Base64编码的图像数据
    print(response.json())
    base64_image_data = response.json()["image"]

    # 解码Base64数据并保存为PNG文件
    img_data = base64.b64decode(base64_image_data)
    img = Image.open(BytesIO(img_data))

    # 保存为本地PNG文件
    img.save("downloaded_image_layout.png", "PNG")
    print("Image saved as 'downloaded_image.png'")
else:
    print("Failed to retrieve image from the API.")
