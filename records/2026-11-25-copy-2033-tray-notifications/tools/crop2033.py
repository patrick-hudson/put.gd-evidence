#!/usr/bin/env python3
"""Crop the uncropped frames to put.gd's own tooltip, notifications and History window.
usage: crop2033.py FRAMES_DIR OUT_DIR   (frames named <before|after>-<scene>-full.png)"""
import sys
from pathlib import Path
from PIL import Image
frames, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
CROPS = {  # name: (scene frame, (left, top, width, height))
    '1-tray-tooltip': ('tooltip', (1500, 900, 420, 180)),
    '2-notification-failed-upload': ('toast-failure', (1410, 0, 510, 170)),
    '3-notification-diagnostics-saved': ('notification', (1410, 0, 510, 170)),
    '4-history-lost-reply': ('history-lost', (120, 20, 1240, 1000)),
}
for label in ('before', 'after'):
    for name, (scene, (x, y, w, h)) in CROPS.items():
        Image.open(frames / ('%s-%s-full.png' % (label, scene))).convert('RGB').crop((x, y, x + w, y + h)).save(out / ('%s-%s.png' % (name, label)))
        print(label, name)
