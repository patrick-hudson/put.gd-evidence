#!/usr/bin/env python3
"""Write spec.json for annotate2028.py: red (#D7263D) rectangles around the changed sizes, an arrow and a label."""
import json
RED = '#D7263D'
def rect(x, y, w, h): return {'kind': 'rectangle', 'rect': [x, y, w, h], 'color': RED, 'width': 3}
def arrow(a, b): return {'kind': 'arrow', 'from': list(a), 'to': list(b), 'color': RED, 'width': 3}
def text(at, t, px=18): return {'kind': 'text', 'at': list(at), 'text': t, 'color': RED, 'fontPixels': px}
spec = {
    '1-editor-size-limit-kb-before.png': [rect(60, 508, 812, 26), text((330, 556), 'Before (nightly): kB')],
    '1-editor-size-limit-kb-after.png': [rect(60, 508, 812, 26), text((330, 556), 'After (#2041): KB')],
    '2-history-size-under-1-kb-before.png': [rect(438, 268, 68, 26), rect(980, 521, 70, 28), arrow((930, 690), (1010, 556)), text((820, 700), 'Before (nightly): 300 B')],
    '2-history-size-under-1-kb-after.png': [rect(438, 268, 72, 26), rect(980, 521, 76, 28), arrow((930, 690), (1010, 556)), text((820, 700), 'After (#2041): 0.3 KB')],
}
json.dump(spec, open('spec.json', 'w'), indent=1)
