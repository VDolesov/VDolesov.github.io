import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageChops, ImageEnhance, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from photos_v8 import OUT, PREVIEW, SIZE, neural_cutout

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(os.path.dirname(HERE))


PIES = {
    "801": ("i.jpg", (0, 250, 1440, 1900), (0.97, 1.00, 1.06), 0.90, .72),
    "802": ("i1.jpg", (0, 300, 1920, 1440), (1.00, 1.00, 1.00), 0.94, .86),
    "803": ("i2.jpg", (0, 330, 1920, 1440), (1.00, 1.00, 0.98), 0.94, .86),
}
BASE = .85


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


def scene():
    ys, xs = np.mgrid[0:SIZE, 0:SIZE].astype(np.float32)
    u, v = xs / SIZE, ys / SIZE

    deep = np.array([24, 15, 13], np.float32)
    warm = np.array([74, 46, 38], np.float32)
    d = np.clip(np.hypot((u - .40) / .90, (v - .28) / .95), 0, 1)
    img = warm + (deep - warm) * (d ** 1.35)[..., None]

    table = np.clip((v - .74) / .26, 0, 1)
    img += np.array([26, 16, 11], np.float32) * (table * (1 - table * .5))[..., None]

    rng = np.random.default_rng(7)
    img += rng.normal(0, 2.0, (SIZE, SIZE, 1))
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")


def place(product, span):
    canvas = scene()
    pw, ph = product.size
    k = (SIZE * span) / max(pw, ph)
    nw, nh = max(1, int(pw * k)), max(1, int(ph * k))
    product = product.resize((nw, nh), Image.LANCZOS)
    px, py = (SIZE - nw) // 2, int(SIZE * BASE) - nh

    alpha = product.getchannel("A")
    silhouette = alpha.point(lambda x: 255 if x > 60 else 0)

    soft = silhouette.resize((nw, max(2, int(nh * .26))), Image.LANCZOS)
    layer = Image.new("L", (SIZE, SIZE), 0)
    layer.paste(soft, (px + int(nw * .03), py + nh - int(nh * .14)))
    layer = layer.filter(ImageFilter.GaussianBlur(SIZE * .05)).point(lambda x: int(x * .75))
    canvas = Image.composite(Image.new("RGB", (SIZE, SIZE), (10, 6, 5)), canvas, layer)

    tight = silhouette.resize((int(nw * .96), max(2, int(nh * .07))), Image.LANCZOS)
    layer = Image.new("L", (SIZE, SIZE), 0)
    layer.paste(tight, (px + int(nw * .02), py + nh - int(nh * .035)))
    layer = layer.filter(ImageFilter.GaussianBlur(SIZE * .018)).point(lambda x: int(x * .6))
    canvas = Image.composite(Image.new("RGB", (SIZE, SIZE), (6, 3, 3)), canvas, layer)

    rgb = product.convert("RGB").filter(ImageFilter.UnsharpMask(radius=1.4, percent=28, threshold=3))
    rgb.putalpha(alpha)
    canvas.paste(rgb, (px, py), rgb)
    return canvas


def finish(im):
    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * 1.03)))
    b = b.point(lambda v: int(v * .96))
    im = Image.merge("RGB", (r, g, b))

    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    e = np.hypot((xs - SIZE * .5) / (SIZE * .58), (ys - SIZE * .46) / (SIZE * .58))
    t = np.clip((e - .82) / .60, 0, 1)
    t = t * t * (3 - 2 * t)
    mask = Image.fromarray(((1 - t * .5) * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(40))
    im = Image.composite(im, ImageEnhance.Brightness(im).enhance(.6), mask)

    noise = Image.effect_noise(im.size, 6).convert("RGB")
    return Image.blend(im, ImageChops.overlay(im, noise), .07)


def main():
    os.makedirs(PREVIEW, exist_ok=True)
    tiles = []
    for pid, (name, box, tint, sat, span) in PIES.items():
        src = Image.open(os.path.join(SITE, name)).convert("RGB").crop(box)
        cut = clean_mask(neural_cutout(src, restore_inside=False))
        im = finish(place(balance(cut, tint, sat), span))
        im.save(os.path.join(OUT, f"{pid}-v8.webp"), "WEBP", quality=86, method=6)
        small = im.resize((640, 640), Image.LANCZOS)
        small.save(os.path.join(OUT, f"{pid}-v8-640.webp"), "WEBP", quality=84, method=6)
        tiles.append(small)
        print(f"  {pid}: {name} done")

    sheet = Image.new("RGB", (640 * 3 + 40, 640 + 20), (30, 24, 22))
    for i, t in enumerate(tiles):
        sheet.paste(t, (10 + i * 650, 10))
    sheet.save(os.path.join(PREVIEW, "osetin-sheet.jpg"), quality=86)


if __name__ == "__main__":
    main()
