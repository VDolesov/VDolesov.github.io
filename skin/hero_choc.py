import os
import sys

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
OUT = os.path.join(APP, "assets")
AI = os.path.join(APP, "build", "sources", "ai")

BG_W, BG_H = 2400, 1060
GROUND = (16, 10, 8)

SLIDES = [
    ("hero-bg.jpg", os.path.join(OUT, "hero-noir.webp"), (1.04, .84), 1.0),
    ("hero-2.jpg", os.path.join(AI, "801.png"), (1.02, .90), 1.0),
    ("hero-3.jpg", os.path.join(AI, "hero-cake.png"), (1.03, .90), .83),
]


def fit_height(photo, fit):
    h = round(BG_H * fit)
    k = h / photo.height
    body = photo.resize((round(photo.width * k), h), Image.LANCZOS)
    if h >= BG_H:
        return body
    top = (BG_H - h) // 2
    w = body.width

    def band(strip, height):
        return strip.resize((w, height), Image.LANCZOS).filter(ImageFilter.GaussianBlur(10))

    out = Image.new("RGB", (w, BG_H))
    out.paste(band(body.crop((0, 0, w, 6)), top + 40), (0, 0))
    out.paste(band(body.crop((0, h - 6, w, h)), BG_H - top - h + 40), (0, top + h - 40))
    mask = Image.new("L", (w, h), 255)
    ramp = np.array(mask).astype(np.float32)
    ys = np.arange(h, dtype=np.float32)
    edge = np.minimum(np.clip(ys / 36, 0, 1), np.clip((h - 1 - ys) / 36, 0, 1))
    ramp *= edge[:, None]
    mask = Image.fromarray(ramp.astype(np.uint8), "L")
    out.paste(body, (0, top), mask)
    return out


def backdrop(source, grade, fit=1.0):
    photo = fit_height(Image.open(source).convert("RGB"), fit)
    r, g, b = photo.split()
    r = r.point(lambda v: min(255, int(v * grade[0])))
    b = b.point(lambda v: int(v * grade[1]))
    photo = ImageEnhance.Contrast(Image.merge("RGB", (r, g, b))).enhance(1.05)

    x0 = BG_W - photo.width
    strip = photo.crop((0, 0, 60, BG_H)).resize((BG_W, BG_H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(40))
    canvas = strip.copy()
    canvas.paste(photo, (x0, 0))

    ys, xs = np.mgrid[0:BG_H, 0:BG_W].astype(np.float32)
    u, v = xs / BG_W, ys / BG_H
    arr = np.array(canvas).astype(np.float32)
    ground = np.array(GROUND, np.float32) + np.clip((u - .1) / .5, 0, 1)[..., None] * np.array((14, 9, 6), np.float32)
    strip_arr = np.array(strip).astype(np.float32)
    strip_arr = ground * .8 + strip_arr * .2
    seam = np.clip((xs - (x0 - 60)) / 320, 0, 1)[..., None]
    seam = seam * seam * (3 - 2 * seam)
    arr = strip_arr * (1 - seam) + arr * seam
    lum = arr.mean(axis=2)
    dark = np.clip((90 - lum) / 90, 0, 1)[..., None]
    arr += dark * np.array((9, 3, -4), np.float32)
    arr *= np.clip(.55 + .45 * np.clip((u - .05) / .5, 0, 1), 0, 1)[..., None]
    arr *= np.clip(1.02 - .35 * np.clip((v - .7) / .3, 0, 1), 0, 1)[..., None]
    rng = np.random.default_rng(11)
    arr += rng.normal(0, 1.4, (BG_H, BG_W, 1))
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def preview(bg, name):
    w, h = 1425, 631
    frame = bg.resize((w, int(w * BG_H / BG_W)), Image.LANCZOS)
    frame = frame.crop((0, (frame.height - h) // 2, w, (frame.height - h) // 2 + h))
    path = os.path.join(HERE, name.replace(".jpg", "-preview.jpg"))
    frame.save(path, quality=90)
    return path


def main():
    os.makedirs(OUT, exist_ok=True)
    wanted = sys.argv[1:]
    for name, source, grade, fit in SLIDES:
        if wanted and name not in wanted:
            continue
        bg = backdrop(source, grade, fit)
        bg_path = os.path.join(OUT, name)
        bg.save(bg_path, quality=86, optimize=True, progressive=True)
        for path in (bg_path, preview(bg, name)):
            print(f"  {os.path.basename(path)}  {os.path.getsize(path) // 1024} KB")


if __name__ == "__main__":
    main()
