"""2x crops of every highlighted region in the headless exports, plus an index."""
import json, os, sys
from PIL import Image, ImageDraw
out, before, dest = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(dest + '/zoom', exist_ok=True)
lines = ['# Exports', '', 'Full exports: `*.png`; untouched captures: `before/`; 2x crops: `zoom/<case>-<n>.png` (left: before, right: after).', '']
for f in sorted(os.listdir(out)):
    if not f.endswith('.inspect.json'): continue
    case = f[:-len('.inspect.json')]
    d = json.load(open(os.path.join(out, f))).get('result', {})
    shapes = d.get('shapes') or []
    png = os.path.join(out, case + '.png')
    if not os.path.exists(png): lines.append(f'- {case}: no export'); continue
    after = Image.open(png).convert('RGB')
    src = before + '/' + case.split('-')[0] + '.png'
    bef = Image.open(src).convert('RGB')
    lines.append(f'## {case} ({after.width}x{after.height})'); lines.append('')
    for i, s in enumerate(shapes, 1):
        if s.get('kind') != 'highlight': continue
        x, y, w, h = s['rect']; pad = 14
        box = (max(0, x - pad), max(0, y - pad), min(after.width, x + w + pad), min(after.height, y + h + pad))
        a = after.crop(box); b = bef.crop(box)
        z = 2
        tile = Image.new('RGB', (a.width * z * 2 + 12, a.height * z), '#d4d4d0')
        tile.paste(b.resize((b.width * z, b.height * z), Image.NEAREST), (0, 0))
        tile.paste(a.resize((a.width * z, a.height * z), Image.NEAREST), (a.width * z + 12, 0))
        name = f'zoom/{case}-{i}.png'; tile.save(os.path.join(dest, name))
        lines.append(f'- mark {i}: colour {s.get("color")}, rect {s["rect"]} → `{name}`')
    lines.append('')
open(dest + '/index.md', 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
