"""Second-distance check of Alice's height in game units.
1) scale k of Alice from the far frame (v-0) to the near frame (w-f100, camera 100 units closer);
2) her vertical shift in the near frame when the camera drops 40 units (w-f100-m40).
Height in units = (392 px * k) / (shift_px / 40)."""
import numpy as np
from PIL import Image
S = r"C:/Users/Tefa/AppData/Local/Temp/claude/D--Program-Files--x86--Steam-steamapps-common/83896c25-936b-49aa-9e03-2eb792c66e2b/scratchpad/"
L = lambda n: np.asarray(Image.open(S + n).convert("L"), dtype=np.float32)
def z(p): return (p - p.mean()) / (p.std() + 1e-6)

far, near, near40 = L("v-0.png"), L("w-f100.png"), L("w-f100-m40.png")
# template: Alice's upper body in the far frame (head to hem), anchored at its centre
fx0, fx1, fy0, fy1 = 585, 700, 305, 590
T = far[fy0:fy1, fx0:fx1]
best = (-9, None)
for k in np.arange(1.30, 1.90, 0.01):
    t = np.asarray(Image.fromarray(T).resize((int(T.shape[1] * k), int(T.shape[0] * k)), Image.BILINEAR), dtype=np.float32)
    tz = z(t); th, tw = t.shape
    for cy in range(380, 560, 2):
        for cx in range(620, 680, 2):
            ya, xa = cy - th // 2, cx - tw // 2
            if ya < 0 or xa < 0 or ya + th > 720 or xa + tw > 1280: continue
            c = float((z(near[ya:ya + th, xa:xa + tw]) * tz).mean())
            if c > best[0]: best = (c, (round(k, 2), cy, cx))
print("far->near scale k = %.2f  (centre y %d x %d, corr %.3f)" % (best[1][0], best[1][1], best[1][2], best[0]))
k = best[1][0]

nx0, nx1, ny0, ny1 = 545, 740, 280, 600
T2 = z(near[ny0:ny1, nx0:nx1]); h, w = T2.shape
b2 = (-9, None)
for dy in range(-260, 20):
    for dx in range(-10, 11, 2):
        ya, xa = ny0 + dy, nx0 + dx
        if ya < 0 or ya + h > 720: continue
        c = float((z(near40[ya:ya + h, xa:xa + w]) * T2).mean())
        if c > b2[0]: b2 = (c, (dy, dx))
dy = b2[1][0]
print("near frame, camera -40 units: shift %d px (corr %.3f) -> %.3f px/unit" % (dy, b2[0], -dy / 40.0))
H = 392.0 * k / (-dy / 40.0)
print("Alice height = %.1f game units (far-frame height 392 px x k %.2f)" % (H, k))
