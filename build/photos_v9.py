import json
import os
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from photos_v8 import (OUT, SIZE, SRC_HD, SRC_LEGACY, SRC_STUDIO, STUDIO,
                       neural_cutout, upscale)
from osetin import PIES, balance, clean_mask

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(os.path.dirname(HERE))
PREVIEW = os.path.join(HERE, "preview-v9")
SERIES = "v9"

SPAN = .78
BASE_LINE = .84
GROUND = (16, 10, 8)
LIT = (74, 46, 33)
POOL = (92, 62, 44)


def scene():
    ys, xs = np.mgrid[0:SIZE, 0:SIZE].astype(np.float32)
    u, v = xs / SIZE, ys / SIZE
    g, l = np.array(GROUND, np.float32), np.array(LIT, np.float32)
    d = np.clip(np.hypot((u - .50) / .75, (v - .30) / .85), 0, 1)
    img = l + (g - l) * (d ** 1.35)[..., None]
    table = np.clip((v - .72) / .28, 0, 1) ** 1.3
    img -= 6 * table[..., None]
    rng = np.random.default_rng(7)
    img += rng.normal(0, 1.4, (SIZE, SIZE, 1)).astype(np.float32)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")


def place(product, span=SPAN, sharpen=50):
    canvas = scene()
    pw, ph = product.size
    k = (SIZE * span) / max(pw, ph)
    nw, nh = max(1, int(pw * k)), max(1, int(ph * k))
    product = product.resize((nw, nh), Image.LANCZOS)
    px, py = (SIZE - nw) // 2, int(SIZE * BASE_LINE) - nh
    alpha = product.getchannel("A")
    silhouette = alpha.point(lambda x: 255 if x > 60 else 0)

    layer = Image.new("L", (SIZE, SIZE), 0)
    soft = silhouette.resize((int(nw * 1.35), max(2, int(nh * .30))), Image.LANCZOS)
    layer.paste(soft, (px - int(nw * .175), py + nh - int(nh * .16)))
    layer = layer.filter(ImageFilter.GaussianBlur(SIZE * .06)).point(lambda x: int(x * .55))
    canvas = Image.composite(Image.new("RGB", (SIZE, SIZE), POOL), canvas, layer)

    tight = silhouette.resize((int(nw * .94), max(2, int(nh * .07))), Image.LANCZOS)
    layer = Image.new("L", (SIZE, SIZE), 0)
    layer.paste(tight, (px + int(nw * .03), py + nh - int(nh * .035)))
    layer = layer.filter(ImageFilter.GaussianBlur(SIZE * .018)).point(lambda x: int(x * .70))
    canvas = Image.composite(Image.new("RGB", (SIZE, SIZE), (0, 0, 0)), canvas, layer)

    rgb = natural(product.convert("RGB"))
    if sharpen:
        rgb = rgb.filter(ImageFilter.UnsharpMask(radius=1.2, percent=sharpen, threshold=3))

    edge = alpha.filter(ImageFilter.GaussianBlur(3)).point(lambda x: 255 - int((255 - x) * .35))
    rgb = Image.composite(rgb, ImageEnhance.Brightness(rgb).enhance(.6), edge)
    rgb.putalpha(alpha)
    canvas.paste(rgb, (px, py), rgb)
    return canvas


def natural(rgb):
    soft = rgb.filter(ImageFilter.GaussianBlur(1.1))
    rgb = Image.blend(rgb, soft, .38)
    arr = np.asarray(rgb).astype(np.float32) / 255
    wide = np.asarray(rgb.filter(ImageFilter.GaussianBlur(14))).astype(np.float32) / 255
    arr = arr + (wide - arr) * .12

    mx, mn = arr.max(axis=2), arr.min(axis=2)
    delta = mx - mn
    sat = np.where(mx > 0, delta / np.maximum(mx, 1e-6), 0)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    hue = np.zeros_like(mx)
    m = delta > 1e-6
    rm, gm, bm = (mx == r) & m, (mx == g) & m & ~(mx == r), (mx == b) & m & ~(mx == r) & ~(mx == g)
    hue[rm] = ((g - b)[rm] / delta[rm]) % 6
    hue[gm] = (b - r)[gm] / delta[gm] + 2
    hue[bm] = (r - g)[bm] / delta[bm] + 4
    hue = hue / 6
    warm = np.clip(1 - np.abs(hue - .07) / .09, 0, 1)
    scale = .88 - .16 * warm - .10 * np.clip((sat - .55) / .45, 0, 1)
    grey = mx[..., None]
    arr = grey + (arr - grey) * scale[..., None]

    arr = .025 + arr * .955
    arr = np.where(arr > .74, .74 + (arr - .74) * .84, arr)
    arr[..., 0] *= .985
    arr[..., 2] *= 1.02
    return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8), "RGB")


