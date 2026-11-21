#!/usr/bin/env python3
"""panel.py OUT.png TITLE X0,Y0,X1,Y1 HX0,HY0,HX1,HY1 LABEL=IMAGE[@SHIFT] ...
Side-by-side crops of the same page rows (image rows Y0..Y1, columns X0..X1; SHIFT moves that image's rows),
each with a caption, the area HX0.. outlined in red. For PR pictures (#1557)."""
import sys
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
out, title = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = map(int, sys.argv[3].split(',')); hx0, hy0, hx1, hy1 = map(int, sys.argv[4].split(','))
def font(n):
    for f in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf', '/usr/share/fonts/google-noto/NotoSans-Bold.ttf'):
        try: return ImageFont.truetype(f, n)
        except OSError: pass
    return ImageFont.load_default()
F, T = font(18), font(20)
tiles = []
for arg in sys.argv[5:]:
    label, path = arg.split('=', 1)
    shift = 0
    if '@' in path: path, shift = path.rsplit('@', 1); shift = int(shift)
    im = Image.open(path).convert('RGB').crop((x0, y0 + shift, x1, y1 + shift))
    d = ImageDraw.Draw(im)
    d.rectangle((hx0 - x0, hy0 - y0, hx1 - x0, hy1 - y0), outline=(215, 38, 61), width=4)
    tiles.append((label, im))
w, h = x1 - x0, y1 - y0; gap = 16; cap = 34; top = 40
o = Image.new('RGB', (len(tiles) * w + (len(tiles) - 1) * gap + 2 * gap, top + cap + h + gap), (255, 255, 255))
d = ImageDraw.Draw(o)
d.text((gap, 10), title, fill=(20, 20, 20), font=T)
for i, (label, im) in enumerate(tiles):
    x = gap + i * (w + gap)
    d.text((x, top + 6), label, fill=(215, 38, 61), font=F)
    o.paste(im, (x, top + cap))
o.save(out)
print(out, o.size)
