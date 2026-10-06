import cv2
import numpy as np
from PIL import Image, ImageEnhance


PIES = {
    "801": ("i.jpg", (0, 250, 1440, 1900), (0.97, 1.00, 1.06), 0.90, .72),
    "802": ("i1.jpg", (0, 300, 1920, 1440), (1.00, 1.00, 1.00), 0.94, .86),
    "803": ("i2.jpg", (0, 330, 1920, 1440), (1.00, 1.00, 0.98), 0.94, .86),
}


def clean_mask(cut):
    a = np.array(cut.getchannel("A"))
    a = cv2.morphologyEx(a, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21)))
    a = cv2.morphologyEx(a, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    a = cv2.GaussianBlur(a, (0, 0), 1.6)
    out = cut.copy()
    out.putalpha(Image.fromarray(a, "L"))
    box = out.getbbox()
    return out.crop(box) if box else out


def balance(cut, tint, sat):
    rgb = cut.convert("RGB")
    channels = list(rgb.split())
    for i in range(3):
        channels[i] = channels[i].point(lambda v, m=tint[i]: min(255, int(v * m)))
    rgb = Image.merge("RGB", tuple(channels))
    rgb = ImageEnhance.Color(rgb).enhance(sat)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.04)
    rgb.putalpha(cut.getchannel("A"))
    return rgb
