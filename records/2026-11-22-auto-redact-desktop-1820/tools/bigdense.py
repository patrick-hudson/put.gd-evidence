"""Dense synthetic pages as files: bigdense.py OUT W H — 9 px monospace lorem with a test card every 9th line."""
import sys
from PIL import Image, ImageDraw, ImageFont
out, w, h = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
im = Image.new('L', (w, h), 255); d = ImageDraw.Draw(im)
try:
    f = ImageFont.truetype('DejaVuSansMono.ttf', 9)
except OSError:
    f = ImageFont.load_default()
words = 'lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor'.split()
y, n = 2, 0
while y < h - 12:
    line = ' '.join(words[(n + i) % len(words)] for i in range(w // 30)); n += 7
    if (y // 11) % 9 == 4:
        line = line[:60] + ' 4111 1111 1111 1111 ' + line[60:]
    d.text((2, y), line, font=f, fill=0); y += 11
im.save(out)
