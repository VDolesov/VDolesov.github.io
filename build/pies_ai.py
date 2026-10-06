import os
import sys

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from photos_v9 import GROUND

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
RAW = os.path.join(HERE, "sources", "ai")

ITEMS = {"801": "801.png", "802": "802.png", "803": "803.png", "752": "752.png"}
ABOUT = "about.png"
ABOUT_CROP = (250, 0, 1344, 768)


def about():
    im = Image.open(os.path.join(RAW, ABOUT)).convert("RGB").crop(ABOUT_CROP)
    w, h = 1200, 842
    im = im.resize((w, h), Image.LANCZOS)
    im = ImageEnhance.Brightness(im).enhance(.86)
    im = ImageEnhance.Contrast(im).enhance(1.05)
    r, g, b = im.split()
    b = b.point(lambda v: int(v * .94))
    im = Image.merge("RGB", (r, g, b))
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    e = np.clip(np.hypot((xs / w - .5) / .85, (ys / h - .5) / .95), 0, 1) ** 1.5
    mask = Image.fromarray(((1 - e * .6) * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(50))
    return Image.composite(im, Image.new("RGB", (w, h), GROUND), mask)


def main():
    path = os.path.join(APP, "assets", "about.jpg")
    about().save(path, quality=84, optimize=True, progressive=True)
    print("  about.jpg", flush=True)


if __name__ == "__main__":
    main()
