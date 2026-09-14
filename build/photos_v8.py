import json
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter
from rembg import new_session, remove

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from photos import (BASE_LINE, SIZE, SPAN, SRC_HD, SRC_LEGACY, SRC_STUDIO,
                    _dilate, _erode, _spread, placeholder)

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(SITE, "pages_mirror", "assets", "products")
PREVIEW = os.path.join(HERE, "preview-v8")
MODEL_SR = os.path.join(HERE, "models", "FSRCNN_x3.pb")

STUDIO = {"736", "737", "738", "739", "741", "772", "773", "774"}

REAL = {"801": ("i.jpg", (720, 1000), 720, (1.04, 1.00, .90)),
        "802": ("i1.jpg", (930, 940), 760, (1.02, 1.00, .95)),
        "803": ("i2.jpg", (960, 940), 780, (1.02, 1.00, .95))}

SPAN_BY_KIND = {"real": .84, "default": SPAN}

_sessions = {}


def session(model):
    if model not in _sessions:
        _sessions[model] = new_session(model)
    return _sessions[model]


def enclosed_mask(im, white_luma=241, white_sat=16):
    a = np.array(im.convert("RGB")).astype(np.float32)
    luma, sat = a.max(axis=-1), a.max(axis=-1) - a.min(axis=-1)
    white = (luma > white_luma) & (sat < white_sat)
    border = np.zeros(white.shape, bool)
    border[0, :] = border[-1, :] = border[:, 0] = border[:, -1] = True
    background = _spread(border & white, white)
    product = _erode(_dilate(~background, 5), 5)
    return _erode(product, 7)


def neural_cutout(im, restore_inside=True, crop=True):
    im = im.convert("RGB")
    if max(im.size) > 1600:
        im.thumbnail((1600, 1600), Image.LANCZOS)

    alpha = None
    for model in ("isnet-general-use", "u2net"):
        cut = remove(im, session=session(model), alpha_matting=True,
                     alpha_matting_foreground_threshold=240,
                     alpha_matting_background_threshold=12,
                     alpha_matting_erode_size=8)
        a = np.array(cut.getchannel("A"))
        alpha = a if alpha is None else np.maximum(alpha, a)
    cut = im.convert("RGBA")
    cut.putalpha(Image.fromarray(alpha, "L"))
    if restore_inside:
        inside = enclosed_mask(im)
        alpha = np.where(inside & (alpha < 250), np.maximum(alpha, 255), alpha).astype(np.uint8)
        alpha = cv2.GaussianBlur(alpha, (0, 0), .8)

    n, labels, stats, _ = cv2.connectedComponentsWithStats((alpha > 24).astype(np.uint8), 8)
    if n > 2:
        biggest = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        keep = np.isin(labels, [i for i in range(1, n)
                                if stats[i, cv2.CC_STAT_AREA] >= stats[biggest, cv2.CC_STAT_AREA] * .015])
        alpha = np.where(keep, alpha, 0).astype(np.uint8)
        cut.putalpha(Image.fromarray(alpha, "L"))
    if not crop:
        return cut
    box = cut.getbbox()
    return cut.crop(box) if box else cut


def upscale(im, factor=3):
    import shutil
    import tempfile

    ascii_path = os.path.join(tempfile.gettempdir(), "FSRCNN_x3.pb")
    if not os.path.exists(ascii_path):
        shutil.copyfile(MODEL_SR, ascii_path)
    sr = cv2.dnn_superres.DnnSuperResImpl_create()
    sr.readModel(ascii_path)
    sr.setModel("fsrcnn", factor)
    arr = cv2.cvtColor(np.array(im.convert("RGB")), cv2.COLOR_RGB2BGR)
    out = sr.upsample(arr)
    return Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))


