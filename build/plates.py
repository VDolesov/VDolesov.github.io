import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from photos_v8 import SRC_HD, SRC_LEGACY, neural_cutout, upscale
from photos_v9 import finish, place, save, sheet

POLY = {
    "765": [(215, 560), (225, 470), (290, 390), (370, 330), (480, 300), (600, 295), (720, 310), (830, 350), (890, 430), (915, 540), (900, 700), (220, 700)],
    "760": [(370, 560), (405, 450), (470, 375), (580, 325), (720, 305), (830, 335), (915, 425), (950, 540), (930, 720), (360, 720)],
    "768": [(215, 560), (245, 440), (340, 370), (450, 320), (560, 285), (640, 255), (760, 258), (855, 335), (915, 450), (905, 620), (870, 780), (230, 780)],
    "769": [(215, 560), (245, 440), (335, 360), (455, 300), (600, 285), (740, 300), (860, 360), (905, 480), (895, 640), (860, 790), (240, 790)],
    "761": [(215, 600), (245, 480), (340, 405), (450, 360), (560, 330), (700, 340), (800, 400), (850, 480), (870, 610), (860, 780), (215, 780)],
    "781": [(190, 600), (225, 470), (330, 405), (450, 355), (580, 335), (720, 340), (845, 385), (935, 465), (975, 590), (935, 760), (190, 760)],
    "782": [(190, 600), (225, 470), (330, 405), (450, 355), (580, 335), (720, 340), (845, 385), (935, 465), (975, 590), (935, 760), (190, 760)],
    "766": [(140, 560), (185, 390), (335, 300), (520, 252), (700, 270), (870, 350), (945, 455), (960, 600), (890, 850), (140, 850)],
}
BOWL = set(POLY)
PLATE = {"770", "771", "783"}
PLATTER = {"764"}

RIM = np.array([128, 110, 96], np.float32)
BODY = np.array([78, 64, 56], np.float32)
INSIDE = np.array([50, 41, 36], np.float32)


def source(pid):
    hd = os.path.join(SRC_HD, f"{pid}.jpg")
    if os.path.exists(hd):
        return Image.open(hd).convert("RGB")
    legacy = [f for f in os.listdir(SRC_LEGACY) if f.endswith(f"-{pid}.jpg")]
    return upscale(Image.open(os.path.join(SRC_LEGACY, legacy[0])).convert("RGB"))


def cutout(pid):
    src = source(pid)
    if pid in POLY:
        cut = neural_cutout(src, crop=False)
        mask = Image.new("L", src.size, 0)
        ImageDraw.Draw(mask).polygon(POLY[pid], fill=255)
        mask = mask.filter(ImageFilter.MinFilter(41)).filter(ImageFilter.GaussianBlur(3))
        a = np.array(cut.getchannel("A")).astype(np.float32) * (np.array(mask).astype(np.float32) / 255)
        cut.putalpha(Image.fromarray(a.astype(np.uint8), "L"))
    else:
        cut = neural_cutout(src)
    box = cut.getbbox()
    return cut.crop(box) if box else cut


def shade(shape, cx, cy, rx, ry):
    H, W = shape
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    ex, ey = (xs - cx) / rx, (ys - cy) / ry
    return ex, ey, np.hypot(ex, ey)


def ellipse_mask(W, H, cx, cy, rx, ry, feather=1.5):
    _, _, r = shade((H, W), cx, cy, rx, ry)
    edge = np.clip((1 - r) * min(rx, ry) / feather, 0, 1)
    return edge


