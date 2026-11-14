#!/usr/bin/env python3
"""banner.py RUN... : rows of the cookie banner's colour above the image's last screen (page rows)."""
import json, sys
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
for run in sys.argv[1:]:
    a = np.asarray(Image.open(run + '/capture.png').convert('RGB')).astype(int)
    view = json.load(open(run + '/result.json'))['rect'][3]
    H = a.shape[0]
    tail = a[H - 150:H].reshape(-1, 3)
    dark = tail[tail.sum(axis=1) < 250]
    if len(dark) == 0:
        print(run, 'no dark tail'); continue
    vals, counts = np.unique(dark // 4 * 4, axis=0, return_counts=True)
    navy = vals[counts.argmax()]
    near = np.abs(a - navy).max(axis=2) <= 12
    rows = near.sum(axis=1) >= 40
    print('%-24s banner colour %s  banner rows in the page (above the last screen): %d of %d' % (run, navy.tolist(), int(rows[:H - view].sum()), H - view))
