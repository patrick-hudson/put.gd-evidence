import sys
from PIL import Image, ImageDraw, ImageFont
src, dst, box, label, colour = sys.argv[1], sys.argv[2], [int(v) for v in sys.argv[3].split(',')], sys.argv[4], sys.argv[5]
im = Image.open(src).convert('RGB'); d = ImageDraw.Draw(im)
for i in range(6): d.rectangle([box[0]-i, box[1]-i, box[2]+i, box[3]+i], outline=colour)
try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 34)
except OSError: font = ImageFont.load_default()
tw = d.textlength(label, font=font); x = box[0]; y = max(40, box[1] - 60)
d.rectangle([x, y, x + tw + 24, y + 50], fill=colour); d.text((x + 12, y + 6), label, fill='white', font=font)
im.save(dst)
