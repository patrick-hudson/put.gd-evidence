#!/usr/bin/env python3
"""cutscan.py RUNDIR [IMAGE] [--rows N]: white boxes over ink (#1557).
Capture (or IMAGE) vs reference.png, row-aligned per 64-row band by the best
small shift (+-40): cells of 8x8 where the capture is white (min>248) and the
reference has ink (min<220); clusters >= 120 missing pixels, >=16 wide."""
import sys, json
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
run = sys.argv[1]
img = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else run + '/capture.png'
rows = int(sys.argv[sys.argv.index('--rows') + 1]) if '--rows' in sys.argv else 3000
a = np.asarray(Image.open(img).convert('L')).astype(np.int16)
b = np.asarray(Image.open(run + '/reference.png').convert('L')).astype(np.int16)
W = min(a.shape[1], b.shape[1]) - 24  # leave out the scrollbar
H = min(rows, a.shape[0])
mask = np.zeros((H, W), bool)
shifts = []
for y0 in range(0, H, 64):
    y1 = min(H, y0 + 64)
    best = None
    for s in range(-40, 41):
        if y0 + s < 0 or y1 + s > b.shape[0]: continue
        d = np.abs(a[y0:y1, :W] - b[y0 + s:y1 + s, :W]).mean()
        if best is None or d < best[0]: best = (d, s)
    s = best[1]; shifts.append(s)
    mask[y0:y1] = (a[y0:y1, :W] > 248) & (b[y0 + s:y1 + s, :W] < 220)
gh, gw = (H + 7) // 8, (W + 7) // 8
grid = np.zeros((gh, gw), bool)
yy, xx = np.where(mask); grid[yy // 8, xx // 8] = True
seen = np.zeros_like(grid); boxes = []
for gy, gx in zip(*np.where(grid)):
    if seen[gy, gx]: continue
    todo = [(gy, gx)]; seen[gy, gx] = True; cells = []
    while todo:
        cy, cx = todo.pop(); cells.append((cy, cx))
        for ny, nx in ((cy-1,cx),(cy+1,cx),(cy,cx-1),(cy,cx+1)):
            if 0 <= ny < gh and 0 <= nx < gw and grid[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True; todo.append((ny, nx))
    ys = [c[0] for c in cells]; xs = [c[1] for c in cells]
    x0, y0, x1, y1 = int(min(xs))*8, int(min(ys))*8, int(max(xs)+1)*8, int(max(ys)+1)*8
    n = int(mask[y0:y1, x0:x1].sum())
    if n >= 120 and x1 - x0 >= 16:
        boxes.append({'box': [x0, y0, x1, y1], 'missing': n})
print(json.dumps({'run': run.rstrip('/').split('/')[-1], 'image': img.split('/')[-1], 'rows': H, 'shiftsUsed': sorted(set(shifts)), 'boxes': boxes}, default=int))
