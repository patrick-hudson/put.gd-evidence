#!/usr/bin/env python3
"""barcheck.py RUN_DIR X0 X1 : rows of capture.png with a dark run wider than 150 px between
columns X0 and X1 (the bar's dark body would leave one on a light page), and a picture of the
image's last 700 rows."""
import sys
import numpy as np
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None
run, x0, x1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
im = Image.open(run + '/capture.png').convert('RGB')
a = np.asarray(im)
dark = a[:, x0:x1].max(axis=2) < 70
hits = []
for y in range(a.shape[0]):
    d = np.diff(np.concatenate([[0], dark[y].astype(np.int8), [0]]))
    s, e = np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]
    if len(s) and (e - s).max() > 150:
        hits.append(y)
print(run, 'rows with a dark run over 150 px in the bar columns:', len(hits), hits[:10], '... last', hits[-5:] if hits else '')
H = a.shape[0]
tail = im.crop((0, max(0, H - 700), im.width, H))
d = ImageDraw.Draw(tail)
tail.save(run + '/tail.png')
