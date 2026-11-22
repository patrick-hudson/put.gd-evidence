"""Draw a review image: upload, missed tokens in red boxes, wrongly changed near misses in orange, over-cover in magenta."""
import json, sys
from PIL import Image, ImageDraw
up, chk, out = sys.argv[1:4]
crop = [int(v) for v in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
d = json.load(open(chk))
im = Image.open(up).convert('RGB'); dr = ImageDraw.Draw(im)
for t in d['tokens']:
    if t.get('pass') is False:
        x0,y0,x1,y1 = t['bbox']; dr.rectangle((x0-3,y0-3,x1+3,y1+3), outline=(230,0,0) if t['expect']=='covered' else (255,140,0), width=3)
for r in d.get('overCoverRects', []):
    dr.rectangle((r[0]-2,r[1]-2,r[2]+2,r[3]+2), outline=(220,0,220), width=2)
if crop: im = im.crop(crop)
im.save(out)
