# -*- coding: utf-8 -*-
"""Сборка единой фотосерии каталога.

Источники по приоритету:
  1. build/photos/<id>.jpg — оригиналы с сайта (1100 px), packshot на белом;
  2. assets/products/pies-<id>-v2.webp — студийная серия пирогов (своих
     фотографий этих позиций у предприятия нет);
  3. i.jpg / i1.jpg / i2.jpg — съёмка осетинских пирогов на производстве;
  4. заглушка для позиции, у которой фотографии нет вовсе.

Итог: assets/products/<id>-v7.webp (1024 px) и <id>-v7-640.webp.
"""
import json
import os
import sys

import numpy as np
from PIL import (Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter,
                 ImageFont)

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
SITE = os.path.dirname(os.path.dirname(os.path.dirname(APP)))
SRC_HD = os.path.join(HERE, "photos")
PRODUCTS = os.path.join(APP, "assets", "products")
PREVIEW = os.path.join(HERE, "preview")

SIZE = 1024
SPAN = 0.78
BASE_LINE = 0.84

# прозрачные упаковки и стекло: вырез крошится, показываем кадр целиком
TINT_IDS = {"760", "761", "764", "769", "758", "778"}
# студийные кадры: собственных фотографий этих пирогов нет
STUDIO = {"736", "737", "738", "739", "741", "772", "773", "774"}
# съёмка на производстве: файл, центр и полуоси доски, коррекция цвета
REAL = {
    "801": (os.path.join(SITE, "i.jpg"), (720, 1040), (660, 660), (1.00, 1.00, 1.00), 0.97),
    "802": (os.path.join(SITE, "i1.jpg"), (875, 830), (880, 480), (1.05, 1.05, 0.88), 0.80),
    "803": (os.path.join(SITE, "i2.jpg"), (900, 860), (890, 470), (1.02, 1.02, 0.94), 0.90),
}


# --------------------------------------------------------------- морфология

def _dilate(m, n):
    for _ in range(n):
        g = m.copy()
        for sh, ax in ((1, 0), (-1, 0), (1, 1), (-1, 1)):
            g |= np.roll(m, sh, axis=ax)
        m = g
    return m


def _erode(m, n):
    return ~_dilate(~m, n)


def _spread(seed, allowed, steps=1400):
    cur = seed & allowed
    for _ in range(steps):
        g = cur.copy()
        for sh, ax in ((1, 0), (-1, 0), (1, 1), (-1, 1)):
            g |= np.roll(cur, sh, axis=ax)
        g &= allowed
        if g.sum() == cur.sum():
            break
        cur = g
    return cur


# -------------------------------------------------------------------- сцена

def background():
    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    d = np.clip(np.hypot(xs - SIZE * .5, ys - SIZE * .40) / (SIZE * .80), 0, 1)
    light = np.array([242, 233, 218], np.float32)
    shade = np.array([198, 181, 158], np.float32)
    return Image.fromarray(
        (light + (shade - light) * (d ** 1.35)[..., None]).astype(np.uint8), "RGB")


def finish(im, floor=.55, lift=1.0, shadows=1.0, sat=.96):
    """Общий грейд каталога: тёплый свет, мягкая виньетка, лёгкое зерно."""
    if shadows != 1.0:
        lut = [min(255, int(255 * (v / 255.) ** shadows)) for v in range(256)]
        im = im.point(lut * 3)
    im = ImageEnhance.Brightness(im).enhance(lift)
    im = ImageEnhance.Contrast(im).enhance(1.08)
    im = ImageEnhance.Color(im).enhance(sat)

    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * 1.03)))
    g = g.point(lambda v: min(255, int(v * 1.008)))
    b = b.point(lambda v: int(v * .955))
    im = Image.merge("RGB", (r, g, b))

    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    e = np.hypot((xs - SIZE * .5) / (SIZE * .52), (ys - SIZE * .5) / (SIZE * .52))
    t = np.clip((e - .86) / (1.42 - .86), 0, 1)
    t = t * t * (3 - 2 * t)
    mask = Image.fromarray(((1 - t * (1 - floor)) * 255).astype(np.uint8), "L")
    mask = mask.filter(ImageFilter.GaussianBlur(40))
    edge = ImageEnhance.Brightness(im).enhance(.62)
    edge = ImageEnhance.Color(edge).enhance(.82).filter(ImageFilter.GaussianBlur(3))
    im = Image.composite(im, edge, mask)

    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=50, threshold=3))
    noise = Image.effect_noise(im.size, 7).convert("RGB")
    return Image.blend(im, ImageChops.overlay(im, noise), .10)


