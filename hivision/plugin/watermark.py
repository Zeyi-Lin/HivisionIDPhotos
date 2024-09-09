"""
Reference: https://gist.github.com/Deali-Axy/e22ea79bfbe785f9017b2e3cd7fdb3eb
"""

import enum
import os
import math
import textwrap
from PIL import Image, ImageFont, ImageDraw, ImageEnhance, ImageChops
import os

base_path = os.path.abspath(os.path.dirname(__file__))


class WatermarkerStyles(enum.Enum):
    """水印样式"""

    STRIPED = 1  # 斜向重复
    CENTRAL = 2  # 居中


class Watermarker(object):
    """图片水印工具"""

    def __init__(
        self,
        input_image: Image.Image,
        text: str,
        style: WatermarkerStyles,
        angle=30,
        color="#8B8B1B",
        font_file="青鸟华光简琥珀.ttf",
        opacity=0.15,
        size=50,
        space=75,
        chars_per_line=8,
        font_height_crop=1.2,
    ):
        """_summary_

        Parameters
        ----------
        input_image : Image.Image
            PIL图片对象
        text : str
            水印文字
        style : WatermarkerStyles
            水印样式
        angle : int, optional
            水印角度, by default 30
        color : str, optional
            水印颜色, by default "#8B8B1B"
        font_file : str, optional
            字体文件, by default "青鸟华光简琥珀.ttf"
        font_height_crop : float, optional
            字体高度裁剪比例, by default 1.2
        opacity : float, optional
            水印透明度, by default 0.15
        size : int, optional
            字体大小, by default 50
        space : int, optional
            水印间距, by default 75
        chars_per_line : int, optional
            每行字符数, by default 8
        """
        self.input_image = input_image
        self.text = text
        self.style = style
        self.angle = angle
        self.color = color
        self.font_file = os.path.join(base_path, "font", font_file)
        self.font_height_crop = font_height_crop
        self.opacity = opacity
        self.size = size
        self.space = space
        self.chars_per_line = chars_per_line
        self._result_image = None

    @staticmethod
    def set_image_opacity(image: Image, opacity: float):
        alpha = image.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        image.putalpha(alpha)
        return image

    @staticmethod
    def crop_image_edge(image: Image):
        bg = Image.new(mode="RGBA", size=image.size)
        diff = ImageChops.difference(image, bg)
        bbox = diff.getbbox()
        if bbox:
            return image.crop(bbox)
        return image

    def _add_mark_striped(self):
        origin_image = self.input_image.convert("RGBA")
        width = len(self.text) * self.size
        height = round(self.size * self.font_height_crop)
        watermark_image = Image.new(mode="RGBA", size=(width, height))
        draw_table = ImageDraw.Draw(watermark_image)
        draw_table.text(
            (0, 0),
            self.text,
            fill=self.color,
            font=ImageFont.truetype(self.font_file, size=self.size),
        )
        watermark_image = Watermarker.crop_image_edge(watermark_image)
        Watermarker.set_image_opacity(watermark_image, self.opacity)

        c = int(math.sqrt(origin_image.size[0] ** 2 + origin_image.size[1] ** 2))
        watermark_mask = Image.new(mode="RGBA", size=(c, c))
        y, idx = 0, 0
        while y < c:
            x = -int((watermark_image.size[0] + self.space) * 0.5 * idx)
            idx = (idx + 1) % 2
            while x < c:
                watermark_mask.paste(watermark_image, (x, y))
                x += watermark_image.size[0] + self.space
            y += watermark_image.size[1] + self.space

        watermark_mask = watermark_mask.rotate(self.angle)
        origin_image.paste(
            watermark_mask,
            (int((origin_image.size[0] - c) / 2), int((origin_image.size[1] - c) / 2)),
            mask=watermark_mask.split()[3],
        )
        return origin_image

    def _add_mark_central(self):
        origin_image = self.input_image.convert("RGBA")
        text_lines = textwrap.wrap(self.text, width=self.chars_per_line)
        text = "\n".join(text_lines)
        width = len(text) * self.size
        height = round(self.size * self.font_height_crop * len(text_lines))
        watermark_image = Image.new(mode="RGBA", size=(width, height))
        draw_table = ImageDraw.Draw(watermark_image)
        draw_table.text(
            (0, 0),
            text,
            fill=self.color,
            font=ImageFont.truetype(self.font_file, size=self.size),
        )
        watermark_image = Watermarker.crop_image_edge(watermark_image)
        Watermarker.set_image_opacity(watermark_image, self.opacity)

        c = int(math.sqrt(origin_image.size[0] ** 2 + origin_image.size[1] ** 2))
        watermark_mask = Image.new(mode="RGBA", size=(c, c))
        watermark_mask.paste(
            watermark_image,
            (
                int((watermark_mask.width - watermark_image.width) / 2),
                int((watermark_mask.height - watermark_image.height) / 2),
            ),
        )
        watermark_mask = watermark_mask.rotate(self.angle)

        origin_image.paste(
            watermark_mask,
            (
                int((origin_image.width - watermark_mask.width) / 2),
                int((origin_image.height - watermark_mask.height) / 2),
            ),
            mask=watermark_mask.split()[3],
        )
        return origin_image

    @property
    def image(self):
        if not self._result_image:
            if self.style == WatermarkerStyles.STRIPED:
                self._result_image = self._add_mark_striped()
            elif self.style == WatermarkerStyles.CENTRAL:
                self._result_image = self._add_mark_central()
        return self._result_image

    def save(self, file_path: str, image_format: str = "png"):
        with open(file_path, "wb") as f:
            self.image.save(f, image_format)


# Gradio 接口
def watermark_image(
    image,
    text,
    style,
    angle,
    color,
    opacity,
    size,
    space,
):
    # 创建 Watermarker 实例
    watermarker = Watermarker(
        input_image=image,
        text=text,
        style=(
            WatermarkerStyles.STRIPED
            if style == "STRIPED"
            else WatermarkerStyles.CENTRAL
        ),
        angle=angle,
        color=color,
        opacity=opacity,
        size=size,
        space=space,
    )

    # 返回带水印的图片
    return watermarker.image


if __name__ == "__main__":
    import gradio as gr

    iface = gr.Interface(
        fn=watermark_image,
        inputs=[
            gr.Image(type="pil", label="上传图片", height=400),
            gr.Textbox(label="水印文字"),
            gr.Radio(choices=["STRIPED", "CENTRAL"], label="水印样式"),
            gr.Slider(minimum=0, maximum=360, value=30, label="水印角度"),
            gr.ColorPicker(label="水印颜色"),
            gr.Slider(minimum=0, maximum=1, value=0.15, label="水印透明度"),
            gr.Slider(minimum=10, maximum=100, value=50, label="字体大小"),
            gr.Slider(minimum=10, maximum=200, value=75, label="水印间距"),
        ],
        outputs=gr.Image(type="pil", label="带水印的图片", height=400),
        title="图片水印工具",
        description="上传一张图片，添加水印并下载。",
    )

    iface.launch()
