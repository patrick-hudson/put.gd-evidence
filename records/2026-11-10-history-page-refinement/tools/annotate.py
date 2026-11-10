#!/usr/bin/env python3
"""Annotate History renders for the pull request: red boxes with numbered labels."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path('/home/patrick/work/put.gd-history-ui/work')
RED = (215, 38, 61)
FONT = None
for cand in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'):
    if Path(cand).exists():
        FONT = ImageFont.truetype(cand, 18)
        break

def annotate(src, dst, marks, banner):
    image = Image.open(src).convert('RGB')
    w, h = image.size
    probe = ImageDraw.Draw(image)
    # Legend lines under the title, wrapped to the picture's width.
    lines, line = [], ''
    for n, (box, label, where) in enumerate(marks, 1):
        item = f'{n}  {label}'
        trial = item if not line else line + '      ' + item
        if probe.textlength(trial, font=FONT) > w - 32 and line:
            lines.append(line); line = item
        else:
            line = trial
    if line: lines.append(line)
    bar = 40 + 28 * len(lines) + (6 if lines else 0)
    out = Image.new('RGB', (w, h + bar), RED)
    out.paste(image, (0, bar))
    draw = ImageDraw.Draw(out)
    draw.text((16, 9), banner, fill='white', font=FONT)
    for i, text in enumerate(lines):
        draw.text((16, 40 + 28 * i), text, fill='white', font=FONT)
    for n, (box, label, where) in enumerate(marks, 1):
        x0, y0, x1, y1 = box
        y0 += bar; y1 += bar
        draw.rectangle((x0, y0, x1, y1), outline=RED, width=3)
        s = 26
        if where == 'left': bx, by = x0 - s, y0
        elif where == 'right': bx, by = x1, y0
        elif where == 'below': bx, by = x0, y1
        elif where == 'above': bx, by = x0, y0 - s
        else: bx, by = x0, y0
        bx = max(0, min(w - s, bx)); by = max(bar, min(h + bar - s, by))
        draw.rectangle((bx, by, bx + s, by + s), fill=RED)
        tw = draw.textlength(str(n), font=FONT)
        draw.text((bx + (s - tw) / 2, by + 2), str(n), fill='white', font=FONT)
    dst.parent.mkdir(parents=True, exist_ok=True)
    out.save(dst, optimize=True)

def main():
    build = sys.argv[1]
    new = ROOT / 'build/fx1'
    old = ROOT / 'renders/realistic'
    out = ROOT / 'build/pictures/out'
    B = 'Before · nightly 77c9d278d'
    A = 'After · ' + build
    jobs = [
        (old / 'dark/r02-list-top-selected.png', '01-list-before-dark.png', B + ' · list with details, dark', [
            ((240, 124, 372, 160), 'Unlabelled number beside a 16 px heading', 'left'),
            ((240, 176, 300, 198), '12 px day label', 'left'),
            ((1066, 172, 1432, 204), 'No way to close the pane', 'left'),
            ((896, 882, 1054, 922), 'No page position', 'left'),
        ]),
        (new / 'dark/list.png', '02-list-after-dark.png', A + ' · list with details, dark', [
            ((240, 122, 416, 162), 'Page heading with a labelled count', 'left'),
            ((240, 168, 350, 194), 'Day heading with its count', 'left'),
            ((866, 214, 952, 396), 'Time column', 'right'),
            ((352, 226, 550, 248), 'Destination in the detail line', 'right'),
            ((1268, 120, 1312, 164), 'Details toggle', 'above'),
            ((1068, 180, 1428, 232), 'Pane title row with a close button', 'left'),
            ((618, 874, 1034, 914), 'Page position beside Previous / Next', 'left'),
            ((16, 126, 200, 320), 'Sidebar counts', 'below'),
        ]),
        (new / 'light/list-closed.png', '03-pane-closed-light.png', A + ' · details closed stays closed, light', [
            ((240, 272, 1414, 344), 'Selected; the pane stays closed until asked for', 'left'),
            ((1268, 120, 1312, 164), 'Details toggle (off)', 'below'),
            ((1004, 874, 1420, 914), 'Page position', 'above'),
        ]),
        (new / 'dark/page2.png', '04-page2-dark.png', A + ' · page 2, dark', [
            ((240, 166, 562, 192), 'A day continued from page 1 says so', 'right'),
            ((988, 874, 1420, 914), 'Page 2 of 5 · items 51–100 of 236', 'above'),
        ]),
        (new / 'light/scrolled.png', '05-pinned-day-light.png', A + ' · scrolled mid-day, light', [
            ((240, 172, 384, 204), 'The day heading stays pinned while its rows scroll', 'right'),
        ]),
        (old / 'dark/r12-search-filters.png', '06-filters-before-dark.png', B + ' · search and filters, dark', []),
        (new / 'dark/filtered.png', '07-filters-after-dark.png', A + ' · search and filters, dark', [
            ((240, 122, 438, 162), 'Count follows category, search and filters', 'right'),
            ((240, 172, 764, 212), 'Filters as chips: click to edit, × to remove', 'right'),
        ]),
        (old / 'light/r15-multiselect.png', '08-multiselect-before-light.png', B + ' · three rows selected, light', []),
        (new / 'light/multi.png', '09-multiselect-after-light.png', A + ' · three rows selected, pane closed, light', [
            ((240, 120, 1280, 164), 'Selection bar in the header', 'left'),
        ]),
        (old / 'dark/r10-failed.png', '10-failed-before-dark.png', B + ' · Failed uploads, dark', []),
        (new / 'dark/failed.png', '11-failed-after-dark.png', A + ' · Failed uploads, dark', [
            ((352, 198, 720, 224), 'Names where the upload was going', 'right'),
            ((1236, 190, 1350, 604), 'Date and time, no day sections', 'left'),
        ]),
        (old / 'dark/r13-gallery-top.png', '12-gallery-before-dark.png', B + ' · gallery, dark', []),
        (new / 'dark/gallery.png', '13-gallery-after-dark.png', A + ' · gallery, dark', [
            ((240, 174, 350, 200), 'Day sections in the gallery', 'right'),
            ((252, 392, 522, 458), 'Two-line names, detail line with time', 'below'),
            ((252, 484, 524, 652), 'Actions on the picture', 'right'),
        ]),
        (ROOT / 'build/fxc1/dark/history-in-progress.png', '15-in-progress-dark.png', A + ' · uploads in progress (catalog), dark', [
            ((240, 254, 340, 280), 'In progress section above the days', 'right'),
            ((240, 212, 1048, 250), 'Active-uploads band stays under the header', 'left'),
        ]),
        (new / 'light/scale-150/compact-150.png', '14-compact-150-light.png', A + ' · 1060×680 at 150 % text, light', []),
    ]
    for src, name, banner, marks in jobs:
        annotate(src, out / name, marks, banner)
        print(name)

main()
