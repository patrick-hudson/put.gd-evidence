"""Held-out check: new seeds, sizes not tuned on, each item inside a sentence.
Truth boxes cover the item's characters only. Throwaway, never committed."""
import importlib.util, json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
spec = importlib.util.spec_from_file_location('g', sys.argv[2]); g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
FONTS = g.FONTS; paths = {n: next(Path('/usr/share/fonts').rglob(n)) for n in FONTS}
k = 0
for font in FONTS:
    for size in (12, 13, 16, 24):
        k += 1; dark = k % 2 == 0; name = f'held-{font}-{size}-{dark}'
        image = Image.new("RGB", (3600, 1500), '#202124' if dark else 'white'); draw = ImageDraw.Draw(image)
        face = ImageFont.truetype(str(paths[font]), size); y = 12; truth = []
        for category, text in g.items(5000 + k):
            for n, line in enumerate(text.split('\n')):
                before = 'Please keep this value private: ' if n == 0 else ''
                after = ' (expires next week).' if '\n' not in text or n == text.count('\n') else ''
                x0 = 12 + draw.textlength(before, font=face)
                draw.text((12, y), before + line + after, font=face, fill='white' if dark else 'black')
                box = draw.textbbox((x0, y), line, font=face)
                truth.append(dict(category=category, text_codepoints=list(map(ord, line)), box=[int(box[0]), box[1], int(box[2]) + 1, box[3]]))
                y += size + 9
        image.save(out / (name + '.png')); (out / (name + '.truth.json')).write_text(json.dumps(dict(words=truth)))
print(k)
