# -*- coding: utf-8 -*-
"""Главный баннер: свой кадр вместо стоковой фотографии.

Шаблон складывает баннер из двух картинок — широкой подложки на весь блок
и вырезанного продукта справа. Здесь собираются обе, в тех же пропорциях,
что и на сайте, поэтому меняются только файлы:

    assets/hero-bg.jpg    2400x1060  подложка
    assets/hero-cake.png  1308x880   торт, снизу уходящий в темноту

Подложка намеренно тихая: почти чёрное вино с одним приглушённым источником
света сверху справа. Яркий софит превращал вырез в наклейку — продукт висел
на розовом пятне. Низ выреза уводится в прозрачность, поэтому торт не стоит
на пустоте, а выходит из темноты.

    python skin/hero.py
"""
import os
import sys

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

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

# почти чёрное вино; светлее — только там, где падает свет
DARK = np.array([18, 10, 13], np.float32)
DEEP = np.array([46, 16, 26], np.float32)
WARM = np.array([150, 104, 84], np.float32)


def backdrop():
    """Тихий тёмный фон: один приглушённый источник света и виньетка."""
    y, x = np.mgrid[0:BG_H, 0:BG_W].astype(np.float32)
    u, v = x / BG_W, y / BG_H

    ramp = np.clip(u * 0.70 + (1 - v) * 0.40, 0, 1)[..., None]
    img = DARK + (DEEP - DARK) * ramp

    # свет сверху справа — мягкий, без выраженного центра
    glow = np.exp(-(((u - 0.72) / 0.46) ** 2 + ((v - 0.20) / 0.62) ** 2))
    img += WARM * (glow ** 1.4)[..., None] * 0.30

    # пол под продуктом: узкая полоса отражённого света
    floor = np.exp(-(((u - 0.66) / 0.26) ** 2 + ((v - 0.86) / 0.10) ** 2))
    img += WARM * (floor ** 2)[..., None] * 0.13

    # низ кадра глушим — из этой темноты выходит вырез
    img *= np.clip(1.0 - 0.45 * np.clip((v - 0.62) / 0.38, 0, 1) ** 1.6, 0, 1)[..., None]

    # левая треть под текст: заметно темнее
    img *= np.clip(0.60 + 0.40 * np.clip((u - 0.04) / 0.42, 0, 1), 0, 1)[..., None]

    # виньетка
    r = np.sqrt(((u - 0.52) / 0.68) ** 2 + ((v - 0.48) / 0.74) ** 2)
    img *= np.clip(1.04 - 0.40 * r ** 2.0, 0, 1)[..., None]

    rng = np.random.default_rng(11)
    img += rng.normal(0, 2.2, (BG_H, BG_W, 1))

    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")


def relight(im):
    """Свет сцены падает сверху справа — гасим левый и нижний край продукта.

    Снимок каталога снят ровным студийным светом со всех сторон. Без этого
    вырез выглядит наклейкой: на тёмном фоне у него нет ни одной тени.
    Заодно придерживаем самые светлые места — бумажная салфетка не должна
    быть ярче торта.
    """
    a = np.array(im).astype(np.float32)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u, v = xx / w, yy / h

    # ключевой свет: ярче в правом верхнем углу, глуше в левом нижнем
    key = 0.74 + 0.34 * np.clip(u * 0.62 + (1 - v) * 0.52, 0, 1)
    a[..., :3] *= key[..., None]

    # придерживаем пересветы
    rgb = a[..., :3]
    top = np.clip((rgb - 196) / 59.0, 0, 1)
    rgb -= top * 30.0
    a[..., :3] = np.clip(rgb, 0, 255)

    return Image.fromarray(a.astype(np.uint8), "RGBA")


def fade_base(im, start=0.86, end=1.00):
    """Низ снимка уводится в прозрачность — подставка не висит в воздухе."""
    a = np.array(im.getchannel("A")).astype(np.float32)
    h = a.shape[0]
    rows = np.arange(h, dtype=np.float32) / h
    ramp = 1.0 - np.clip((rows - start) / (end - start), 0, 1) ** 1.3
    a *= ramp[:, None]
    im.putalpha(Image.fromarray(a.astype(np.uint8), "L"))
    return im


def cake():
    """Вырез продукта: приглушённый по цвету, снизу растворённый в тени."""
    im = cutout(SOURCE)

    # кадр снят на холодном ярком свету — сажаем под тёплый приглушённый
    im = ImageEnhance.Color(im).enhance(0.86)
    im = ImageEnhance.Brightness(im).enhance(0.94)
    a = np.array(im).astype(np.float32)
    a[..., 0] *= 1.04
    a[..., 2] *= 0.94
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")

    im = relight(im)
    im = fade_base(im)

    box_w, box_h = int(CAKE_W * 0.88), int(CAKE_H * 0.94)
    im.thumbnail((box_w, box_h), Image.LANCZOS)

    canvas = Image.new("RGBA", (CAKE_W, CAKE_H), (0, 0, 0, 0))
    x = (CAKE_W - im.width) // 2
    y = int(CAKE_H * 0.93) - im.height

    # тень под продуктом: широкая и мягкая, только чтобы поймать пол
    silhouette = im.getchannel("A").point(lambda v: 255 if v > 40 else 0)
    squashed = silhouette.resize((im.width, max(1, int(im.height * 0.10))), Image.LANCZOS)
    plate = Image.new("L", (CAKE_W, CAKE_H), 0)
    plate.paste(squashed, (x, int(CAKE_H * 0.80)))
    plate = plate.filter(ImageFilter.GaussianBlur(CAKE_W * 0.030))
    canvas.paste(Image.new("RGBA", (CAKE_W, CAKE_H), (10, 4, 7, 130)), (0, 0), plate)

    canvas.alpha_composite(im, (x, max(0, y)))
    return canvas


def preview(bg, ck):
    """Склейка в пропорциях блока — чтобы оценить результат до публикации."""
    w, h = 1425, 631
    frame = bg.resize((w, int(w * BG_H / BG_W)), Image.LANCZOS)
    frame = frame.crop((0, (frame.height - h) // 2, w, (frame.height - h) // 2 + h))
    shown_w = 662
    scaled = ck.resize((shown_w, int(shown_w * CAKE_H / CAKE_W)), Image.LANCZOS)
    frame.paste(scaled, (713, (h - scaled.height) // 2), scaled)
    path = os.path.join(HERE, "hero-preview.jpg")
    frame.save(path, quality=90)
    return path


def main():
    os.makedirs(OUT, exist_ok=True)

    bg = backdrop()
    bg_path = os.path.join(OUT, "hero-bg.jpg")
    bg.save(bg_path, quality=88, optimize=True, progressive=True)

    ck = cake()
    ck_path = os.path.join(OUT, "hero-cake.png")
    ck.save(ck_path, optimize=True)

    for path in (bg_path, ck_path, preview(bg, ck)):
        print(f"  {os.path.basename(path)}  {os.path.getsize(path) // 1024} КБ")


if __name__ == "__main__":
    main()
