import os
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from photos import SIZE, SRC_HD, SRC_LEGACY, SRC_STUDIO, _dilate, _erode, _spread

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
OUT = os.path.join(APP, "assets", "products")
MODEL_SR = os.path.join(HERE, "models", "FSRCNN_x3.pb")

STUDIO = {"736", "737", "738", "739", "741", "772", "773", "774"}


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
