import json
import os
import sys
import tempfile

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import photos_v8
import photos_v9
import pies_ai
import plates
from photos_v8 import OUT, SRC_HD, neural_cutout, upscale
from photos_v9 import SERIES, SPAN, finish, place

HERE = os.path.dirname(os.path.abspath(__file__))
SIZE = 2048
SUFFIX = f"{SERIES}-{SIZE}"
SKIP = photos_v8.STUDIO | {"758", "766", "777"}

for module in (photos_v8, photos_v9, plates, pies_ai):
    module.SIZE = SIZE


def up_rgba(cut):
    rgb = upscale(cut.convert("RGB"))
    alpha = cut.getchannel("A").resize(rgb.size, Image.LANCZOS)
    rgb.putalpha(alpha)
    return rgb


def ai_sources():
    folder = tempfile.mkdtemp(prefix="hero-ai-")
    for name in set(pies_ai.ITEMS.values()):
        upscale(Image.open(os.path.join(pies_ai.RAW, name)).convert("RGB")).save(os.path.join(folder, name))
    return folder


def render(pid):
    if pid in pies_ai.ITEMS:
        return pies_ai.frame(pid), "ai render x3"
    if pid in plates.BOWL or pid in plates.PLATE or pid in plates.PLATTER:
        span = .88 if pid in plates.PLATTER else .80
        return place(up_rgba(plates.plated(pid)), span, sharpen=20), "plated x3"
    hd = os.path.join(SRC_HD, f"{pid}.jpg")
    if not os.path.exists(hd):
        raise FileNotFoundError(f"no HD source for {pid}")
    return place(up_rgba(neural_cutout(Image.open(hd))), SPAN, sharpen=24), "site HD x3"


def main():
    catalog = json.load(open(os.path.join(HERE, "catalog.json"), encoding="utf-8"))
    ids = sys.argv[1:] or sorted(({i["id"] for i in catalog["items"]} | set(pies_ai.ITEMS)) - SKIP)
    pies_ai.RAW = ai_sources()
    for pid in ids:
        try:
            im, kind = render(pid)
            finish(im).save(os.path.join(OUT, f"{pid}-{SUFFIX}.webp"), "WEBP", quality=84, method=6)
            print(f"  {pid}: {kind}", flush=True)
        except Exception as exc:
            print(f"  {pid}: ERROR {exc}", flush=True)


if __name__ == "__main__":
    main()
