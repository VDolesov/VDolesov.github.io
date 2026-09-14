import os

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
OUT = os.path.join(APP, "assets")
SOURCE = os.path.join(OUT, "hero-noir.webp")

BG_W, BG_H = 2400, 1060
GROUND = (16, 10, 8)


def backdrop():
    photo = Image.open(SOURCE).convert("RGB")
    k = BG_H / photo.height
    photo = photo.resize((round(photo.width * k), BG_H), Image.LANCZOS)
    r, g, b = photo.split()
    r = r.point(lambda v: min(255, int(v * 1.04)))
    b = b.point(lambda v: int(v * .84))
    photo = ImageEnhance.Contrast(Image.merge("RGB", (r, g, b))).enhance(1.05)

    x0 = BG_W - photo.width
    strip = photo.crop((0, 0, 60, BG_H)).resize((BG_W, BG_H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(40))
    canvas = strip.copy()
    canvas.paste(photo, (x0, 0))

    ys, xs = np.mgrid[0:BG_H, 0:BG_W].astype(np.float32)
    u, v = xs / BG_W, ys / BG_H
    arr = np.array(canvas).astype(np.float32)
    seam = np.clip((xs - (x0 - 220)) / 220, 0, 1)[..., None]
    arr = np.array(strip).astype(np.float32) * (1 - seam) + arr * seam
    arr *= np.clip(.55 + .45 * np.clip((u - .05) / .5, 0, 1), 0, 1)[..., None]
    arr *= np.clip(1.02 - .35 * np.clip((v - .7) / .3, 0, 1), 0, 1)[..., None]
    rng = np.random.default_rng(11)
    arr += rng.normal(0, 1.4, (BG_H, BG_W, 1))
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def preview(bg):
    w, h = 1425, 631
    frame = bg.resize((w, int(w * BG_H / BG_W)), Image.LANCZOS)
    frame = frame.crop((0, (frame.height - h) // 2, w, (frame.height - h) // 2 + h))
    path = os.path.join(HERE, "hero-preview.jpg")
    frame.save(path, quality=90)
    return path


def main():
    os.makedirs(OUT, exist_ok=True)
    bg = backdrop()
    bg_path = os.path.join(OUT, "hero-bg.jpg")
    bg.save(bg_path, quality=86, optimize=True, progressive=True)
    for path in (bg_path, preview(bg)):
        print(f"  {os.path.basename(path)}  {os.path.getsize(path) // 1024} KB")


if __name__ == "__main__":
    main()
