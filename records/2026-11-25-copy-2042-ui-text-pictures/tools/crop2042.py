#!/usr/bin/env python3
"""Crop the uncropped frames to put.gd's own dialogs, panels, tooltips and bars.
usage: crop2042.py FRAMES_DIR OUT_DIR   (FRAMES_DIR holds before-<scene>-full.png and after-<scene>-full.png)"""
import sys
from pathlib import Path
from PIL import Image
frames, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
CROPS = {  # name: (scene frame, (left, top, width, height))
    '1-history-delete-dialog': ('history-delete-dialog', (360, 110, 580, 510)),
    '2-editor-blur-switch-to-redact': ('editor-blur', (880, 130, 460, 260)),
    '2b-editor-discard-dialog': ('editor-discard-dialog', (530, 335, 430, 200)),
    '3-editor-upload-tooltip': ('editor-upload-tooltip', (1100, 860, 500, 130)),
    '4-scroll-bar-paused': ('scroll-paused-mouse', (140, 880, 620, 110)),
}
for label in ('before', 'after'):
    for name, (scene, (x, y, w, h)) in CROPS.items():
        Image.open(frames / ('%s-%s-full.png' % (label, scene))).convert('RGB').crop((x, y, x + w, y + h)).save(out / ('%s-%s.png' % (name, label)))
        print(label, name)
