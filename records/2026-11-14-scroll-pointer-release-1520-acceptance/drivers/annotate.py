#!/usr/bin/env python3
"""annotate.py IN OUT --crop X,Y,W,H --box X,Y,W,H:LABEL [--box ...]: crop a desktop frame and call out parts."""
import argparse
from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument('src')
ap.add_argument('out')
ap.add_argument('--crop')
ap.add_argument('--box', action='append', default=[])
a = ap.parse_args()
im = Image.open(a.src).convert('RGB')
ox = oy = 0
if a.crop:
    x, y, w, h = [int(v) for v in a.crop.split(',')]
    im = im.crop((x, y, x + w, y + h))
    ox, oy = x, y
d = ImageDraw.Draw(im)
try:
    font = ImageFont.truetype('/usr/share/fonts/google-noto-vf/NotoSans[wght].ttf', 18)
except OSError:
    font = ImageFont.load_default()
gold = (232, 168, 0)
for spec in a.box:
    rect, _, label = spec.partition(':')
    x, y, w, h = [int(v) for v in rect.split(',')]
    x -= ox
    y -= oy
    for i in range(4):
        d.rectangle((x - i, y - i, x + w + i, y + h + i), outline=gold)
    if label:
        tw = d.textlength(label, font=font)
        ty = y - 30 if y - 30 > 0 else y + h + 6
        d.rectangle((x - 3, ty - 2, x + tw + 9, ty + 24), fill=gold)
        d.text((x + 3, ty), label, fill=(20, 20, 20), font=font)
im.save(a.out)
print(a.out, im.size)
