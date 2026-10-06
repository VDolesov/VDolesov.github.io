import os
import sys

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from photos import SRC_HD, SRC_LEGACY, SRC_STUDIO
from photos_v8 import STUDIO, neural_cutout, upscale

HERE = os.path.dirname(os.path.abspath(__file__))
SERIES = "v9"

SPAN = .78
GROUND = (34, 23, 17)


def natural(rgb):
    soft = rgb.filter(ImageFilter.GaussianBlur(1.1))
    rgb = Image.blend(rgb, soft, .38)
    arr = np.asarray(rgb).astype(np.float32) / 255
    wide = np.asarray(rgb.filter(ImageFilter.GaussianBlur(14))).astype(np.float32) / 255
    arr = arr + (wide - arr) * .12

    mx, mn = arr.max(axis=2), arr.min(axis=2)
    delta = mx - mn
    sat = np.where(mx > 0, delta / np.maximum(mx, 1e-6), 0)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    hue = np.zeros_like(mx)
    m = delta > 1e-6
    rm, gm, bm = (mx == r) & m, (mx == g) & m & ~(mx == r), (mx == b) & m & ~(mx == r) & ~(mx == g)
    hue[rm] = ((g - b)[rm] / delta[rm]) % 6
    hue[gm] = (b - r)[gm] / delta[gm] + 2
    hue[bm] = (r - g)[bm] / delta[bm] + 4
    hue = hue / 6
    warm = np.clip(1 - np.abs(hue - .07) / .09, 0, 1)
    scale = .88 - .16 * warm - .10 * np.clip((sat - .55) / .45, 0, 1)
    grey = mx[..., None]
    arr = grey + (arr - grey) * scale[..., None]

    arr = .025 + arr * .955
    arr = np.where(arr > .74, .74 + (arr - .74) * .84, arr)
    arr[..., 0] *= .985
    arr[..., 2] *= 1.02
    return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8), "RGB")


def cutout(pid):
    if pid in STUDIO:
        src = Image.open(os.path.join(SRC_STUDIO, f"pies-{pid}-v2.webp"))
        return neural_cutout(src, restore_inside=False), SPAN, "studio series"
    hd = os.path.join(SRC_HD, f"{pid}.jpg")
    if os.path.exists(hd):
        return neural_cutout(Image.open(hd)), SPAN, "site HD"
    legacy = [f for f in os.listdir(SRC_LEGACY) if f.endswith(f"-{pid}.jpg")]
    if legacy:
        src = upscale(Image.open(os.path.join(SRC_LEGACY, legacy[0])))
        return neural_cutout(src), SPAN, "archive 350 px, x3 super-resolution"
    raise FileNotFoundError(f"no source for {pid}")
