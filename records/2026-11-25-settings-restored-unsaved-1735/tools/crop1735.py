#!/usr/bin/env python3
"""Crop the uncropped #1735 frames to put.gd's window (1160x1000 at 100,20 on the 1920x1080 desktop).
usage: crop1735.py RUN_ROOT OUT_DIR   (RUN_ROOT holds before-2/frames and after-3/frames)"""
import sys
from pathlib import Path
from PIL import Image
root, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
x, y, w, h = 100, 20, 1160, 1000
PICTURES = {
    '1-restored-before.png': 'before-2/frames/before-restored-full.png',
    '2-refused-before.png': 'before-2/frames/before-action-full.png',
    '3-renamed-after.png': 'after-3/frames/after-renamed-full.png',
    '4-upload-clipboard-after.png': 'after-3/frames/after-action-full.png',
}
for name, frame in PICTURES.items():
    Image.open(root / frame).convert('RGB').crop((x, y, x + w, y + h)).save(out / name)
    print(name)
