# -*- coding: utf-8 -*-
"""Картинки главной страницы: подборка в баннер и кадр для блока «О компании».

    assets/hero-mosaic.webp 1320x900   четыре кадра плиткой: слева высокий —
                                       настоящая съёмка пирога на производстве,
                                       справа два квадрата из каталожной серии
    assets/about.jpg        1440x610   пирог на столе цеха, для блока о компании

Подборка вместо одного выреза: у выреза на тёмном фоне всегда видно, что он
вырезан. Кадры в рамках — нет: это просто фотографии.

    python skin/home.py
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
SITE = os.path.dirname(APP)
PRODUCTS = os.path.join(APP, "assets", "products")
OUT = os.path.join(APP, "assets")

W, H, GAP, RADIUS = 1320, 900, 26, 26


def cover(im, w, h, focus=(0.5, 0.5)):
    """Вписывает кадр в w×h с обрезкой, центр обрезки — в точке focus."""
    im = im.convert("RGB")
    scale = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    x = round((im.width - w) * focus[0])
    y = round((im.height - h) * focus[1])
    return im.crop((x, y, x + w, y + h))


def grade(im, warmth=1.0, dark=1.0, sat=1.0):
    a = np.array(im).astype(np.float32)
    a[..., 0] *= 1.0 + 0.05 * (warmth - 1) * 20
    a[..., 2] *= 1.0 - 0.05 * (warmth - 1) * 20
    a *= dark
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")
    return ImageEnhance.Color(im).enhance(sat)


def rounded(im, radius):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius, fill=255)
    out = im.convert("RGBA")
    out.putalpha(mask)
    return out


def tile_real(path, w, h, box, focus):
    im = Image.open(path)
    im = im.crop(box)
    im = cover(im, w, h, focus)
    return grade(im, warmth=1.02, dark=0.92, sat=0.96)


def tile_product(pid, w, h):
    im = Image.open(os.path.join(PRODUCTS, f"{pid}-v7.webp"))
    return cover(im, w, h, (0.5, 0.52))


def mosaic():
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    col = (W - GAP) // 2
    row = (H - GAP) // 2

    # слева — высокий кадр с производства: пирог на доске, тёмный стол
    left = tile_real(os.path.join(SITE, "i2.jpg"), col, H, (420, 420, 1330, 1440), (0.6, 0.25))
    # справа — два кадра из каталожной серии
    top = tile_product("747", col, row)
    bottom = tile_product("746", col, row)

    # мягкая тень под каждой плиткой, чтобы подборка не висела в воздухе
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    for box in ((0, 0, col, H), (col + GAP, 0, W, row), (col + GAP, row + GAP, W, H)):
        draw.rounded_rectangle((box[0] + 6, box[1] + 18, box[2] - 6, box[3] + 18), RADIUS, fill=(0, 0, 0, 120))
    shadow = shadow.filter(ImageFilter.GaussianBlur(22))
    canvas.alpha_composite(shadow)

    canvas.alpha_composite(rounded(left, RADIUS), (0, 0))
    canvas.alpha_composite(rounded(top, RADIUS), (col + GAP, 0))
    canvas.alpha_composite(rounded(bottom, RADIUS), (col + GAP, row + GAP))

    # тонкая светлая кромка — как рамка у карточек
    edge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(edge)
    for box in ((0, 0, col - 1, H - 1), (col + GAP, 0, W - 1, row - 1), (col + GAP, row + GAP, W - 1, H - 1)):
        d.rounded_rectangle(box, RADIUS, outline=(255, 245, 235, 46), width=2)
    canvas.alpha_composite(edge)
    return canvas


def about():
    im = Image.open(os.path.join(SITE, "i1.jpg"))
    im = im.crop((0, 300, 1920, 1440))
    im = cover(im, 1440, 610, (0.5, 0.55))
    return grade(im, warmth=1.03, dark=0.86, sat=0.94)


def main():
    os.makedirs(OUT, exist_ok=True)
    m = mosaic()
    p1 = os.path.join(OUT, "hero-mosaic.webp")
    m.save(p1, "WEBP", quality=88, method=6)
    a = about()
    p2 = os.path.join(OUT, "about.jpg")
    a.save(p2, quality=86, optimize=True, progressive=True)
    for p in (p1, p2):
        print(f"  {os.path.basename(p)}  {os.path.getsize(p) // 1024} КБ")

    # предпросмотр на подложке баннера
    bg = Image.open(os.path.join(OUT, "hero-bg.jpg")).convert("RGB")
    frame = bg.resize((1425, round(1425 * bg.height / bg.width)), Image.LANCZOS)
    frame = frame.crop((0, (frame.height - 631) // 2, 1425, (frame.height - 631) // 2 + 631))
    shown = m.resize((662, round(662 * H / W)), Image.LANCZOS)
    frame.paste(shown, (713, (631 - shown.height) // 2), shown)
    frame.save(os.path.join(HERE, "hero-preview.jpg"), quality=90)


if __name__ == "__main__":
    main()
