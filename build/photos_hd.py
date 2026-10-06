import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import photos_v8
import photos_v9
import pies_ai
import plates
from photos_v8 import upscale

HERE = os.path.dirname(os.path.abspath(__file__))
SIZE = 2048

for module in (photos_v8, photos_v9, plates, pies_ai):
    module.SIZE = SIZE


def up_rgba(cut):
    rgb = upscale(cut.convert("RGB"))
    alpha = cut.getchannel("A").resize(rgb.size, Image.LANCZOS)
    rgb.putalpha(alpha)
    return rgb
