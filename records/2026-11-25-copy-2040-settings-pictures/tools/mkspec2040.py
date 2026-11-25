#!/usr/bin/env python3
"""Write spec.json for annotate2040.py: a #D7263D rectangle around the changed description and a label.
Coordinates are in the 1160x1000 crops."""
import json
RED = '#D7263D'
def rect(x, y, w, h): return {'kind': 'rectangle', 'rect': [x, y, w, h], 'color': RED, 'width': 3}
def text(at, t, px=20): return {'kind': 'text', 'at': list(at), 'text': t, 'color': RED, 'fontPixels': px}
B, A = 'Before (nightly)', 'After (#2040)'
spec = {
    '1-resource-limits-memory-for-queued-images-before.png': [rect(506, 822, 340, 146), text((858, 830), B)],
    '1-resource-limits-memory-for-queued-images-after.png': [rect(506, 822, 332, 84), text((850, 830), A)],
    '2-capture-region-selection-while-selecting-before.png': [rect(256, 614, 736, 64), text((780, 522), B)],
    '2-capture-region-selection-while-selecting-after.png': [rect(256, 614, 736, 50), text((780, 522), A)],
    '3-advanced-debug-logging-before.png': [rect(256, 766, 738, 48), text((640, 736), B)],
    '3-advanced-debug-logging-after.png': [rect(256, 748, 738, 44), text((640, 716), A)],
    '4-resource-limits-largest-file-before.png': [rect(510, 286, 342, 176), text((862, 300), B)],
    '4-resource-limits-largest-file-after.png': [rect(510, 286, 336, 80), text((856, 300), A)],
    '5-capture-check-for-sensitive-text-before.png': [rect(256, 574, 726, 70), text((640, 540), B)],
    '5-capture-check-for-sensitive-text-after.png': [rect(256, 574, 726, 44), text((640, 540), A)],
}
json.dump(spec, open('spec.json', 'w'), indent=1)
