#!/bin/bash
# vcheck.sh TAG RUN...: replay through bin/replay-TAG (built if missing from ./TAG); compare with rr-base; fills outside the scrollbar; boxes; pixels off the reference where they differ
cd ~/work/w1557
T=$1; shift
[ -x bin/replay-$T ] || bash tools/rpt.sh $T $T > /dev/null
for R in "$@"; do
  if [ -n "$TOOLBOX" ]; then bash tools/arr.sh $T $R; else bash tools/rr.sh $T $R; fi
  python3 - $R $T <<'PY'
import sys
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
R, T = sys.argv[1], sys.argv[2]
a = np.asarray(Image.open(R + '/rr-base/image.png').convert('L')).astype(int)
b = np.asarray(Image.open(R + '/rr-' + T + '/image.png').convert('L')).astype(int)
ref = np.asarray(Image.open(R + '/reference.png').convert('L')).astype(int)
fills = sum(1 for l in open(R + '/rr-' + T + '/fills.txt') if l.startswith('plain ') and int(l.split()[2]) < 1896)
name = R.rstrip('/').split('/')[-1].replace('firefox-github-user-', '')
if a.shape != b.shape:
    print(name, T, 'height', a.shape[0], '->', b.shape[0], 'fills', fills); sys.exit()
d = (a != b)
n = int(d.sum())
msg = ''
if n:
    ys = np.where(d.any(1))[0]
    off_a = off_b = 0
    # rows that differ, in runs; per run the pixels off the reference (shift 0) before and after
    runs = []
    for y in ys:
        if runs and y - runs[-1][1] <= 8: runs[-1][1] = y
        else: runs.append([y, y])
    for y0, y1 in runs:
        y1 += 1
        m0, m1 = max(0, y0 - 40), min(b.shape[0], y1 + 40)
        best = None
        for s in range(-300, 301):
            if m0 + s < 0 or m1 + s > ref.shape[0]: continue
            e = np.abs(b[m0:m1, ::4] - ref[m0 + s:m1 + s, ::4]).mean() + np.abs(a[m0:m1, ::4] - ref[m0 + s:m1 + s, ::4]).mean()
            if best is None or e < best[0]: best = (e, s)
        if best is None: continue
        s = best[1]
        off_a += int((np.abs(a[y0:y1] - ref[y0 + s:y1 + s]) > 40).sum()); off_b += int((np.abs(b[y0:y1] - ref[y0 + s:y1 + s]) > 40).sum())
    msg = 'changed rows %s; off-reference %d -> %d' % ([(int(x), int(y)) for x, y in runs[:6]], off_a, off_b)
print(name, T, 'changed px', n, 'fills', fills, msg)
PY
done
