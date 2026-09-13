# -*- coding: utf-8 -*-
"""Главный баннер направления «Чёрный шоколад».

Шаблон складывает баннер из широкой подложки и картинки продукта справа.
Обе собираются здесь в тех же пропорциях, что и раньше (skin/hero.py):

    assets/hero-bg.jpg     2400x1060  подложка — почти чёрное какао,
                                      одно тёплое световое пятно справа
    assets/hero-cake.webp  1308x880   торт «Шварцвальдский» с лужицей
                                      света и тенью, прозрачный WebP

Свет и тень запечены в картинку продукта, а не в подложку: шаблон двигает
продукт при смене ширины экрана, и пятно света должно ехать вместе с ним.
Заодно пересобирается фотография в блоке «О компании» — темнее, в тон.

    python skin/hero_choc.py
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
from photos_v8 import neural_cutout  # noqa: E402  — тот же вырез, что в каталоге

BG_W, BG_H = 2400, 1060
CAKE_W, CAKE_H = 1308, 880
SOURCE = os.path.join(BUILD, "photos", "749.jpg")

GROUND = np.array([16, 10, 8], np.float32)
LIT = np.array([74, 46, 33], np.float32)
POOL = (92, 62, 44)


def backdrop():
    """Тихая подложка: какао, тёплое пятно света там, где стоит продукт."""
    y, x = np.mgrid[0:BG_H, 0:BG_W].astype(np.float32)
    u, v = x / BG_W, y / BG_H
    d = np.clip(np.hypot((u - .70) / .55, (v - .32) / .95), 0, 1)
    img = LIT + (GROUND - LIT) * (d ** 1.3)[..., None]
    # левая половина под текст — темнее
    img *= np.clip(.62 + .38 * np.clip((u - .05) / .45, 0, 1), 0, 1)[..., None]
    rng = np.random.default_rng(11)
    img += rng.normal(0, 1.6, (BG_H, BG_W, 1))
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")


def cake():
    """Вырез продукта с лужицей света и тенью на прозрачном фоне."""
    im = neural_cutout(Image.open(SOURCE))
    rgb = im.convert("RGB")
    rgb = ImageEnhance.Contrast(rgb).enhance(1.08)
    rgb = ImageEnhance.Brightness(rgb).enhance(.96)
    rgb = rgb.filter(ImageFilter.UnsharpMask(radius=1.6, percent=50, threshold=2))
    alpha = im.getchannel("A")
    edge = alpha.filter(ImageFilter.GaussianBlur(3)).point(lambda x: 255 - int((255 - x) * .35))
    rgb = Image.composite(rgb, ImageEnhance.Brightness(rgb).enhance(.6), edge)
    rgb.putalpha(alpha)
    im = rgb

    box_w, box_h = int(CAKE_W * .80), int(CAKE_H * .82)
    im.thumbnail((box_w, box_h), Image.LANCZOS)
    x = (CAKE_W - im.width) // 2
    y = int(CAKE_H * .86) - im.height

    canvas = Image.new("RGBA", (CAKE_W, CAKE_H), (0, 0, 0, 0))
    silhouette = im.getchannel("A").point(lambda v: 255 if v > 60 else 0)

    # лужица света под изделием — светлее подложки, с прозрачностью
    soft = silhouette.resize((int(im.width * 1.4), max(2, int(im.height * .30))), Image.LANCZOS)
    layer = Image.new("L", (CAKE_W, CAKE_H), 0)
    layer.paste(soft, (x - int(im.width * .2), y + im.height - int(im.height * .16)))
    layer = layer.filter(ImageFilter.GaussianBlur(CAKE_W * .05)).point(lambda v: int(v * .70))
    canvas.paste(Image.new("RGBA", (CAKE_W, CAKE_H), POOL + (255,)), (0, 0), layer)

    # контактная тень — чёрная, узкая
    tight = silhouette.resize((int(im.width * .94), max(2, int(im.height * .07))), Image.LANCZOS)
    layer = Image.new("L", (CAKE_W, CAKE_H), 0)
    layer.paste(tight, (x + int(im.width * .03), y + im.height - int(im.height * .035)))
    layer = layer.filter(ImageFilter.GaussianBlur(CAKE_W * .014)).point(lambda v: int(v * .75))
    canvas.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (CAKE_W, CAKE_H), (0, 0, 0)).split(), layer)))

    canvas.alpha_composite(im, (x, max(0, y)))
    return canvas


def about():
    """Фото с производства в блоке «О компании»: темнее и теплее, в тон странице."""
    im = Image.open(os.path.join(SITE, "i1.jpg")).convert("RGB").crop((230, 330, 1920, 1440))
    w, h = 1440, 610
    k = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    left, top = (im.width - w) // 2, int((im.height - h) * .55)
    im = im.crop((left, top, left + w, top + h))
    im = ImageEnhance.Brightness(im).enhance(.72)
    im = ImageEnhance.Contrast(im).enhance(1.08)
    im = ImageEnhance.Color(im).enhance(.9)
    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * 1.04)))
    b = b.point(lambda v: int(v * .9))
    im = Image.merge("RGB", (r, g, b))
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    e = np.clip(np.hypot((xs / w - .55) / .75, (ys / h - .5) / .85), 0, 1) ** 1.4
    mask = Image.fromarray(((1 - e * .7) * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(50))
    return Image.composite(im, ImageEnhance.Brightness(im).enhance(.25), mask)


def preview(bg, ck):
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
    bg.save(bg_path, quality=86, optimize=True, progressive=True)

    ck = cake()
    ck_path = os.path.join(OUT, "hero-cake.webp")
    ck.save(ck_path, "WEBP", quality=88, method=6)

    ab = about()
    ab_path = os.path.join(OUT, "about.jpg")
    ab.save(ab_path, quality=84, optimize=True, progressive=True)

    for path in (bg_path, ck_path, ab_path, preview(bg, ck)):
        print(f"  {os.path.basename(path)}  {os.path.getsize(path) // 1024} КБ")


if __name__ == "__main__":
    main()
