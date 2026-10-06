import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_HD = os.path.join(HERE, "photos")
SRC_STUDIO = os.path.join(HERE, "sources", "studio")
SRC_LEGACY = os.path.join(HERE, "sources", "legacy")


def _dilate(m, n):
    for _ in range(n):
        g = m.copy()
        for sh, ax in ((1, 0), (-1, 0), (1, 1), (-1, 1)):
            g |= np.roll(m, sh, axis=ax)
        m = g
    return m


def _erode(m, n):
    return ~_dilate(~m, n)


def _spread(seed, allowed, steps=1400):
    cur = seed & allowed
    for _ in range(steps):
        g = cur.copy()
        for sh, ax in ((1, 0), (-1, 0), (1, 1), (-1, 1)):
            g |= np.roll(cur, sh, axis=ax)
        g &= allowed
        if g.sum() == cur.sum():
            break
        cur = g
    return cur
