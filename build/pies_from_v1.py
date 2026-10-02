import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import photos_hd
import photos_v9 as pv
import pies_v1
import v1_photos

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
OUT = os.path.join(SITE, "assets", "products")
AI_SRC = os.path.join(HERE, "sources", "ai", "v1-pies")
STUDIO = ["736", "737", "738", "739", "741", "772", "773", "774", "775", "776"]
AI = ["801", "802", "803"]


def cut_for(pid):
    if pid in AI:
        name = next(f for f in os.listdir(AI_SRC) if f.startswith(pid + "."))
        return pies_v1.cutout(Image.open(os.path.join(AI_SRC, name)))
    cut, _, _ = pv.cutout(pid)
    return v1_photos.grade(photos_hd.up_rgba(cut))


def save(im, pid):
    base = os.path.join(OUT, f"{pid}-{pv.SERIES}")
    im.save(f"{base}-2048.webp", "WEBP", quality=82, method=6)
    im.resize((1024, 1024), Image.LANCZOS).save(f"{base}.webp", "WEBP", quality=86, method=6)
    im.resize((640, 640), Image.LANCZOS).save(f"{base}-640.webp", "WEBP", quality=84, method=6)


def main(wanted):
    pv.natural = lambda rgb: rgb
    for pid in STUDIO + AI:
        if wanted and pid not in wanted:
            continue
        save(pv.finish(pv.place(cut_for(pid), pv.SPAN, sharpen=20)), pid)
        print(f"  {pid}: v1 photo on the dark scene", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
