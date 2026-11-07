#!/usr/bin/env python3
"""Before/after figures: 'before' reproduces the old 41 % source-over fill on the
same rects the real app snapped to; 'after' is the real app's saved copy."""
import json, sys
from PIL import Image, ImageDraw, ImageFont
CASES = {
 'cinnamon': ((380, 250, 930, 700), 'Cinnamon Update Manager (light, LCD text)'),
 'history': ((50, 40, 760, 420), 'put.gd History on Mint (dark, zebra rows)'),
 'plasma': ((540, 410, 1270, 720), 'Kubuntu Plasma notification and wallpaper'),
 'aurora': ((100, 380, 620, 720), 'Aurora: notice over a painting, painting'),
}
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
def hexrgb(h): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
rows = []
for name, (view, title) in CASES.items():
    try:
        after = Image.open(f'out/{name}.png').convert('RGB')
        shapes = json.load(open(f'out/{name}.inspect.json'))['result']['shapes']
    except Exception as e:
        print('skip', name, e); continue
    before = Image.open(f'caps/{name}.png').convert('RGB')
    overlay = Image.new('RGBA', before.size, (0, 0, 0, 0)); d = ImageDraw.Draw(overlay)
    for s in shapes:
        x, y, w, h = s['rect']; d.rectangle([x, y, x + w - 1, y + h - 1], fill=hexrgb(s.get('color', '#facc15')) + (105,))
    before = Image.alpha_composite(before.convert('RGBA'), overlay).convert('RGB')
    b, a = before.crop(view), after.crop(view)
    # Call out the snapped rects on the after image.
    ad = ImageDraw.Draw(a)
    for s in shapes:
        x, y, w, h = s['rect']; ad.rectangle([x - view[0] - 3, y - view[1] - 3, x - view[0] + w + 2, y - view[1] + h + 2], outline=(255, 0, 255), width=2)
    rows.append((title, b, a))
W = max(b.width + a.width + 30 for _, b, a in rows); H = sum(max(b.height, a.height) + 40 for _, b, a in rows) + 30
sheet = Image.new('RGB', (W, H), (236, 236, 236)); d = ImageDraw.Draw(sheet)
d.text((10, 6), 'Before: 41 % translucent fill (reproduced on the same rects)', font=font, fill=(20, 20, 20))
d.text((W // 2 + 10, 6), 'After: background-tinting marker, snapped to text (real app export; magenta = the stored rect)', font=font, fill=(20, 20, 20))
y = 30
for title, b, a in rows:
    d.text((10, y + 4), title, font=small, fill=(60, 60, 60))
    sheet.paste(b, (10, y + 22)); sheet.paste(a, (b.width + 20, y + 22))
    y += max(b.height, a.height) + 40
sheet.save(sys.argv[1]); print(sheet.size)
