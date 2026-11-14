#!/usr/bin/env python3
"""side.py OUT SCALE RUN...: each run's capture beside its browser's picture, scaled, in one row."""
import sys
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
out, scale = sys.argv[1], float(sys.argv[2])
tiles = []
for run in sys.argv[3:]:
    for name in ('capture.png', 'reference.png'):
        try:
            im = Image.open(f'{run}/{name}').convert('RGB')
            tiles.append(im.resize((int(im.width * scale), int(im.height * scale))))
        except Exception:
            pass
h = max(t.height for t in tiles)
o = Image.new('RGB', (sum(t.width + 12 for t in tiles), h), 'white')
x = 0
for t in tiles:
    o.paste(t, (x, 0)); x += t.width + 12
o.save(out)