def dish(w, depth, rim_ratio=.34, bowl=True):
    pad = int(w * .10)
    rh = int(w * rim_ratio)
    W = w + pad * 2
    H = rh + depth + pad * 2
    cx, cy = W / 2, pad + rh / 2
    rx, ry = w / 2, rh / 2
    ex, ey, r = shade((H, W), cx, cy, rx, ry)
    light = np.clip(.80 + .30 * (-ex * .35 - ey * .8) * .5, .5, 1.2)[..., None]

    back = np.zeros((H, W, 4), np.float32)
    inner = ellipse_mask(W, H, cx, cy, rx * .92, ry * .92)
    ring = ellipse_mask(W, H, cx, cy, rx, ry)
    far = np.clip(-ey, 0, 1)[..., None]
    back[..., :3] = INSIDE * light * (1 - .35 * far)
    back[..., 3] = inner * 255
    ringc = np.clip(ring - inner, 0, 1)
    back[..., :3] = np.where(ringc[..., None] > 0, RIM * light, back[..., :3])
    back[..., 3] = np.maximum(back[..., 3], ringc * 255)

    front = np.zeros((H, W, 4), np.float32)
    if bowl:
        ys = np.arange(H)[:, None].astype(np.float32)
        xs = np.arange(W)[None, :].astype(np.float32)
        nx = (xs - cx) / rx
        top = cy + ry * np.sqrt(np.clip(1 - nx ** 2, 0, 1))
        bottom = cy + ry * .55 + depth * np.sqrt(np.clip(1 - (nx / .82) ** 2, 0, 1)) - depth * .1
        body = ((ys >= top - 1) & (ys <= bottom) & (np.abs(nx) <= 1)).astype(np.float32)
        grad = np.clip(1 - (ys - top) / np.maximum(bottom - top, 1), 0, 1)
        tone = ((0.55 + 0.6 * grad) * np.clip(1.05 - np.abs(nx) * .35, .6, 1.1))[..., None]
        front[..., :3] = BODY * tone
        front[..., 3] = body * 255
        lip = ((r <= 1.02) & (r >= .93) & (ey > -.05)).astype(np.float32)
        lipc = np.clip(1 - np.abs(r - .975) / .045, 0, 1) * (ey > -.05)
        front[..., :3] = np.where(lipc[..., None] > 0, RIM * light * 1.05, front[..., :3])
        front[..., 3] = np.maximum(front[..., 3], lipc * 255)
    back_im = Image.fromarray(np.clip(back, 0, 255).astype(np.uint8), "RGBA")
    front_im = Image.fromarray(np.clip(front, 0, 255).astype(np.uint8), "RGBA")
    shadow = Image.fromarray((np.clip(1 - (np.hypot((np.arange(W)[None, :] - cx) / (rx * 1.02), (np.arange(H)[:, None] - (cy + ry * .55 + depth * .9)) / (ry * .9))), 0, 1) * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(w * .025))
    return back_im, front_im, shadow, (cx, cy, rx, ry)


def plated(pid):
    f = cutout(pid)
    fw, fh = f.size
    if pid in BOWL:
        w = int(fw * 1.26)
        depth = int(w * .24)
        back, front, shadow, (cx, cy, rx, ry) = dish(w, depth, rim_ratio=.36, bowl=True)
        fx = int(cx - fw / 2)
        fy = int(cy + ry + fh * .16) - fh
    elif pid in PLATTER:
        w = int(fw * 1.2)
        depth = int(w * .04)
        back, front, shadow, (cx, cy, rx, ry) = dish(w, depth, rim_ratio=min(.6, 1.35 * fh / w), bowl=False)
        fx = int(cx - fw / 2)
        fy = int(cy - fh / 2)
    else:
        w = int(max(fw * 1.25, fh * 1.4))
        depth = int(w * .04)
        back, front, shadow, (cx, cy, rx, ry) = dish(w, depth, rim_ratio=.60, bowl=False)
        fx = int(cx - fw / 2)
        fy = int(cy + ry * .30) - fh
    W, H = back.size
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    canvas.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (W, H), (0, 0, 0)).split(), shadow.point(lambda v: int(v * .5)))))
    canvas.alpha_composite(back)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rgb = ImageEnhance.Contrast(f.convert("RGB")).enhance(1.05)
    rgb.putalpha(f.getchannel("A"))
    layer.alpha_composite(rgb, (max(fx, 0), max(fy, 0)))
    if pid in BOWL:
        ys = np.arange(H)[:, None].astype(np.float32)
        xs = np.arange(W)[None, :].astype(np.float32)
        nx = (xs - cx) / rx
        bottom = cy + ry * .55 + depth * np.sqrt(np.clip(1 - (nx / .82) ** 2, 0, 1)) - depth * .1
        allowed = ((np.abs(nx) <= .90) & (ys <= bottom)).astype(np.float32)
        allowed = np.array(Image.fromarray((allowed * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(2))).astype(np.float32) / 255
        la = np.array(layer.getchannel("A")).astype(np.float32) * allowed
        layer.putalpha(Image.fromarray(la.astype(np.uint8), "L"))
    else:
        sil = f.getchannel("A").point(lambda v: 255 if v > 60 else 0)
        contact = sil.resize((int(fw * .96), max(2, int(fh * .10))), Image.LANCZOS)
        sh = Image.new("L", (W, H), 0)
        sh.paste(contact, (fx + int(fw * .02), fy + fh - int(fh * .05)))
        sh = sh.filter(ImageFilter.GaussianBlur(fw * .03)).point(lambda v: int(v * .6))
        canvas.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (W, H), (8, 5, 4)).split(), sh)))
    canvas.alpha_composite(layer)
    canvas.alpha_composite(front)
    box = canvas.getbbox()
    return canvas.crop(box) if box else canvas


def main():
    ids = sys.argv[1:] or sorted(set(BOWL) | PLATE | PLATTER)
    for pid in ids:
        try:
            im = place(plated(pid), .88 if pid in PLATTER else .80, sharpen=25)
            save(finish(im), pid)
            print(f"  {pid}: plated", flush=True)
        except Exception as exc:
            import traceback
            traceback.print_exc()
            print(f"  {pid}: ERROR {exc}", flush=True)
    sheet()


if __name__ == "__main__":
    main()
