"""Before/after picture for #1838: the same crop of two redacted captures, one
above the other, each neighbour word the cover touched outlined in red, and a
caption. Usage: annotate.py FIXTURE_DIR OUT.png CROP(x0,y0,x1,y1) SCALE
  LABEL1 IMAGE1 CHECK1.json LABEL2 IMAGE2 CHECK2.json"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT = '/usr/share/fonts/google-noto/NotoSans-Regular.ttf'
RED = (215, 38, 61)


def panel(image_path, check_path, crop, scale, label):
    image = Image.open(image_path).convert('RGB').crop(crop)
    image = image.resize((image.width * scale, image.height * scale), Image.NEAREST)
    draw = ImageDraw.Draw(image)
    words = json.loads(Path(check_path).read_text())['words']
    touched = 0
    for word in words:
        if word['role'] != 'neighbour' or not word['changed']:
            continue
        x0, y0, x1, y1 = word['box']
        if x1 < crop[0] or x0 > crop[2] or y1 < crop[1] or y0 > crop[3]:
            continue
        touched += 1
        box = [(x0 - crop[0] - 3) * scale, (y0 - crop[1] - 3) * scale, (x1 - crop[0] + 3) * scale, (y1 - crop[1] + 3) * scale]
        draw.rectangle(box, outline=RED, width=3)
    font = ImageFont.truetype(FONT, 22)
    head = Image.new('RGB', (image.width, 40), (255, 255, 255))
    caption = f'{label}: {touched} neighbouring word{"s" if touched != 1 else ""} covered (outlined)' if touched else f'{label}: no neighbouring word covered'
    ImageDraw.Draw(head).text((8, 6), caption, font=font, fill=RED if touched else (20, 110, 40))
    out = Image.new('RGB', (image.width, image.height + 40), (255, 255, 255))
    out.paste(head, (0, 0))
    out.paste(image, (0, 40))
    return out


def main():
    fixture, target, crop, scale = sys.argv[1], sys.argv[2], tuple(int(v) for v in sys.argv[3].split(',')), int(sys.argv[4])
    panels = [panel(sys.argv[i + 1], sys.argv[i + 2], crop, scale, sys.argv[i]) for i in range(5, len(sys.argv), 3)]
    width = max(p.width for p in panels)
    out = Image.new('RGB', (width + 4, sum(p.height for p in panels) + 12 * (len(panels) - 1) + 4), (200, 200, 200))
    y = 2
    for p in panels:
        out.paste(p, (2, y))
        y += p.height + 12
    out.save(target)


main()
