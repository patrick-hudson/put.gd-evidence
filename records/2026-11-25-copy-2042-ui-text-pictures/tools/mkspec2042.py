#!/usr/bin/env python3
"""Write spec.json for annotate2042.py: #D7263D rectangles around the changed text and a Before / After label."""
import json
RED = '#D7263D'
def rect(x, y, w, h): return {'kind': 'rectangle', 'rect': [x, y, w, h], 'color': RED, 'width': 3}
def text(at, t, px=18): return {'kind': 'text', 'at': list(at), 'text': t, 'color': RED, 'fontPixels': px}
B, A = 'Before (nightly)', 'After (#2042)'
spec = {
    '1-history-delete-dialog-before.png': [rect(206, 10, 170, 28), rect(26, 88, 522, 46), text((28, 455), B)],
    '1-history-delete-dialog-after.png': [rect(180, 10, 222, 28), rect(26, 88, 520, 46), text((28, 455), A)],
    '2-editor-blur-switch-to-redact-before.png': [rect(256, 78, 164, 26), rect(256, 110, 134, 26), text((14, 40), B)],
    '2-editor-blur-switch-to-redact-after.png': [rect(256, 76, 190, 50), rect(256, 130, 118, 26), text((14, 40), A)],
    '2b-editor-discard-dialog-before.png': [rect(164, 11, 100, 24), rect(26, 54, 372, 58), text((18, 140), 'Before', 16)],
    '2b-editor-discard-dialog-after.png': [rect(98, 18, 148, 26), rect(50, 60, 198, 60), text((250, 66), 'After', 16)],
    '3-editor-upload-tooltip-before.png': [rect(170, 58, 312, 34), text((14, 80), B)],
    '3-editor-upload-tooltip-after.png': [rect(170, 58, 322, 50), text((14, 80), A)],
    '4-scroll-bar-paused-before.png': [rect(34, 18, 216, 48), text((16, 76), B)],
    '4-scroll-bar-paused-after.png': [rect(34, 18, 176, 48), text((16, 76), A)],
}
json.dump(spec, open('spec.json', 'w'), indent=1)
