import os
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter
from rembg import new_session, remove

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from photos_v9 import natural

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
SRC = os.path.join(HERE, "sources", "ai", "v1-pies")
OUT = os.path.join(SITE, "v1", "assets", "products")
PREVIEW = os.path.join(HERE, "preview-v1-pies")
VERSION = 9

SIZE = 1024
SPAN = 0.78
BASE_LINE = 0.84

_sessions = {}


def session(model):
    if model not in _sessions:
        _sessions[model] = new_session(model)
    return _sessions[model]


def cutout(im):
    im = im.convert("RGB")
    alpha = None
    for model in ("isnet-general-use", "u2net"):
        cut = remove(im, session=session(model), alpha_matting=True,
                     alpha_matting_foreground_threshold=240,
                     alpha_matting_background_threshold=12,
                     alpha_matting_erode_size=8)
        a = np.array(cut.getchannel("A"))
        alpha = a if alpha is None else np.maximum(alpha, a)
    graded = Image.blend(im, natural(im), .3)
    graded = ImageEnhance.Contrast(graded).enhance(1.06)
    graded = ImageEnhance.Color(graded).enhance(1.08)
    r, g, b = graded.split()
    graded = Image.merge("RGB", (r.point(lambda v: min(255, int(v * 1.02))), g, b.point(lambda v: int(v * .93))))
    cut = graded.convert("RGBA")
    cut.putalpha(Image.fromarray(alpha, "L"))
    box = cut.getbbox()
    return cut.crop(box) if box else cut


def background():
    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    d = np.clip(np.hypot(xs - SIZE * .5, ys - SIZE * .40) / (SIZE * .80), 0, 1)
    light = np.array([242, 233, 218], np.float32)
    shade = np.array([198, 181, 158], np.float32)
    return Image.fromarray((light + (shade - light) * (d ** 1.35)[..., None]).astype(np.uint8), "RGB")


def place(product, span=SPAN, base=BASE_LINE, center=.5):
    canvas = background()
    pw, ph = product.size
    k = (SIZE * span) / max(pw, ph)
    nw, nh = max(1, int(pw * k)), max(1, int(ph * k))
    product = product.resize((nw, nh), Image.LANCZOS)
    product = product.filter(ImageFilter.UnsharpMask(radius=2, percent=30, threshold=3))
    px, py = int(SIZE * center - nw / 2), int(SIZE * base) - nh

    shadow = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(shadow).ellipse(
        [px + nw * .10, py + nh - SIZE * .040, px + nw * .90, py + nh + SIZE * .040], fill=122)
    shadow = shadow.filter(ImageFilter.GaussianBlur(24))
    canvas = Image.composite(Image.new("RGB", (SIZE, SIZE), (150, 132, 112)), canvas, shadow)
    canvas.paste(product, (px, py), product)
    return canvas


def finish(im, floor=.55):
    im = ImageEnhance.Contrast(im).enhance(1.08)
    im = ImageEnhance.Color(im).enhance(.96)
    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * 1.03)))
    g = g.point(lambda v: min(255, int(v * 1.008)))
    b = b.point(lambda v: int(v * .955))
    im = Image.merge("RGB", (r, g, b))

    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    e = np.hypot((xs - SIZE * .5) / (SIZE * .52), (ys - SIZE * .5) / (SIZE * .52))
    t = np.clip((e - .86) / (1.42 - .86), 0, 1)
    t = t * t * (3 - 2 * t)
    mask = Image.fromarray(((1 - t * (1 - floor)) * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(40))
    edge = ImageEnhance.Brightness(im).enhance(.62)
    edge = ImageEnhance.Color(edge).enhance(.82).filter(ImageFilter.GaussianBlur(3))
    im = Image.composite(im, edge, mask)

    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=40, threshold=3))
    noise = Image.effect_noise(im.size, 7).convert("RGB")
    return Image.blend(im, ImageChops.overlay(im, noise), .10)


def save(im, pid):
    os.makedirs(PREVIEW, exist_ok=True)
    im.save(os.path.join(OUT, f"pies-{pid}-v{VERSION}.webp"), "WEBP", quality=86, method=6)
    small = im.resize((640, 640), Image.LANCZOS)
    small.save(os.path.join(OUT, f"pies-{pid}-v{VERSION}-640.webp"), "WEBP", quality=84, method=6)
    small.save(os.path.join(PREVIEW, f"{pid}.webp"), "WEBP", quality=84)


def sheet():
    files = sorted(f for f in os.listdir(PREVIEW) if f.endswith(".webp") and f != "sheet.jpg")
    cols = 5
    tile = 300
    rows = (len(files) + cols - 1) // cols
    out = Image.new("RGB", (cols * tile, rows * tile), (255, 255, 255))
    for i, name in enumerate(files):
        im = Image.open(os.path.join(PREVIEW, name)).convert("RGB").resize((tile, tile), Image.LANCZOS)
        out.paste(im, ((i % cols) * tile, (i // cols) * tile))
    out.save(os.path.join(PREVIEW, "sheet.jpg"), quality=82)


def main(wanted):
    for name in sorted(os.listdir(SRC)):
        pid, ext = os.path.splitext(name)
        if ext.lower() not in (".png", ".jpg", ".webp") or (wanted and pid not in wanted):
            continue
        product = cutout(Image.open(os.path.join(SRC, name)))
        save(finish(place(product)), pid)
        print(f"  {pid}: {product.size[0]}x{product.size[1]} cutout")
    sheet()


if __name__ == "__main__":
    main(sys.argv[1:])
