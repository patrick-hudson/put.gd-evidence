#!/usr/bin/env python3
"""tails.py OUT ROWS RUN...: each run's capture's last ROWS rows, left half, stacked."""
import sys
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None
out, rows = sys.argv[1], int(sys.argv[2])
ims = []
for run in sys.argv[3:]:
    im = Image.open(f'{run}/capture.png').convert('RGB')
    t = im.crop((0, im.height - rows, im.width // 2, im.height)).resize((im.width // 4, rows // 2))
    d = ImageDraw.Draw(t); d.rectangle((0, 0, 330, 16), fill=(255, 255, 255)); d.text((4, 2), run, fill=(200, 0, 0))
    ims.append(t)
o = Image.new('RGB', (max(i.width for i in ims), sum(i.height + 8 for i in ims)), 'white')
y = 0
for i in ims:
    o.paste(i, (0, y)); y += i.height + 8
o.save(out)