def place(product, span=SPAN):
    """Изделие на общей сцене: единый габарит и линия основания."""
    canvas = background()
    pw, ph = product.size
    k = (SIZE * span) / max(pw, ph)
    nw, nh = max(1, int(pw * k)), max(1, int(ph * k))
    product = product.resize((nw, nh), Image.LANCZOS)
    product = product.filter(ImageFilter.UnsharpMask(radius=2, percent=65, threshold=2))
    px, py = (SIZE - nw) // 2, int(SIZE * BASE_LINE) - nh

    shadow = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(shadow).ellipse(
        [px + nw * .10, py + nh - SIZE * .040,
         px + nw * .90, py + nh + SIZE * .040], fill=122)
    shadow = shadow.filter(ImageFilter.GaussianBlur(24))
    canvas = Image.composite(Image.new("RGB", (SIZE, SIZE), (150, 132, 112)), canvas, shadow)
    canvas.paste(product, (px, py), product)
    return canvas


# -------------------------------------------------------------------- вырез

def cutout(path, white_luma=241, white_sat=16, close=7):
    """Фоном считается только белое, связанное с рамкой кадра."""
    im = Image.open(path).convert("RGB")
    if max(im.size) > 1400:
        im.thumbnail((1400, 1400), Image.LANCZOS)
    w, h = im.size
    a = np.array(im).astype(np.float32)
    luma = a.max(axis=-1)
    sat = luma - a.min(axis=-1)

    white = (luma > white_luma) & (sat < white_sat)
    border = np.zeros((h, w), bool)
    border[0, :] = border[-1, :] = True
    border[:, 0] = border[:, -1] = True

    bg = _spread(border & white, white)
    prod = _erode(_dilate(~bg, close), close)
    prod = _dilate(_erode(prod, 2), 2)

    alpha = prod.astype(np.float32)
    zone = _dilate(bg, 6) & prod
    soft = np.clip((252. - luma) / 12., 0, 1)
    keep = np.clip(sat / 26., 0, 1)
    alpha[zone] = np.maximum(soft[zone], keep[zone])

    a_ch = Image.fromarray((alpha * 255).astype(np.uint8), "L")
    im.putalpha(a_ch.filter(ImageFilter.GaussianBlur(1.0)))
    return im.crop(im.getbbox() or (0, 0, w, h))


