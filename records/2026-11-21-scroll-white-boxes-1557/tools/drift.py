#!/usr/bin/env python3
"""drift.py RUNDIR [IMAGE]: per 64-row band, the best shift against the reference within +-400 (coarse), printed where it changes."""
import sys
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
run = sys.argv[1]; img = sys.argv[2] if len(sys.argv) > 2 else run + '/capture.png'
a = np.asarray(Image.open(img).convert('L')).astype(np.int16)[:, :1880:2]
b = np.asarray(Image.open(run + '/reference.png').convert('L')).astype(np.int16)[:, :1880:2]
last = None
for y0 in range(0, a.shape[0] - 64, 64):
    best = None
    for s in range(-400, 401):
        if y0 + s < 0 or y0 + 64 + s > b.shape[0]: continue
        d = np.abs(a[y0:y0+64] - b[y0+s:y0+s+64]).mean()
        if best is None or d < best[0]: best = (d, s)
    if a[y0:y0+64].std() < 3: continue  # blank band: no evidence
    if best[1] != last:
        print(y0, 'shift', best[1], 'diff %.2f' % best[0]); last = best[1]
