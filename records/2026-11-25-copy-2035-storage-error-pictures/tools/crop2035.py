#!/usr/bin/env python3
"""Crop the uncropped d69 frames to put.gd's own window (placed by KWin at 40,60, 1440x900, in the run's log).
usage: crop2035.py FRAMES_DIR OUT_DIR   (frames named <before|after>-history-<http|sftp>-full.png)"""
import sys
from pathlib import Path
from PIL import Image
frames, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
X, Y, W, H = 40, 60, 1440, 900
NAMES = {'http': '1-custom-uploader-closed-port', 'sftp': '2-sftp-closed-port'}
for label in ('before', 'after'):
    for scene, name in NAMES.items():
        Image.open(frames / ('%s-history-%s-full.png' % (label, scene))).convert('RGB').crop((X, Y, X + W, Y + H)).save(out / ('%s-%s.png' % (name, label)))
        print(label, name)
