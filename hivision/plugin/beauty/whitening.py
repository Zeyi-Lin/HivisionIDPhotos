import cv2
import numpy as np
import os
import gradio as gr


class LutWhite:
    CUBE64_ROWS = 8
    CUBE64_SIZE = 64
    CUBE256_SIZE = 256
    CUBE_SCALE = CUBE256_SIZE // CUBE64_SIZE

    def __init__(self, lut_image):
        self.lut = self._create_lut(lut_image)

    def _create_lut(self, lut_image):
        reshape_lut = np.zeros(
            (self.CUBE256_SIZE, self.CUBE256_SIZE, self.CUBE256_SIZE, 3), dtype=np.uint8
        )
        for i in range(self.CUBE64_SIZE):
            tmp = i // self.CUBE64_ROWS
            cx = (i % self.CUBE64_ROWS) * self.CUBE64_SIZE
            cy = tmp * self.CUBE64_SIZE
            cube64 = lut_image[cy : cy + self.CUBE64_SIZE, cx : cx + self.CUBE64_SIZE]
            if cube64.size == 0:
                continue
            cube256 = cv2.resize(cube64, (self.CUBE256_SIZE, self.CUBE256_SIZE))
            reshape_lut[i * self.CUBE_SCALE : (i + 1) * self.CUBE_SCALE] = cube256
        return reshape_lut

    def apply(self, src):
        b, g, r = src[:, :, 0], src[:, :, 1], src[:, :, 2]
        return self.lut[b, g, r]


class MakeWhiter:
    def __init__(self, lut_image):
        self.lut_white = LutWhite(lut_image)

    def run(self, src: np.ndarray, strength: int) -> np.ndarray:
        strength = np.clip(strength / 10.0, 0, 1)
        if strength <= 0:
            return src
        img = self.lut_white.apply(src[:, :, :3])
        return cv2.addWeighted(src[:, :, :3], 1 - strength, img, strength, 0)


base_dir = os.path.dirname(os.path.abspath(__file__))
default_lut = cv2.imread(os.path.join(base_dir, "lut/lut_origin.png"))
make_whiter = MakeWhiter(default_lut)


def make_whitening(image, strength):
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    iteration = strength // 10
    bias = strength % 10

    for i in range(iteration):
        image = make_whiter.run(image, 10)

    image = make_whiter.run(image, bias)

    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def make_whitening_png(image, strength):
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGBA2BGRA)

    b, g, r, a = cv2.split(image)
    bgr_image = cv2.merge((b, g, r))

    b_w, g_w, r_w = cv2.split(make_whiter.run(bgr_image, strength))
    output_image = cv2.merge((b_w, g_w, r_w, a))

    return cv2.cvtColor(output_image, cv2.COLOR_RGBA2BGRA)


# 启动Gradio应用
if __name__ == "__main__":
    demo = gr.Interface(
        fn=make_whitening,
        inputs=[
            gr.Image(type="pil", image_mode="RGBA", label="Input Image"),
            gr.Slider(0, 30, step=1, label="Whitening Strength"),
        ],
        outputs=gr.Image(type="pil"),
        title="Image Whitening Demo",
        description="Upload an image and adjust the whitening strength to see the effect.",
    )
    demo.launch()