def scene():
    ys, xs = np.mgrid[0:SIZE, 0:SIZE].astype(np.float32)
    u, v = xs / SIZE, ys / SIZE

    light = np.array([246, 238, 226], np.float32)
    shade = np.array([203, 186, 164], np.float32)
    d = np.clip(np.hypot((u - .38) / .95, (v - .30) / 1.05), 0, 1)
    img = light + (shade - light) * (d ** 1.5)[..., None]

    table = np.clip((v - .70) / .30, 0, 1) ** 1.2
    img += np.array([-14, -16, -20], np.float32) * table[..., None]

    rng = np.random.default_rng(3)
    fine = rng.normal(0, 1, (SIZE, SIZE)).astype(np.float32)
    coarse = cv2.GaussianBlur(rng.normal(0, 1, (SIZE // 4, SIZE // 4)).astype(np.float32), (0, 0), 2)
    coarse = cv2.resize(coarse, (SIZE, SIZE), interpolation=cv2.INTER_CUBIC)
    img += (fine * 1.6 + coarse * 5.0)[..., None]

    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")


def place(product, span=SPAN, sharpen=55):
    canvas = scene()
    pw, ph = product.size
    k = (SIZE * span) / max(pw, ph)
    nw, nh = max(1, int(pw * k)), max(1, int(ph * k))
    product = product.resize((nw, nh), Image.LANCZOS)
    px, py = (SIZE - nw) // 2, int(SIZE * BASE_LINE) - nh

    alpha = product.getchannel("A")
    silhouette = alpha.point(lambda x: 255 if x > 60 else 0)

    soft = silhouette.resize((nw, max(2, int(nh * .22))), Image.LANCZOS)
    layer = Image.new("L", (SIZE, SIZE), 0)
    layer.paste(soft, (px + int(nw * .04), py + nh - int(nh * .12)))
    layer = layer.filter(ImageFilter.GaussianBlur(SIZE * .045))
    layer = layer.point(lambda x: int(x * .42))
    canvas = Image.composite(Image.new("RGB", (SIZE, SIZE), (128, 108, 88)), canvas, layer)

    tight = silhouette.resize((int(nw * .96), max(2, int(nh * .06))), Image.LANCZOS)
    layer = Image.new("L", (SIZE, SIZE), 0)
    layer.paste(tight, (px + int(nw * .02), py + nh - int(nh * .03)))
    layer = layer.filter(ImageFilter.GaussianBlur(SIZE * .020))
    layer = layer.point(lambda x: int(x * .36))
    canvas = Image.composite(Image.new("RGB", (SIZE, SIZE), (96, 78, 62)), canvas, layer)

    rgb = product.convert("RGB")
    if sharpen:
        rgb = rgb.filter(ImageFilter.UnsharpMask(radius=1.6, percent=sharpen, threshold=2))
    product = rgb.copy()
    product.putalpha(alpha)
    canvas.paste(product, (px, py), product)
    return canvas


def finish(im):
    lut = []
    for v in range(256):
        x = v / 255.
        s = x + .06 * np.sin(np.pi * x) * (1 if x > .5 else -.6)
        lut.append(int(np.clip(s, 0, 1) * 255))
    im = im.point(lut * 3)
    im = ImageEnhance.Color(im).enhance(.97)

    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * 1.025)))
    b = b.point(lambda v: int(v * .965))
    im = Image.merge("RGB", (r, g, b))

    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    e = np.hypot((xs - SIZE * .5) / (SIZE * .55), (ys - SIZE * .48) / (SIZE * .55))
    t = np.clip((e - .90) / .55, 0, 1)
    t = t * t * (3 - 2 * t)
    mask = Image.fromarray(((1 - t * .40) * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(36))
    edge = ImageEnhance.Brightness(im).enhance(.70)
    im = Image.composite(im, edge, mask)

    noise = Image.effect_noise(im.size, 6).convert("RGB")
    return Image.blend(im, ImageChops.overlay(im, noise), .08)


def real_frame(name, center, half, tint):
    im = Image.open(os.path.join(SITE, name)).convert("RGB")
    x0, y0 = max(0, center[0] - half), max(0, center[1] - half)
    x1, y1 = min(im.width, center[0] + half), min(im.height, center[1] + half)
    side = min(x1 - x0, y1 - y0)
    im = im.crop((x0, y0, x0 + side, y0 + side)).resize((SIZE, SIZE), Image.LANCZOS)

    channels = list(im.split())
    for i in range(3):
        channels[i] = channels[i].point(lambda v, m=tint[i]: min(255, int(v * m)))
    im = Image.merge("RGB", tuple(channels))
    im = ImageEnhance.Color(im).enhance(.92)
    im = ImageEnhance.Contrast(im).enhance(1.06)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=30, threshold=3))

    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    e = np.hypot((xs - SIZE * .5) / (SIZE * .58), (ys - SIZE * .5) / (SIZE * .58))
    t = np.clip((e - .80) / .60, 0, 1)
    t = t * t * (3 - 2 * t)
    mask = Image.fromarray(((1 - t * .55) * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(40))
    return Image.composite(im, ImageEnhance.Brightness(im).enhance(.55), mask)


def build(pid):
    if pid in REAL:
        return real_frame(*REAL[pid]), "production shot, full frame"
    if pid in STUDIO:
        src = Image.open(os.path.join(SRC_STUDIO, f"pies-{pid}-v2.webp"))
        return finish(place(neural_cutout(src, restore_inside=False))), "studio series"
    hd = os.path.join(SRC_HD, f"{pid}.jpg")
    if os.path.exists(hd):
        return finish(place(neural_cutout(Image.open(hd)))), "site HD"
    legacy = [f for f in os.listdir(SRC_LEGACY) if f.endswith(f"-{pid}.jpg")]
    if legacy:
        src = upscale(Image.open(os.path.join(SRC_LEGACY, legacy[0])))
        return finish(place(neural_cutout(src))), "archive 350 px, x3 super-resolution"
    return finish(placeholder()), "placeholder"


def save(im, pid):
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREVIEW, exist_ok=True)
    im.save(os.path.join(OUT, f"{pid}-v8.webp"), "WEBP", quality=86, method=6)
    small = im.resize((640, 640), Image.LANCZOS)
    small.save(os.path.join(OUT, f"{pid}-v8-640.webp"), "WEBP", quality=84, method=6)
    small.save(os.path.join(PREVIEW, f"{pid}.webp"), "WEBP", quality=84)


def main():
    catalog = json.load(open(os.path.join(HERE, "catalog.json"), encoding="utf-8"))
    ids = sys.argv[1:] or [i["id"] for i in catalog["items"]] + sorted(REAL)
    for pid in ids:
        try:
            im, kind = build(pid)
            save(im, pid)
            print(f"  {pid}: {kind}")
        except Exception as exc:
            print(f"  {pid}: ERROR {exc}")


if __name__ == "__main__":
    main()
