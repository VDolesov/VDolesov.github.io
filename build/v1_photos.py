import json
import os
import sys

from PIL import Image, ImageEnhance

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pies_v1
from photos_hd import up_rgba
from photos_v9 import cutout, natural

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
OUT = os.path.join(SITE, "v1", "assets", "products")
PREVIEW = os.path.join(HERE, "preview-v1")
VERSION = 10
SIZE = 2048
AI = {"801", "802", "803"}

pies_v1.SIZE = SIZE


def grade(cut):
    rgb = Image.blend(cut.convert("RGB"), natural(cut.convert("RGB")), .75)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.04)
    r, g, b = rgb.split()
    rgb = Image.merge("RGB", (r.point(lambda v: min(255, int(v * 1.02))), g, b.point(lambda v: int(v * .96))))
    rgb.putalpha(cut.getchannel("A"))
    return rgb


def product(pid):
    return cutout(pid)


LAYOUT = json.load(open(os.path.join(HERE, "v1_layout.json"), encoding="utf-8"))
DEFAULTS = {"pastry": (.60, .80), "pies": (.76, .89)}


def placement(name, cut):
    box = LAYOUT.get(name)
    if not box:
        span, base = DEFAULTS.get(name.split("-")[0], (.80, .866))
        return span, base, .5
    x0, x1, y0, y1 = box
    pw, ph = cut.size
    k = min((x1 - x0) / pw, (y1 - y0) / ph)
    return k * max(pw, ph), y1, (x0 + x1) / 2


def save(im, name):
    os.makedirs(PREVIEW, exist_ok=True)
    base = os.path.join(OUT, f"{name}-v{VERSION}")
    im.save(f"{base}-2048.webp", "WEBP", quality=82, method=6)
    im.resize((1024, 1024), Image.LANCZOS).save(f"{base}.webp", "WEBP", quality=86, method=6)
    small = im.resize((640, 640), Image.LANCZOS)
    small.save(f"{base}-640.webp", "WEBP", quality=84, method=6)
    small.save(os.path.join(PREVIEW, f"{name}.webp"), "WEBP", quality=84)


def main(wanted):
    categories = json.load(open(os.path.join(HERE, "v1_categories.json"), encoding="utf-8"))
    for pid in sorted(categories):
        if pid in AI or (wanted and pid not in wanted):
            continue
        name = f"{categories[pid]}-{pid}"
        try:
            cut, _, kind = product(pid)
            span, base, center = placement(name, cut)
            im = pies_v1.finish(pies_v1.place(grade(up_rgba(cut)), span, base, center))
            save(im, name)
            print(f"  {name}: {kind}", flush=True)
        except Exception as exc:
            print(f"  {name}: ERROR {exc}", flush=True)
    pies_v1.PREVIEW = PREVIEW
    pies_v1.sheet()


if __name__ == "__main__":
    main(sys.argv[1:])
