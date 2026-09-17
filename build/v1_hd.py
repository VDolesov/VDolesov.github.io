import json
import os
import re
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(SITE, "skin"))
from hero_choc import enlarge

PRODUCTS = os.path.join(SITE, "v1", "assets", "products")
ASSETS = os.path.join(SITE, "v1", "assets")
SIZE = 2048
HERO_HEIGHT = 1440
SKIP = {"736", "737", "738", "739", "741", "772", "773", "774", "758", "766", "777"}


def hero():
    src = Image.open(os.path.join(ASSETS, "hero-noir.webp")).convert("RGB")
    big = enlarge(src, HERO_HEIGHT)
    big.save(os.path.join(ASSETS, "hero-noir-2560.webp"), "WEBP", quality=80, method=6)
    print(f"  hero-noir-2560.webp {big.size[0]}x{big.size[1]}")


def products():
    catalog = json.load(open(os.path.join(HERE, "catalog.json"), encoding="utf-8"))
    ids = sorted({i["id"] for i in catalog["items"]} | {"801", "802", "803"})
    done = []
    for name in sorted(os.listdir(PRODUCTS)):
        m = re.fullmatch(r"([a-z]+)-(\d+)-v(\d+)\.webp", name)
        if not m or m.group(2) in SKIP or m.group(2) not in ids:
            continue
        src = Image.open(os.path.join(PRODUCTS, name)).convert("RGB")
        if src.size[0] >= SIZE:
            continue
        big = enlarge(src, SIZE)
        big.save(os.path.join(PRODUCTS, name.replace(".webp", f"-{SIZE}.webp")), "WEBP", quality=82, method=6)
        done.append(m.group(2))
        print(f"  {name} -> {SIZE}", flush=True)
    print("ids:", " ".join(f'"{i}"' for i in sorted(done)))


if __name__ == "__main__":
    hero()
    products()
