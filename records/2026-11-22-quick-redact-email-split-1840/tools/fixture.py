"""#1838 desktop fixture: a 1920x1080 page of synthetic test text, drawn one word at a
time so every word's ink is known exactly. Writes fixture.png, labels.png (16-bit word
index + 1 where that word's coverage is at least 32/255) and words.json.
Usage: fixture.py OUTDIR"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

TOKEN = 'gh' + 'p_' + 'aB3dE5fG7hJ9kL1mN3pQ' + '5rS7tU9vW1xY3zA5'  # made-up test value from the unit tests
CARD = '4111 1111 1111 1111'  # the standard test card number
EMAIL = 'jane.doe@example.com'
# (text, matched word indexes, words find() also takes (#1839))
LINES = [
    ('Card ' + CARD, [1, 2, 3, 4], []),
    ('Your token ' + TOKEN + ' was leaked today', [2], [3, 4, 5]),
    ('Please write to ' + EMAIL + ' before Friday', [3], []),
    (CARD + ' is on file', [0, 1, 2, 3], []),
    ('Reach me at ' + EMAIL, [3], []),
]
FONTS = {
    'sans': '/usr/share/fonts/google-noto/NotoSans-Regular.ttf',
    'liberation': '/usr/share/fonts/liberation-sans-fonts/LiberationSans-Regular.ttf',
    'mono': '/usr/share/fonts/google-noto/NotoSansMono-Regular.ttf',
}
# block: (name, font, px, x, y, paper, ink, lines)
BLOCKS = [
    ('card-large', 'liberation', 40, 60, 40, (255, 255, 255), (0, 0, 0), [0]),
    ('sans-18', 'sans', 18, 60, 140, (255, 255, 255), (20, 20, 20), [0, 1, 2, 3, 4]),
    ('mono-15', 'mono', 15, 60, 340, (255, 255, 255), (30, 30, 30), [0, 1, 2, 3, 4]),
    ('dark-16', 'sans', 16, 60, 520, (30, 30, 30), (230, 230, 230), [0, 1, 2, 3, 4]),
    ('liberation-13', 'liberation', 13, 60, 720, (255, 255, 255), (0, 0, 0), [0, 1, 2, 3, 4]),
]


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    page = Image.new('RGB', (1920, 1080), (255, 255, 255))
    labels = Image.new('I;16', page.size, 0)
    words = []
    for name, font_name, px, x0, y0, paper, ink, lines in BLOCKS:
        font = ImageFont.truetype(FONTS[font_name], px)
        line_height = int(px * 1.9)
        width = 860 if x0 < 1000 else 860
        ImageDraw.Draw(page).rectangle([x0 - 20, y0 - 16, x0 - 20 + width, y0 + line_height * len(lines) + 6], fill=paper)
        space = font.getlength(' ')
        for row, line_index in enumerate(lines):
            text, matched, taken = LINES[line_index]
            x = float(x0)
            y = y0 + row * line_height
            for index, word in enumerate(text.split(' ')):
                mask = Image.new('L', page.size, 0)
                ImageDraw.Draw(mask).text((x, y), word, font=font, fill=255)
                page.paste(Image.new('RGB', page.size, ink), (0, 0), mask)
                box = mask.point(lambda v: 255 if v >= 32 else 0).getbbox()
                number = len(words) + 1
                labels.paste(number, (0, 0), mask.point(lambda v: 255 if v >= 32 else 0))
                words.append({'n': number, 'block': name, 'line': line_index, 'text': word, 'box': box,
                              'role': 'matched' if index in matched else 'taken-by-find' if index in taken else 'neighbour'})
                x += font.getlength(word) + space
    page.save(out / 'fixture.png')
    labels.save(out / 'labels.png')
    (out / 'words.json').write_text(json.dumps(words, indent=1))
    print(len(words), 'words')


main()
