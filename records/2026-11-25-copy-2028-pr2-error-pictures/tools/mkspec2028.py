#!/usr/bin/env python3
"""Write spec.json for annotate2028.py: red (#D7263D) rectangle around the changed message, an arrow where there is room, and a label."""
import json
RED = '#D7263D'
def rect(x, y, w, h): return {'kind': 'rectangle', 'rect': [x, y, w, h], 'color': RED, 'width': 3}
def arrow(a, b): return {'kind': 'arrow', 'from': list(a), 'to': list(b), 'color': RED, 'width': 3}
def text(at, t, px=18): return {'kind': 'text', 'at': list(at), 'text': t, 'color': RED, 'fontPixels': px}
spec = {
    '1-error-log-queue-full-2034-before.png': [rect(26, 430, 210, 26), arrow((262, 443), (240, 443)), text((270, 433), 'Before (nightly)')],
    '1-error-log-queue-full-2034-after.png': [rect(26, 430, 808, 26), arrow((880, 443), (838, 443)), text((886, 433), 'After (#2034)', 16)],
    '2-notification-own-window-2036-before.png': [rect(52, 58, 364, 24), text((52, 150), 'Before (nightly)')],
    '2-notification-own-window-2036-after.png': [rect(52, 58, 406, 40), text((52, 162), 'After (#2036)')],
    '3-editor-over-limit-2037-before.png': [rect(60, 511, 734, 24), text((330, 548), 'Before (nightly)')],
    '3-editor-over-limit-2037-after.png': [rect(60, 511, 814, 24), text((330, 548), 'After (#2037)')],
}
json.dump(spec, open('spec.json', 'w'), indent=1)
