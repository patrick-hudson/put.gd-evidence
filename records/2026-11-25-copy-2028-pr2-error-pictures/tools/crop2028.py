#!/usr/bin/env python3
"""Crop the uncropped frames to put.gd's own windows and notifications.
usage: crop2028.py FRAMES_DIR OUT_DIR   (FRAMES_DIR holds before-<scene>-full.png and after-<scene>-full.png)"""
import sys
from pathlib import Path
from PIL import Image
frames, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
CROPS = {  # name: (scene frame, (left, top, width, height))
    '1-error-log-queue-full-2034': ('errorlog-queue-full', (336, 176, 1024, 670)),
    '2-notification-own-window-2036': ('toast-own-window-late', (1410, 0, 510, 200)),
    '3-editor-over-limit-2037': ('editor-over-limit', (40, 40, 920, 640)),
}
for label in ('before', 'after'):
    for name, (scene, (x, y, w, h)) in CROPS.items():
        Image.open(frames / ('%s-%s-full.png' % (label, scene))).convert('RGB').crop((x, y, x + w, y + h)).save(out / ('%s-%s.png' % (name, label)))
        print(label, name)
