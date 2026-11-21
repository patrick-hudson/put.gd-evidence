#!/usr/bin/env python3
"""pair.py RUNDIR X0,Y0,X1,Y1 OUT.png [IMAGE] [SHIFT]: capture | reference crop, 24 px margin."""
import sys
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None
run, box, out = sys.argv[1], [int(v) for v in sys.argv[2].split(',')], sys.argv[3]
img = sys.argv[4] if len(sys.argv) > 4 else run + '/capture.png'
s = int(sys.argv[5]) if len(sys.argv) > 5 else 0
a = Image.open(img).convert('RGB'); b = Image.open(run + '/reference.png').convert('RGB')
m = 24; x0, y0, x1, y1 = max(0, box[0]-m), max(0, box[1]-m), box[2]+m, box[3]+m
ca = a.crop((x0, y0, x1, y1)); cb = b.crop((x0, y0 + s, x1, y1 + s))
pic = Image.new('RGB', (ca.width * 2 + 12, ca.height + 16), 'white')
pic.paste(ca, (0, 16)); pic.paste(cb, (ca.width + 12, 16))
d = ImageDraw.Draw(pic); d.text((0, 2), 'capture %s' % box, fill='red'); d.text((ca.width + 12, 2), 'reference', fill='red')
d.rectangle((box[0]-x0, box[1]-y0+16, box[2]-x0, box[3]-y0+16), outline='red')
pic.save(out)
