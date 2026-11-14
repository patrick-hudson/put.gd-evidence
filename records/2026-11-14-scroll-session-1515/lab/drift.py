"""Where a capture's rows sit in the browser's own picture: for bands along the
capture, the vertical offset at which the reference matches best (grey, blurred)."""
import sys
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

def grey(path):
    a = np.asarray(Image.open(path).convert("L"), dtype=np.float32)
    return a

def run(name, step=2000):
    a = grey(name + "/capture.png"); b = grey(name + "/reference.png")
    w = min(a.shape[1], b.shape[1]) - 40
    out = []
    for y in range(500, a.shape[0] - 200, step):
        band = a[y:y + 128, 300:w]
        best = (1e9, None)
        for dy in range(-1200, 1201, 1):
            yy = y + dy
            if yy < 0 or yy + 128 > b.shape[0]:
                continue
            d = float(np.abs(band[::4, ::4] - b[yy:yy + 128:4, 300:w:4]).mean())
            if d < best[0]:
                best = (d, dy)
        out.append((y, best[1], round(best[0], 1)))
    print(name, out)

for n in sys.argv[1:]:
    run(n)
