#!/usr/bin/env python3
"""Crop the uncropped frames to put.gd's Settings window (1160x1000 at 100,20 on the 1920x1080 desktop).
usage: crop2040.py FRAMES_DIR OUT_DIR   (FRAMES_DIR holds before-<scene>-full.png and after-<scene>-full.png)"""
import sys
from pathlib import Path
from PIL import Image
frames, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
WINDOW = (100, 20, 1160, 1000)  # left, top, width, height
PICTURES = {  # picture name: frame scene
    '1-resource-limits-memory-for-queued-images': 'limits-tooltip',
    '2-capture-region-selection-while-selecting': 'region-help',
    '3-advanced-debug-logging': 'debug-logging',
    '4-resource-limits-largest-file': 'largest-file-tooltip',
    '5-capture-check-for-sensitive-text': 'sensitive-text-pre',
}
x, y, w, h = WINDOW
for label in ('before', 'after'):
    for name, scene in PICTURES.items():
        Image.open(frames / ('%s-%s-full.png' % (label, scene))).convert('RGB').crop((x, y, x + w, y + h)).save(out / ('%s-%s.png' % (name, label)))
        print(label, name)