def finish(im):
    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    e = np.hypot((xs - SIZE * .5) / (SIZE * .6), (ys - SIZE * .5) / (SIZE * .6))
    t = np.clip((e - .85) / .6, 0, 1)
    t = t * t * (3 - 2 * t)
    mask = Image.fromarray(((1 - t * .5) * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(36))
    im = Image.composite(im, ImageEnhance.Brightness(im).enhance(.6), mask)
    noise = Image.effect_noise(im.size, 6).convert("RGB")
    return Image.blend(im, ImageChops.overlay(im, noise), .06)


def placeholder():
    canvas = scene()
    d = ImageDraw.Draw(canvas)
    cx, cy, r = SIZE * .5, SIZE * .46, SIZE * .17
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(140, 108, 62), width=3)
    for dy in (-.32, 0, .32):
        d.line([cx - r * .55, cy + r * dy, cx + r * .55, cy + r * dy], fill=(120, 92, 54), width=2)
    try:
        font = ImageFont.truetype("georgia.ttf", 40)
    except Exception:
        font = ImageFont.load_default()
    text = "фото готовится"
    d.text((cx - d.textlength(text, font=font) / 2, cy + r + 40), text, fill=(140, 108, 62), font=font)
    return canvas


def cutout(pid):
    if pid in PIES:
        name, box, tint, sat, span = PIES[pid]
        src = Image.open(os.path.join(SITE, name)).convert("RGB").crop(box)
        return balance(clean_mask(neural_cutout(src, restore_inside=False)), tint, sat), span, "production shot"
    if pid in STUDIO:
        src = Image.open(os.path.join(SRC_STUDIO, f"pies-{pid}-v2.webp"))
        return neural_cutout(src, restore_inside=False), SPAN, "studio series"
    hd = os.path.join(SRC_HD, f"{pid}.jpg")
    if os.path.exists(hd):
        return neural_cutout(Image.open(hd)), SPAN, "site HD"
    legacy = [f for f in os.listdir(SRC_LEGACY) if f.endswith(f"-{pid}.jpg")]
    if legacy:
        src = upscale(Image.open(os.path.join(SRC_LEGACY, legacy[0])))
        return neural_cutout(src), SPAN, "archive 350 px, x3 super-resolution"
    raise FileNotFoundError(f"no source for {pid}")


def save(im, pid):
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREVIEW, exist_ok=True)
    im.save(os.path.join(OUT, f"{pid}-{SERIES}.webp"), "WEBP", quality=86, method=6)
    small = im.resize((640, 640), Image.LANCZOS)
    small.save(os.path.join(OUT, f"{pid}-{SERIES}-640.webp"), "WEBP", quality=84, method=6)
    small.save(os.path.join(PREVIEW, f"{pid}.webp"), "WEBP", quality=84)


def sheet():
    tiles = sorted(f for f in os.listdir(PREVIEW) if f.endswith(".webp"))
    cols = 6
    rows = (len(tiles) + cols - 1) // cols
    board = Image.new("RGB", (cols * 330 + 10, rows * 330 + 10), (40, 34, 32))
    for i, name in enumerate(tiles):
        im = Image.open(os.path.join(PREVIEW, name)).resize((320, 320), Image.LANCZOS)
        board.paste(im, (10 + (i % cols) * 330, 10 + (i // cols) * 330))
    board.save(os.path.join(PREVIEW, "sheet.jpg"), quality=84)


def main():
    from pies_ai import ITEMS as AI, frame
    from plates import BOWL, PLATE, PLATTER, plated
    catalog = json.load(open(os.path.join(HERE, "catalog.json"), encoding="utf-8"))
    ids = sys.argv[1:] or sorted({i["id"] for i in catalog["items"]} | set(AI))
    for pid in ids:
        try:
            if pid in AI:
                im, kind = frame(pid), "ai render"
            elif pid in BOWL or pid in PLATE or pid in PLATTER:
                im, kind = place(plated(pid), .88 if pid in PLATTER else .80, sharpen=25), "plated"
            else:
                try:
                    cut, span, kind = cutout(pid)
                    im = place(cut, span, sharpen=30)
                except FileNotFoundError:
                    im, kind = placeholder(), "placeholder"
            save(finish(im), pid)
            print(f"  {pid}: {kind}", flush=True)
        except Exception as exc:
            print(f"  {pid}: ERROR {exc}", flush=True)
    sheet()


if __name__ == "__main__":
    main()
