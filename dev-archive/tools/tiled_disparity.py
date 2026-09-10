"""tiled_disparity.py L.png R.png [tile]
Phase-correlate each tile of a left/right pair and print the horizontal
disparity per tile as a grid. Sign: positive = feature sits further RIGHT in
R than in L. Depth correctness: nearer tiles should differ from farther ones
monotonically, and the whole map should shift when convergence changes.
"""
import sys
import numpy as np
from PIL import Image

def ld(p):
    return np.asarray(Image.open(p).convert("L"), dtype=np.float32)

def shift(a, b):
    a = a - a.mean(); b = b - b.mean()
    if a.std() < 2 or b.std() < 2:
        return None, 0.0
    A = np.fft.fft2(a); B = np.fft.fft2(b)
    R = A * np.conj(B); R /= (np.abs(R) + 1e-9)
    r = np.fft.ifft2(R).real
    y, x = np.unravel_index(r.argmax(), r.shape)
    if x > a.shape[1] // 2: x -= a.shape[1]
    return -int(x), float(r.max())   # -x so positive = b is right of a

L, R = ld(sys.argv[1]), ld(sys.argv[2])
t = int(sys.argv[3]) if len(sys.argv) > 3 else 160
rows = L.shape[0] // t; cols = L.shape[1] // t
print("tile=%d  grid %dx%d  (dx px, '.'=flat tile, ?=weak peak<0.05)" % (t, rows, cols))
for r in range(rows):
    line = []
    for c in range(cols):
        a = L[r*t:(r+1)*t, c*t:(c+1)*t]; b = R[r*t:(r+1)*t, c*t:(c+1)*t]
        dx, pk = shift(a, b)
        if dx is None: line.append("   . ")
        elif pk < 0.05: line.append("%+4d?" % dx)
        else: line.append("%+4d " % dx)
    print(" ".join(line))
