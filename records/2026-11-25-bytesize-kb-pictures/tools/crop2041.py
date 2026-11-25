#!/usr/bin/env python3
"""Crop the uncropped frames to put.gd's own windows.
usage: crop2041.py FRAMES_DIR OUT_DIR   (FRAMES_DIR holds before-<scene>-full.png and after-<scene>-full.png)"""
import sys
from pathlib import Path
from PIL import Image
frames, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
CROPS = {  # name: (scene frame, (left, top, width, height)); the windows' geometry is in results/*-facts.json
    '1-editor-size-limit-kb': ('editor-over-limit', (40, 40, 920, 640)),
    '2-history-size-under-1-kb': ('history-details', (120, 20, 1240, 1000)),
}
for label in ('before', 'after'):
    for name, (scene, (x, y, w, h)) in CROPS.items():
        Image.open(frames / ('%s-%s-full.png' % (label, scene))).convert('RGB').crop((x, y, x + w, y + h)).save(out / ('%s-%s.png' % (name, label)))
        print(label, name)
