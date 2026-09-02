# -*- coding: utf-8 -*-
"""Главный баннер: свой кадр вместо стоковой фотографии.

Шаблон складывает баннер из двух картинок — широкой подложки на весь блок
и вырезанного продукта справа. Здесь собираются обе, в тех же пропорциях,
что и на сайте, поэтому меняются только файлы:

    assets/hero-bg.jpg    2400x1060  подложка
    assets/hero-cake.png  1308x880   торт с мягкой тенью

    python skin/hero.py
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
SITE = os.path.dirname(APP)
BUILD = os.path.join(SITE, "frontend_mir_slad-main", "apps", "noir-classic", "build")
OUT = os.path.join(APP, "assets")

sys.path.insert(0, BUILD)
from photos import cutout  # noqa: E402  — переиспользуем вырез каталога

BG_W, BG_H = 2400, 1060
CAKE_W, CAKE_H = 1308, 880
SOURCE = os.path.join(BUILD, "photos", "749.jpg")

# бордо подложки: слева темнее — там лежит текст, справа теплее — там свет
DARK = np.array([28, 12, 18], np.float32)
DEEP = np.array([78, 20, 40], np.float32)
WARM = np.array([206, 142, 98], np.float32)


def backdrop():
    """Тёплый софит на бордовом фоне: градиент, свет, зерно, виньетка."""
    y, x = np.mgrid[0:BG_H, 0:BG_W].astype(np.float32)
    u, v = x / BG_W, y / BG_H

    # диагональный градиент от почти чёрного слева-снизу к бордовому справа-сверху
    ramp = np.clip(u * 0.85 + (1 - v) * 0.45, 0, 1)[..., None]
    img = DARK + (DEEP - DARK) * ramp

    # софит за тортом
    glow = np.exp(-(((u - 0.66) / 0.34) ** 2 + ((v - 0.46) / 0.52) ** 2))
    img += WARM * (glow ** 1.6)[..., None] * 0.56

    # второй, слабый и холодный — чтобы левый край не был плоским
    side = np.exp(-(((u - 0.06) / 0.30) ** 2 + ((v - 0.30) / 0.70) ** 2))
    img += np.array([70, 22, 40], np.float32) * (side ** 2)[..., None] * 0.35

    # отражение света на «столе» под тортом
    table = np.exp(-(((u - 0.64) / 0.30) ** 2 + ((v - 0.92) / 0.13) ** 2))
    img += WARM * (table ** 2)[..., None] * 0.15

    # виньетка по краям кадра
    r = np.sqrt(((u - 0.5) / 0.62) ** 2 + ((v - 0.5) / 0.72) ** 2)
    img *= np.clip(1.06 - 0.36 * r ** 2.1, 0, 1)[..., None]

    # зерно, чтобы градиент не полосил на больших экранах
    rng = np.random.default_rng(11)
    img += rng.normal(0, 2.6, (BG_H, BG_W, 1))

    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")


def shadow(alpha, w, h):
    """Мягкая контактная тень: силуэт, сплющенный по вертикали."""
    sq = alpha.resize((w, max(1, int(h * 0.16))), Image.LANCZOS)
    plate = Image.new("L", (w, h), 0)
    plate.paste(sq, (0, int(h * 0.80)))
    return plate.filter(ImageFilter.GaussianBlur(w * 0.035))


def cake():
    """Вырез продукта на прозрачном холсте, с тенью и тёплой подсветкой."""
    im = cutout(SOURCE)

    # вписываем в холст с полями, чтобы тень не упиралась в край
    box_w, box_h = int(CAKE_W * 0.86), int(CAKE_H * 0.84)
    im.thumbnail((box_w, box_h), Image.LANCZOS)

    canvas = Image.new("RGBA", (CAKE_W, CAKE_H), (0, 0, 0, 0))
    x = (CAKE_W - im.width) // 2
    y = int(CAKE_H * 0.80) - im.height

    mask = shadow(im.getchannel("A"), CAKE_W, CAKE_H)
    canvas.paste(Image.new("RGBA", (CAKE_W, CAKE_H), (14, 5, 9, 150)), (0, 0), mask)

    # снимок снят на холодном свету — согреваем под софит подложки
    a = np.array(im).astype(np.float32)
    a[..., 0] *= 1.05
    a[..., 1] *= 1.005
    a[..., 2] *= 0.95
    warm = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")

    canvas.alpha_composite(warm, (x, max(0, y)))
    return canvas


def main():
    os.makedirs(OUT, exist_ok=True)

    bg = backdrop()
    bg_path = os.path.join(OUT, "hero-bg.jpg")
    bg.save(bg_path, quality=88, optimize=True, progressive=True)

    ck = cake()
    ck_path = os.path.join(OUT, "hero-cake.png")
    ck.save(ck_path, optimize=True)

    for path in (bg_path, ck_path):
        print(f"  {os.path.basename(path)}  {os.path.getsize(path) // 1024} КБ")


if __name__ == "__main__":
    main()
