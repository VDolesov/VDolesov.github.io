import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(SITE, "skin"))
from hero_choc import enlarge

ASSETS = os.path.join(SITE, "v1", "assets")
HERO_HEIGHT = 1440


def hero():
    src = Image.open(os.path.join(ASSETS, "hero-noir.webp")).convert("RGB")
    big = enlarge(src, HERO_HEIGHT)
    big.save(os.path.join(ASSETS, "hero-noir-2560.webp"), "WEBP", quality=80, method=6)
    print(f"  hero-noir-2560.webp {big.size[0]}x{big.size[1]}")


if __name__ == "__main__":
    hero()
