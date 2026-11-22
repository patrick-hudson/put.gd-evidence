"""Before/after picture for #1839/#1840/#1846/#1850: the same crop of two redacted captures stacked,
each matched word whose ink still shows outlined in red and each neighbour word a cover touched
outlined in orange, with captions. Usage:
annotate_leaks.py OUT.png CROP(x0,y0,x1,y1) SCALE LABEL1 IMAGE1 CHECK1.json LABEL2 IMAGE2 CHECK2.json"""
import json, sys
from PIL import Image, ImageDraw, ImageFont
FONT = '/usr/share/fonts/google-noto/NotoSans-Regular.ttf'
RED, ORANGE = (215, 38, 61), (230, 140, 0)
def panel(path, check, crop, scale, label):
    im = Image.open(path).convert('RGB').crop(crop)
    im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    d = ImageDraw.Draw(im)
    leaks = touched = 0
    for w in json.load(open(check))['words']:
        x0, y0, x1, y1 = w['box']
        if x1 < crop[0] or x0 > crop[2] or y1 < crop[1] or y0 > crop[3]:
            continue
        colour = RED if w['role'] == 'matched' and w['shown'] else ORANGE if w['role'] == 'neighbour' and w['changed'] else None
        if not colour:
            continue
        leaks += colour == RED; touched += colour == ORANGE
        d.rectangle([(x0 - crop[0] - 3) * scale, (y0 - crop[1] - 3) * scale, (x1 - crop[0] + 3) * scale, (y1 - crop[1] + 3) * scale], outline=colour, width=3)
    font = ImageFont.truetype(FONT, 18)
    head = Image.new('RGB', (im.width, 40), (245, 245, 245))
    ImageDraw.Draw(head).text((10, 7), f'{label}: {leaks} still showing (red), {touched} neighbours touched (orange)', fill=(20, 20, 20), font=font)
    out = Image.new('RGB', (im.width, im.height + 40), 'white'); out.paste(head, (0, 0)); out.paste(im, (0, 40))
    return out
a = sys.argv
crop = tuple(int(v) for v in a[2].split(',')); scale = int(a[3])
p1 = panel(a[5], a[6], crop, scale, a[4]); p2 = panel(a[8], a[9], crop, scale, a[7])
out = Image.new('RGB', (p1.width, p1.height + p2.height + 8), (215, 38, 61)); out.paste(p1, (0, 0)); out.paste(p2, (0, p1.height + 8))
out.save(a[1]); print(a[1], out.size)
