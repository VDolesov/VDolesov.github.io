import os
import sys

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from photos_v9 import GROUND, POOL, SIZE, finish, save, scene

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(os.path.dirname(HERE))
RAW = os.path.join(HERE, "sources", "ai")

ITEMS = {"801": "801.png", "802": "802.png", "803": "803.png", "752": "752.png"}
ABOUT = "about.png"
ABOUT_CROP = (250, 0, 1344, 768)


def frame(pid):
    im = Image.open(os.path.join(RAW, ITEMS[pid])).convert("RGB")
    side = min(im.size)
    left, top = (im.width - side) // 2, (im.height - side) // 2
    im = im.crop((left, top, left + side, top + side)).resize((SIZE, SIZE), Image.LANCZOS)
    im = ImageEnhance.Contrast(im).enhance(1.04)
    im = ImageEnhance.Color(im).enhance(.96)
    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * 1.03)))
    b = b.point(lambda v: int(v * .94))
    im = Image.merge("RGB", (r, g, b))

    ys, xs = np.mgrid[0:SIZE, 0:SIZE].astype(np.float32)
    u, v = xs / SIZE, ys / SIZE
    lum = np.array(im.convert("L")).astype(np.float32) / 255
    radial = np.clip(np.hypot((u - .5) / .62, (v - .52) / .62), 0, 1)
    edge = np.clip((radial - .55) / .45, 0, 1) ** 1.6
    keep = np.clip(1 - edge, 0, 1) * (0.35 + 0.65 * np.clip(lum * 4, 0, 1))
    mask = Image.fromarray((np.clip(keep, 0, 1) * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(24))

    canvas = scene()
    pool = Image.new("L", (SIZE, SIZE), 0)
    pool.paste(Image.new("L", (int(SIZE * .7), int(SIZE * .22)), 255), (int(SIZE * .15), int(SIZE * .66)))
    pool = pool.filter(ImageFilter.GaussianBlur(SIZE * .07)).point(lambda x: int(x * .5))
    canvas = Image.composite(Image.new("RGB", (SIZE, SIZE), POOL), canvas, pool)
    return Image.composite(im, canvas, mask)


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
    targets = sys.argv[1:] or list(ITEMS) + ["about"]
    for pid in targets:
        if pid == "about":
            path = os.path.join(SITE, "pages_mirror", "assets", "about.jpg")
            about().save(path, quality=84, optimize=True, progressive=True)
            print("  about.jpg", flush=True)
            continue
        save(finish(frame(pid)), pid)
        print(f"  {pid}: done", flush=True)


if __name__ == "__main__":
    main()
