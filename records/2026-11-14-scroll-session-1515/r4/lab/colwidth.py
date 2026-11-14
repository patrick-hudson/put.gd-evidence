#!/usr/bin/env python3
"""colwidth.py RUN Y0 Y1 STEP: per band, the rightmost column holding text (light pixels on GitHub's dark page)."""
import sys
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
run, y0, y1, step = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
a = np.asarray(Image.open(run + '/capture.png').convert('L')).astype(int)
for y in range(y0, min(y1, a.shape[0]), step):
    band = a[y:y + step, :1800]
    cols = np.nonzero((band > 150).sum(axis=0) >= 2)[0]
    print(y, int(cols.max()) if len(cols) else -1, int(cols.min()) if len(cols) else -1)
