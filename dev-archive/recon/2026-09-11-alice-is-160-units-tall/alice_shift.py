"""Measure how far Alice's image moves (and whether it scales) when the proxy's
head offset lowers the camera. Template-matches Alice's body from the 0-offset
frame in each shifted frame, over vertical offsets and a small scale range."""
import numpy as np
from PIL import Image
S = r"C:/Users/Tefa/AppData/Local/Temp/claude/D--Program-Files--x86--Steam-steamapps-common/83896c25-936b-49aa-9e03-2eb792c66e2b/scratchpad/"

def load(n):
    return np.asarray(Image.open(S + n).convert("L"), dtype=np.float32)

base = load("v-0.png")
# Alice's body in the zero frame: find it first (dress is dark blue, boots black);
# use a generous box around the figure seen in u-0.png: x 560..720, y 300..710.
x0, x1, y0, y1 = 570, 710, 370, 700
tmpl = base[y0:y1, x0:x1]
tmpl = (tmpl - tmpl.mean()) / (tmpl.std() + 1e-6)

def best(img, scales=(0.96, 0.98, 1.0, 1.02, 1.04), dys=range(-200, 40), dxs=range(-12, 13, 2)):
    top = (-9, None)
    h, w = tmpl.shape
    for s in scales:
        if s != 1.0:
            t = np.asarray(Image.fromarray(tmpl).resize((max(1, int(w * s)), max(1, int(h * s)))), dtype=np.float32)
        else:
            t = tmpl
        th, tw = t.shape
        cx, cy = x0 + w / 2, y0 + h / 2          # keep the figure centre as the anchor
        for dy in dys:
            for dx in dxs:
                ya = int(round(cy + dy - th / 2)); xa = int(round(cx + dx - tw / 2))
                if ya < 0 or xa < 0 or ya + th > img.shape[0] or xa + tw > img.shape[1]:
                    continue
                p = img[ya:ya + th, xa:xa + tw]
                p = (p - p.mean()) / (p.std() + 1e-6)
                c = float((p * t).mean())
                if c > top[0]:
                    top = (c, (s, dy, dx))
    return top

for n, off in (("v-0back.png", 0), ("v-m20.png", -20), ("v-m40.png", -40), ("v-m60.png", -60), ("v-m80.png", -80)):
    c, (s, dy, dx) = best(load(n))
    print("%-12s offset %4d  -> dy %4d px  dx %3d  scale %.2f  corr %.3f" % (n, off, dy, dx, s, c))
