#!/usr/bin/env python3
"""unwritten.py RUN_DIR... : cells the tracker never wrote. The spool canvas starts
as zeros, so such a cell is pure black (0,0,0) across its whole 8-px span: a run
of pure black that starts and ends on the tracker's 8-column grid. Page content
that is pure black rarely does both."""
import sys
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
for run in sys.argv[1:]:
    a = np.asarray(Image.open(run + '/capture.png').convert('RGB'))
    H, W, _ = a.shape
    z = (a.max(axis=2) == 0)
    cells = 0
    rows = set()
    for y in np.nonzero(z.any(axis=1))[0]:
        d = np.diff(np.concatenate([[0], z[y].astype(np.int8), [0]]))
        for s, e in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]):
            if s % 8 == 0 and (e % 8 == 0 or e == W) and e - s >= 8:
                cells += (e - s + 7) // 8
                rows.add(int(y))
    first = min(rows) if rows else '-'
    print('%-40s %6d rows  unwritten cells %7d  in %5d rows  first %s' % (run.rstrip('/').split('/')[-1], H, cells, len(rows), first))
