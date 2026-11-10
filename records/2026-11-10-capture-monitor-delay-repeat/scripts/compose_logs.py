#!/usr/bin/env python3
"""compose_logs.py LOG_DIR OUT_DIR: the check driver's output as two terminal pictures (pre/ and spec/ like compose.py).
Pillow draws the plain terminal text; put.gd's editor then draws the call-outs listed in spec/."""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
logs, out = sys.argv[1:3]
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 15); STEP = 21; RED = '#ff2d55'
def render(name, files, note):
    lines = []
    for f in files: lines += [l.rstrip('\n') for l in open(os.path.join(logs, f + '.log'))] + ['']
    lines = lines[:-1]
    width = int(max(font.getlength(l) for l in lines) + 32)
    image = Image.new('RGB', (width, STEP * len(lines) + 28), '#16181d'); draw = ImageDraw.Draw(image); shapes = []
    for i, line in enumerate(lines):
        y = 14 + i * STEP
        colour = '#8ab4f8' if line.startswith('#') else '#ff7b72' if line.startswith('FAIL') else '#d7dae0'
        draw.text((16, y), line, font=font, fill=colour)
        if line.startswith('ok '): draw.text((16, y), 'ok', font=font, fill='#7ee787')
        if line.startswith('# ') and 'git tree' in line:
            x0 = 16 + font.getlength(line[:line.index('put.gd')]); shapes.append({'kind': 'rectangle', 'rect': [int(x0) - 4, y - 3, int(font.getlength(line[line.index('put.gd'):])) + 8, STEP + 3], 'color': RED, 'width': 2})
        if 'session_locked' in line or 'helper_outdated' in line and line.startswith('monitor'):
            word = 'session_locked' if 'session_locked' in line else 'helper_outdated'
            x0 = 16 + font.getlength(line[:line.index(word)]); shapes.append({'kind': 'rectangle', 'rect': [int(x0) - 4, y - 3, int(font.getlength(word)) + 8, STEP + 3], 'color': RED, 'width': 2})
    # The rows under the header are short: the note sits to their right.
    shapes.append({'kind': 'text', 'at': [800, 50], 'text': note, 'color': RED, 'fontPixels': 17})
    image.save(os.path.join(out, 'pre', name + '.png')); json.dump(shapes, open(os.path.join(out, 'spec', name + '.json'), 'w')); print(name, image.size, len(shapes))
os.makedirs(out + '/pre', exist_ok=True); os.makedirs(out + '/spec', exist_ok=True)
render('13-checks-cinnamon-gnome', ['cinnamon', 'gnome', 'gnome-old'], 'boxed: build and tree (= PR head), the lock, the older extension')
render('14-checks-plasma-budgie-hyprland', ['kde', 'budgie', 'hyprland'], 'boxed: build and tree (= PR head), the lock')
