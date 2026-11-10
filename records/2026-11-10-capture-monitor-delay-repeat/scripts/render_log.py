#!/usr/bin/env python3
"""render_log.py OUT.png LOG...: the check driver's terminal output as a picture (plain text, monospace)."""
import sys
from PIL import Image, ImageDraw, ImageFont
out, logs = sys.argv[1], sys.argv[2:]
font = None
for path in ('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', '/usr/share/fonts/dejavu-sans-mono-fonts/DejaVuSansMono.ttf', '/usr/share/fonts/TTF/DejaVuSansMono.ttf'):
    try: font = ImageFont.truetype(path, 15); break
    except OSError: pass
if font is None: raise SystemExit('no monospace font found')
lines = []
for log in logs:
    lines += [line.rstrip('\n') for line in open(log)] + ['']
lines = lines[:-1]
width = max(font.getlength(line) for line in lines) + 32; step = 21
image = Image.new('RGB', (int(width), step * len(lines) + 28), '#16181d'); draw = ImageDraw.Draw(image)
for i, line in enumerate(lines):
    colour = '#8ab4f8' if line.startswith('#') else '#ff7b72' if line.startswith('FAIL') else '#d7dae0'
    draw.text((16, 14 + i * step), line, font=font, fill=colour)
    if line.startswith('ok '): draw.text((16, 14 + i * step), 'ok', font=font, fill='#7ee787')
image.save(out); print(out, image.size)
