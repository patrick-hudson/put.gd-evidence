#!/usr/bin/env python3
"""compose.py RAW_DIR OUT_DIR VERSION

Arranges the raw #1363 pictures (crops side by side, with an empty caption bar over each panel) and writes,
for every picture, OUT_DIR/pre/NAME.png and OUT_DIR/spec/NAME.json: the call-outs (boxes, arrows, caption
text) that put.gd's own editor then draws on it (annotate.py). Pillow only crops and arranges here.
"""
import json, os, sys
from PIL import Image

raw, out, version = sys.argv[1:4]
os.makedirs(out + '/pre', exist_ok=True); os.makedirs(out + '/spec', exist_ok=True)
BAR = 36; GAP = 10; RED = '#ff2d55'
def crop(name, box=None, scale=1.0):
    image = Image.open(os.path.join(raw, name + '.png')).convert('RGB')
    if box: image = image.crop(box)
    if scale != 1.0: image = image.resize((round(image.width * scale), round(image.height * scale)), Image.LANCZOS)
    return image
def caption(x, y, text): return {'kind': 'text', 'at': [x + 10, y + 7], 'text': text, 'color': '#ffffff', 'fontPixels': 19}
def box(x, y, w, h): return {'kind': 'rectangle', 'rect': [x, y, w, h], 'color': RED, 'width': 3}
def arrow(x1, y1, x2, y2): return {'kind': 'arrow', 'from': [x1, y1], 'to': [x2, y2], 'color': RED, 'width': 4}
def label(x, y, text, size=20): return {'kind': 'text', 'at': [x, y], 'text': text, 'color': RED, 'fontPixels': size}
def arrange(name, panels, columns):
    """panels: (image, caption text, shapes relative to the panel image). Laid out in a grid of `columns`."""
    rows = [panels[i:i + columns] for i in range(0, len(panels), columns)]
    widths = [max(row[c][0].width for row in rows if c < len(row)) for c in range(columns)]
    heights = [max(p[0].height for p in row) for row in rows]
    total = Image.new('RGB', (sum(widths) + GAP * (columns - 1), sum(heights) + (BAR + GAP) * len(rows) - GAP), '#101114')
    shapes = []; y = 0
    for r, row in enumerate(rows):
        x = 0
        for c, (image, text, marks) in enumerate(row):
            total.paste(image, (x, y + BAR)); shapes.append(caption(x, y, text))
            for mark in marks:
                mark = json.loads(json.dumps(mark))
                if 'rect' in mark: mark['rect'][0] += x; mark['rect'][1] += y + BAR
                if 'from' in mark:
                    for key in ('from', 'to'): mark[key][0] += x; mark[key][1] += y + BAR
                if 'at' in mark: mark['at'][0] += x; mark['at'][1] += y + BAR
                shapes.append(mark)
            x += widths[c] + GAP
        y += heights[r] + BAR + GAP
    total.save(os.path.join(out, 'pre', name + '.png')); json.dump(shapes, open(os.path.join(out, 'spec', name + '.json'), 'w'), ensure_ascii=False)
    print(name, total.size, len(shapes), 'shapes')

before = 'nightly 26.1109.4404 (32a9a763e)'; after = 'this PR, ' + version

# 01: the command band, before and after.
arrange('01-band-before-after', [
    (crop('before-dash', (0, 0, 1280, 112)), 'Before: ' + before + ', Cinnamon, 100%', []),
    (crop('raw-cinnamon-after-dash', (0, 0, 1280, 112)), 'After: ' + after + ', Cinnamon, 100%', [box(346, 62, 154, 40), label(850, 14, 'new: Capture monitor'), arrow(842, 30, 506, 76)]),
], 1)

# 02: the tray menu on Cinnamon, before and after.
arrange('02-tray-before-after', [
    (crop('before-tray', (860, 290, 1280, 770)), 'Before: ' + before, []),
    (crop('raw-cinnamon-after-tray', (860, 290, 1280, 770)), 'After: ' + after, [box(166, 89, 250, 25), box(166, 141, 250, 25), box(166, 193, 250, 25), box(34, 190, 132, 116), label(6, 60, 'new entries', 18)]),
], 2)

# 03: Settings, Shortcuts.
arrange('03-shortcuts-before-after', [
    (crop('before-shortcuts', (232, 172, 1024, 742)), 'Before: ' + before, []),
    (crop('raw-cinnamon-after-shortcuts', (232, 172, 1024, 742)), 'After: ' + after, [box(20, 144, 752, 48), box(20, 248, 752, 48), label(250, 157, 'new, not set by default', 18), label(250, 261, 'new, not set by default', 18)]),
], 2)

# 04: the capture buttons' context menu, every desktop.
menu = [box(84, 26, 362, 178)]
arrange('04-rail-menu-desktops', [
    (crop('raw-cinnamon-after-rail', (0, 56, 470, 276)), 'Cinnamon (X11), ' + version, menu),
    (crop('raw-gnome-rail', (67, 88, 537, 308)), 'GNOME 50, ' + version, menu),
    (crop('raw-kde-rail', (0, 56, 470, 276)), 'Plasma 6.6, ' + version, menu),
    (crop('raw-budgie-rail', (0, 56, 470, 276)), 'Budgie (labwc), ' + version, menu),
    (crop('raw-hyprland-rail', (12, 94, 482, 314)), 'Hyprland (Omarchy), ' + version, menu),
], 3)

