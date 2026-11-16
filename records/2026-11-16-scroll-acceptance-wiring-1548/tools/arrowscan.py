#!/usr/bin/env python3
"""The acceptance's arrow-pair-scan.py method on any images (PR #1548, item 1).
arrowscan.py CONTROL.png IMAGE... : template = CONTROL's cursor at 1836,957 (25x29, pointer at
1840,960 over magenta), its black core (max<60) and white outline (min>245); an image matches
where >=97% of each class is dark (<80) / light (>225)."""
import json, sys
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
a = np.asarray(Image.open(sys.argv[1]).convert('RGB').crop((1836, 957, 1861, 986)))
bm, wm = a.max(2) < 60, a.min(2) > 245
assert bm.sum() > 15 and wm.sum() > 8, (bm.sum(), wm.sum())
black, white = list(zip(*np.where(bm))), list(zip(*np.where(wm)))
out = {'template': {'black': int(bm.sum()), 'white': int(wm.sum())}, 'images': []}
for f in sys.argv[2:]:
    im = np.asarray(Image.open(f).convert('RGB'))
    dark, light = im.max(2) < 80, im.min(2) > 225
    h, w = im.shape[0] - bm.shape[0] + 1, im.shape[1] - bm.shape[1] + 1
    hit = np.ones((h, w), bool)
    for pts, cls in ((black, dark), (white, light)):
        for j in np.linspace(0, len(pts) - 1, min(10, len(pts)), dtype=int):
            y, x = pts[j]
            hit &= cls[y:y + h, x:x + w]
    m = []
    for y, x in zip(*np.where(hit)):
        d = dark[y:y + bm.shape[0], x:x + bm.shape[1]][bm].mean()
        l = light[y:y + wm.shape[0], x:x + wm.shape[1]][wm].mean()
        if d >= .97 and l >= .97:
            m.append([int(x), int(y)])
    out['images'].append({'path': f, 'size': [im.shape[1], im.shape[0]], 'matches': m})
print(json.dumps(out, indent=1))
