#!/usr/bin/env python3
"""slice.py OUT Y0 Y1 SCALE RUN...: rows Y0..Y1 of each run's capture side by side."""
import sys
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None
out, y0, y1, scale = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
tiles = []
for run in sys.argv[5:]:
    im = Image.open(f'{run}/capture.png').convert('RGB')
    t = im.crop((0, y0, im.width, min(y1, im.height)))
    t = t.resize((int(t.width * scale), int(t.height * scale)))
    d = ImageDraw.Draw(t); d.rectangle((0, 0, 320, 14), fill=(255, 255, 255)); d.text((3, 1), f'{run} {y0}-{y1}', fill=(200, 0, 0))
    tiles.append(t)
o = Image.new('RGB', (sum(t.width + 10 for t in tiles), max(t.height for t in tiles)), 'white')
x = 0
for t in tiles:
    o.paste(t, (x, 0)); x += t.width + 10
o.save(out)
