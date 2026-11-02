import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import photos_hd
import photos_v9 as pv
import pies_ai
import pies_v1
import plates
import v1_photos

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
OUT = os.path.join(APP, "assets", "products")
AI_PIES = os.path.join(HERE, "sources", "ai", "v1-pies")
SERIES = pv.SERIES
SIZE = 2048

PIE_AI = {"801", "802", "803"}
FOOTPRINT = {"752": (.74, .87)}


def product_ids():
    catalog = json.load(open(os.path.join(HERE, "catalog.json"), encoding="utf-8"))
    return sorted({i["id"] for i in catalog["items"]} | set(pies_ai.ITEMS))


def cutout(pid):
    if pid in PIE_AI:
        name = next(f for f in os.listdir(AI_PIES) if f.startswith(pid + "."))
        return pies_v1.cutout(Image.open(os.path.join(AI_PIES, name))), None
    if pid in pies_ai.ITEMS:
        src = Image.open(os.path.join(pies_ai.RAW, pies_ai.ITEMS[pid])).convert("RGB")
        return pies_v1.cutout(photos_hd.upscale(src)), None
    if pid in plates.BOWL or pid in plates.PLATE or pid in plates.PLATTER:
        span = .86 if pid in plates.PLATTER else .78
        return v1_photos.grade(photos_hd.up_rgba(plates.plated(pid))), span
    cut, span, _ = pv.cutout(pid)
    return v1_photos.grade(photos_hd.up_rgba(cut)), span


def placement(pid, cut, span):
    if pid in FOOTPRINT:
        return (*FOOTPRINT[pid], .5)
    name = f"{v1_photos.CATEGORIES[pid]}-{pid}" if pid in v1_photos.CATEGORIES else None
    if name and name in v1_photos.LAYOUT:
        return v1_photos.placement(name, cut)
    if span:
        return span, pies_v1.BASE_LINE, .5
    return .76, .89, .5


def footprint_place(product, span, base, center):
    canvas = pies_v1.background()
    size = pies_v1.SIZE
    k = (size * span) / max(product.size)
    nw, nh = max(1, int(product.width * k)), max(1, int(product.height * k))
    product = product.resize((nw, nh), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2, percent=30, threshold=3))
    px, py = int(size * center - nw / 2), int(size * base) - nh
    alpha = np.array(product.getchannel("A")) > 128
    widths = alpha.sum(axis=1)
    widest = int(np.flatnonzero(widths == widths.max()).max())
    cols = np.flatnonzero(alpha[widest])
    bottom = int(np.flatnonzero(widths).max())
    half_w, half_h = (cols[-1] - cols[0]) / 2, bottom - widest
    cx = px + (cols[0] + cols[-1]) / 2
    shadow = Image.new("L", (size, size), 0)
    ImageDraw.Draw(shadow).ellipse(
        [cx - half_w, py + widest - half_h + size * .012, cx + half_w, py + bottom + size * .022], fill=122)
    shadow = shadow.filter(ImageFilter.GaussianBlur(28))
    canvas = Image.composite(Image.new("RGB", (size, size), (150, 132, 112)), canvas, shadow)
    canvas.paste(product, (px, py), product)
    return canvas


def save(im, pid):
    base = os.path.join(OUT, f"{pid}-{SERIES}")
    im.save(f"{base}-2048.webp", "WEBP", quality=82, method=6)
    im.resize((1024, 1024), Image.LANCZOS).save(f"{base}.webp", "WEBP", quality=86, method=6)
    im.resize((640, 640), Image.LANCZOS).save(f"{base}-640.webp", "WEBP", quality=84, method=6)


def main(wanted):
    pies_v1.SIZE = SIZE
    for pid in product_ids():
        if wanted and pid not in wanted:
            continue
        try:
            cut, span = cutout(pid)
            span, base, center = placement(pid, cut, span)
            place = footprint_place if pid in FOOTPRINT else pies_v1.place
            save(pies_v1.finish(place(cut, span, base, center)), pid)
            print(f"  {pid}: light scene", flush=True)
        except Exception as exc:
            print(f"  {pid}: ERROR {exc}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
