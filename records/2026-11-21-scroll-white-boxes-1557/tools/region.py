#!/usr/bin/env python3
"""region.py RUNDIR TAG Y0 Y1 OUT.png: before (rr-base) | after (rr-TAG) | reference at the best shift, rows Y0..Y1 over the changed columns; prints off-reference counts."""
import sys
import numpy as np
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None
R, T, y0, y1, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
A = Image.open(R + '/rr-base/image.png').convert('RGB'); B = Image.open(R + '/rr-' + T + '/image.png').convert('RGB'); F = Image.open(R + '/reference.png').convert('RGB')
a = np.asarray(A.convert('L')).astype(int); b = np.asarray(B.convert('L')).astype(int); f = np.asarray(F.convert('L')).astype(int)
d = (a[y0:y1] != b[y0:y1]).any(0); xs = np.where(d)[0]
x0, x1 = (max(0, xs.min() - 40), min(a.shape[1], xs.max() + 40)) if len(xs) else (0, a.shape[1])
m0, m1 = max(0, y0 - 20), y1 + 20
best = min(range(-300, 301), key=lambda s: np.abs(b[m0:m1, x0:x1:2] - f[m0 + s:m1 + s, x0:x1:2]).mean() if m0 + s >= 0 and m1 + s <= f.shape[0] else 1e9)
print('shift', best, 'x', x0, x1, 'off before', int((np.abs(a[y0:y1, x0:x1] - f[y0 + best:y1 + best, x0:x1]) > 40).sum()), 'after', int((np.abs(b[y0:y1, x0:x1] - f[y0 + best:y1 + best, x0:x1]) > 40).sum()))
tiles = [A.crop((x0, m0, x1, m1)), B.crop((x0, m0, x1, m1)), F.crop((x0, m0 + best, x1, m1 + best))]
w, h = tiles[0].size
o = Image.new('RGB', (w, (h + 14) * 3), 'blue'); dr = ImageDraw.Draw(o)
for i, (t, n) in enumerate(zip(tiles, ['nightly', T, 'reference'])):
    o.paste(t, (0, i * (h + 14) + 14)); dr.text((2, i * (h + 14)), n, fill='yellow')
o.save(out)
