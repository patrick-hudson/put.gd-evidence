#!/usr/bin/env python3
"""where.py RUN ROW...: for each image row band (64 rows from ROW), the reference row it matches best (grey, mean abs diff)."""
import sys
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
run = sys.argv[1]
a = np.asarray(Image.open(run + '/capture.png').convert('L')).astype(np.float32)
b = np.asarray(Image.open(run + '/reference.png').convert('L')).astype(np.float32)
w = min(a.shape[1], b.shape[1]) - 40
for r in map(int, sys.argv[2:]):
    band = a[r:r + 64, 20:20 + w]
    best, at = 1e9, -1
    for y in range(max(0, r - 1500), min(b.shape[0] - 64, r + 1500)):
        d = float(np.abs(b[y:y + 64, 20:20 + w] - band).mean())
        if d < best:
            best, at = d, y
    print(f'image row {r}: reference row {at} (shift {at - r:+d}), mean diff {best:.1f}')