# 05: the tray menu, every desktop.
arrange('05-tray-menu-desktops', [
    (crop('raw-cinnamon-after-tray', (860, 290, 1280, 770)), 'Cinnamon', [box(166, 89, 250, 25), box(166, 141, 250, 25), box(166, 193, 250, 25)]),
    (crop('raw-gnome-tray', (1030, 28, 1280, 790)), 'GNOME 50', [box(22, 127, 222, 32), box(22, 199, 222, 32), box(22, 271, 222, 32)]),
    (crop('raw-kde-tray', (880, 200, 1270, 750)), 'Plasma 6.6', [box(22, 98, 222, 27), box(22, 156, 222, 27), box(22, 214, 222, 27)]),
    (crop('raw-budgie-tray', (500, 200, 1000, 760)), 'Budgie (labwc)', [box(20, 109, 320, 26), box(20, 165, 320, 26), box(20, 221, 320, 26)]),
    (crop('raw-hyprland-tray', (990, 0, 1260, 470)), 'Hyprland (Omarchy)', [box(24, 131, 222, 28), box(24, 191, 222, 28), box(24, 251, 222, 28)]),
], 5)

# 06: the countdown, every desktop.
def pill(cy): return [box(266, cy - 21, 268, 42), arrow(120, cy, 256, cy)]
arrange('06-countdown-desktops', [
    (crop('raw-cinnamon-countdown', (240, 0, 1040, 100)), 'Cinnamon (X11): a window of putgd-capture, ' + version, pill(30)),
    (crop('raw-gnome-countdown', (240, 0, 1040, 100)), 'GNOME 50: drawn by the put.gd Shell extension, below the top bar', pill(70)),
    (crop('raw-kde-countdown', (112, 0, 912, 100)), 'Plasma 6.6: an overlay layer surface of putgd-region', pill(30)),
    (crop('raw-budgie-countdown', (112, 0, 912, 100)), 'Budgie (labwc): an overlay layer surface of putgd-region', pill(30)),
    (crop('raw-hyprland-countdown', (240, 0, 1040, 100)), 'Hyprland (Omarchy): an overlay layer surface, below the bar', pill(54)),
], 1)

# 07: two monitors and the single-monitor capture.
desk = Image.new('RGB', (1152, 400), '#101114'); desk.paste(crop('raw-cinnamon-desk-head0', None, 0.5), (0, 0)); desk.paste(crop('raw-cinnamon-desk-head1', None, 0.5), (640, 0))
arrange('07-two-monitors-one-capture', [
    (desk, 'The desk: 1280x800 and 1024x768, pointer on the right monitor (Cinnamon, ' + version + ')', [box(641, 1, 510, 382), label(660, 350, 'pointer is here', 18)]),
    (crop('raw-cinnamon-hover-capture', None, 0.75), 'Capture monitor: that monitor alone, at its own 1024x768 (shown at 75%)', []),
], 1)

# 08: a delayed capture keeps what the delay was for.
arrange('08-delay-keeps-open-menu', [
    (crop('raw-cinnamon-hover-during', None, 0.75), 'During the 5 s countdown: the menu stays open', [box(292, 8, 184, 30), arrow(560, 120, 480, 34), box(388, 312, 170, 204)]),
    (crop('raw-cinnamon-hover-capture', None, 0.75), 'The capture: the menu is in it, the countdown is not', [box(388, 312, 170, 204)]),
], 2)

# 09: Repeat last region with nothing to repeat.
arrange('09-repeat-refusal', [
    (crop('raw-cinnamon-repeat-refusal', (0, 0, 1280, 300)), 'Repeat last region before any region capture (Cinnamon, ' + version + ')', [box(779, 8, 484, 126), box(240, 200, 600, 76)]),
], 1)

# 10: Desktop support details on GNOME while an older extension is loaded.
arrange('10-desktop-support-gnome', [
    (crop('raw-gnome-old-support', (67, 32, 1280, 800)), 'GNOME 50 with the previous extension still loaded, ' + version, [box(256, 486, 746, 96), label(770, 440, 'new rows, with the reason', 18)]),
], 1)

# 11, 12: the window at 100% and at 150%.
arrange('11-window-100', [
    (crop('raw-cinnamon-after-dash', (0, 0, 1280, 760)), 'put.gd at 100% (Cinnamon, 1280 px wide): every label in full, ' + version, [box(346, 62, 154, 40)]),
], 1)
arrange('12-window-150', [
    (crop('raw-kde-dash150', (192, 0, 1728, 1118)), 'put.gd at 150% (Plasma 6.6, 1024 logical px wide): Window, Monitor and Desktop shorten first, ' + version, [box(380, 98, 126, 50)]),
], 1)
