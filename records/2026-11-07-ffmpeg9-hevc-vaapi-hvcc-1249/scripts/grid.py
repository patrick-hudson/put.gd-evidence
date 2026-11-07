"""usage: grid.py OUT.png TITLE LABEL=PNG... -- stacks 7-frame contact sheets (2240x180) with a label column, scaled to half size."""
import sys
from PIL import Image, ImageDraw, ImageFont
out, title, rows = sys.argv[1], sys.argv[2], [a.split('=', 1) for a in sys.argv[3:]]
W, H, L, T = 1120, 90, 300, 36
g = Image.new('RGB', (L + W, T + H * len(rows)), (24, 24, 24))
d = ImageDraw.Draw(g)
try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15); big = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)
except OSError: font = big = ImageFont.load_default()
d.text((8, 8), title, fill=(240, 240, 240), font=big)
for i, (label, path) in enumerate(rows):
    y = T + i * H
    g.paste(Image.open(path).convert('RGB').resize((W, H)), (L, y))
    for j, line in enumerate(label.split('|')):
        d.text((8, y + 12 + j * 20), line, fill=(240, 200, 80) if 'FAIL' in line else (220, 220, 220), font=font)
g.save(out)