def tinted(path, span=SPAN):
    """Без выреза: белый фон снимка перекрашивается в тёплый."""
    im = Image.open(path).convert("RGB")
    w, h = im.size
    k = (SIZE * span) / max(w, h)
    im = im.resize((max(1, int(w * k)), max(1, int(h * k))), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=65, threshold=2))

    canvas = Image.new("RGB", (SIZE, SIZE), (255, 255, 255))
    canvas.paste(im, ((SIZE - im.size[0]) // 2, int(SIZE * BASE_LINE) - im.size[1]))

    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    d = np.clip(np.hypot(xs - SIZE * .5, ys - SIZE * .40) / (SIZE * .80), 0, 1)
    light = np.array([246, 238, 224], np.float32) / 255.
    shade = np.array([196, 179, 156], np.float32) / 255.
    tint = light + (shade - light) * (d ** 1.35)[..., None]
    out = np.array(canvas).astype(np.float32) * tint
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")


def refit_studio(path):
    """Студийный кадр: сцену сохраняем, изделие приводим к общему габариту."""
    im = Image.open(path).convert("RGB").resize((SIZE, SIZE), Image.LANCZOS)
    a = np.array(im).astype(np.float32)
    edge = np.concatenate([a[:14].reshape(-1, 3), a[-14:].reshape(-1, 3),
                           a[:, :14].reshape(-1, 3), a[:, -14:].reshape(-1, 3)])
    ref = np.median(edge, axis=0)
    diff = _dilate(_erode(np.linalg.norm(a - ref, axis=-1) > 26, 3), 3)
    ys, xs = np.where(diff)
    if len(xs) == 0:
        return im
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    k = (SIZE * SPAN) / max(x1 - x0, y1 - y0)

    scaled = im.resize((int(SIZE * k), int(SIZE * k)), Image.LANCZOS)
    off_x = int(SIZE * .5 - (x0 + x1) / 2 * k)
    off_y = int(SIZE * BASE_LINE - y1 * k)

    pad = im.filter(ImageFilter.GaussianBlur(90))
    sw, sh = scaled.size
    f = max(24, int(min(sw, sh) * .08))
    mask = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(mask).rectangle([f, f, sw - f, sh - f], fill=255)
    pad.paste(scaled, (off_x, off_y), mask.filter(ImageFilter.GaussianBlur(f * .6)))
    return pad


def real_photo(path, center, axes, tint, sat):
    """Съёмка на производстве: пирог с доской переносится в общую сцену."""
    im = Image.open(path).convert("RGB")
    a = np.array(im).astype(np.float32)
    luma = a.max(axis=-1)
    satmap = luma - a.min(axis=-1)

    ell = Image.new("L", im.size, 0)
    ImageDraw.Draw(ell).ellipse(
        [center[0] - axes[0], center[1] - axes[1],
         center[0] + axes[0], center[1] + axes[1]], fill=255)
    ell = np.array(ell.filter(ImageFilter.GaussianBlur(min(axes) * .04))).astype(np.float32) / 255.
    keep = np.clip((luma - 55) / 50., 0, 1) * np.clip((satmap - 6) / 16., 0, 1)
    keep = np.clip(keep, 0, 1) ** .6
    a_ch = Image.fromarray((ell * keep * 255).astype(np.uint8), "L")
    im.putalpha(a_ch.filter(ImageFilter.GaussianBlur(4)))
    im = im.crop(im.getbbox())

    rgb, alpha = im.convert("RGB"), im.getchannel("A")
    rgb = ImageEnhance.Color(rgb).enhance(sat)
    channels = list(rgb.split())
    for i in range(3):
        channels[i] = channels[i].point(lambda v, m=tint[i]: min(255, int(v * m)))
    im = Image.merge("RGB", tuple(channels))
    im.putalpha(alpha)
    return place(im, span=.90)


def placeholder():
    """Мягкая заглушка для позиции, у которой фотографии нет."""
    canvas = background()
    d = ImageDraw.Draw(canvas)
    cx, cy, r = SIZE * .5, SIZE * .46, SIZE * .17
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(168, 146, 118), width=3)
    for dy in (-.32, 0, .32):
        d.line([cx - r * .55, cy + r * dy, cx + r * .55, cy + r * dy],
               fill=(178, 156, 128), width=2)
    try:
        font = ImageFont.truetype("georgia.ttf", 40)
    except Exception:
        font = ImageFont.load_default()
    text = "фото готовится"
    d.text((cx - d.textlength(text, font=font) / 2, cy + r + 40), text,
           fill=(150, 130, 106), font=font)
    return canvas


def save(im, pid):
    os.makedirs(PREVIEW, exist_ok=True)
    im.save(os.path.join(PRODUCTS, f"{pid}-v7.webp"), "WEBP", quality=86, method=6)
    small = im.resize((640, 640), Image.LANCZOS)
    small.save(os.path.join(PRODUCTS, f"{pid}-v7-640.webp"), "WEBP", quality=84, method=6)
    small.save(os.path.join(PREVIEW, f"{pid}.webp"), "WEBP", quality=84)


def main():
    catalog = json.load(open(os.path.join(HERE, "catalog.json"), encoding="utf-8"))
    only = set(sys.argv[1:])
    ids = [i["id"] for i in catalog["items"]] + list(REAL)

    for pid in ids:
        if only and pid not in only:
            continue
        hd = os.path.join(SRC_HD, f"{pid}.jpg")
        try:
            if pid in REAL:
                out = finish(real_photo(*REAL[pid]), floor=.58, lift=1.10, shadows=.66)
                kind = "съёмка производства"
            elif pid in STUDIO:
                out = finish(refit_studio(os.path.join(PRODUCTS, f"pies-{pid}-v2.webp")))
                kind = "студийная серия"
            elif os.path.exists(hd):
                out = finish(tinted(hd) if pid in TINT_IDS else place(cutout(hd)))
                kind = "HD с сайта" + (", без выреза" if pid in TINT_IDS else "")
            else:
                legacy = [f for f in os.listdir(PRODUCTS) if f.endswith(f"-{pid}.jpg")]
                if legacy:
                    out = finish(place(cutout(os.path.join(PRODUCTS, legacy[0]))))
                    kind = "архивные 350 px"
                else:
                    out = finish(placeholder())
                    kind = "заглушка"
            save(out, pid)
            print(f"  {pid}: {kind}")
        except Exception as exc:
            print(f"  {pid}: ОШИБКА {exc}")


main()
