#!/usr/bin/env python3
"""fills.py FILLS.txt [PHASE,...] [--top N]: boxes of image rows the tracker's
finish() filled (default phase 'plain' = the flat-colour fill). Rows are page
rows; subtract the image's top (first line 'top' of results or min row) for
image rows. Prints connected boxes on an 8 x 8 grid, biggest first."""
import sys, collections
path = sys.argv[1]
phases = set((sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else 'plain').split(','))
grid = set(); allrows = []
for line in open(path):
    ph, r, x0, x1 = line.split()
    r, x0, x1 = int(r), int(x0), int(x1)
    allrows.append(r)
    if ph not in phases: continue
    for gx in range(x0 // 8, (x1 + 7) // 8):
        grid.add((r // 8, gx))
seen = set(); boxes = []
for g in grid:
    if g in seen: continue
    seen.add(g); todo = [g]; cells = []
    while todo:
        c = todo.pop(); cells.append(c)
        for d in ((1,0),(-1,0),(0,1),(0,-1)):
            n = (c[0]+d[0], c[1]+d[1])
            if n in grid and n not in seen: seen.add(n); todo.append(n)
    ys = [c[0] for c in cells]; xs = [c[1] for c in cells]
    boxes.append((len(cells), min(xs)*8, min(ys)*8, (max(xs)+1)*8, (max(ys)+1)*8))
boxes.sort(reverse=True)
print('phases', sorted(phases), 'cells8x8', len(grid), 'boxes', len(boxes))
for n, x0, y0, x1, y1 in boxes[:int(sys.argv[sys.argv.index('--top')+1]) if '--top' in sys.argv else 15]:
    print(f'  {n:6d} cells  x {x0}-{x1}  rows {y0}-{y1}  ({x1-x0}x{y1-y0})')
