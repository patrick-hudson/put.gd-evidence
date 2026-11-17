#!/usr/bin/env python3
"""seam.py RUN OUT IY0 IY1 RY0 RY1 SCALE: image rows IY0..IY1 beside reference rows RY0..RY1."""
import sys
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None
run, out = sys.argv[1], sys.argv[2]
iy0, iy1, ry0, ry1 = map(int, sys.argv[3:7]); scale = float(sys.argv[7])
tiles = []
for name, y0, y1 in (('capture', iy0, iy1), ('reference', ry0, ry1)):
    im = Image.open(f'{run}/{name}.png').convert('RGB')
    t = im.crop((0, y0, im.width, min(y1, im.height)))
    t = t.resize((int(t.width * scale), int(t.height * scale)))
    d = ImageDraw.Draw(t)
    for y in range(((y0 + 99) // 100) * 100, y1, 100):
        yy = int((y - y0) * scale); d.line((0, yy, 12, yy), fill=(255, 0, 0)); d.text((14, yy - 6), str(y), fill=(255, 0, 0))
    d.rectangle((0, 0, 260, 14), fill=(255, 255, 255)); d.text((3, 1), f'{run} {name} {y0}-{y1}', fill=(200, 0, 0))
    tiles.append(t)
o = Image.new('RGB', (sum(t.width + 10 for t in tiles), max(t.height for t in tiles)), 'white')
x = 0
for t in tiles:
    o.paste(t, (x, 0)); x += t.width + 10
o.save(out)
