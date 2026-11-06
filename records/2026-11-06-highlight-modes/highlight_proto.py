#!/usr/bin/env python3
"""Prototype highlight compositing modes for put.gd issue research.

Renders text samples (light UI, dark UI, white-on-accent button, dark syntax
colors) and applies the same yellow highlight box with each candidate mode.
"""
import sys
from collections import Counter
from PIL import Image, ImageDraw, ImageFont, ImageChops

OUT = sys.argv[1]
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
MONO = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 21)
LABEL = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
W, H = 400, 64
HL = (250, 204, 21)  # put.gd default highlight
BOX = (14, 12, 386, 52)


def sample(kind):
    if kind == "light":
        im = Image.new("RGB", (W, H), (255, 255, 255)); d = ImageDraw.Draw(im)
        d.text((20, 18), "Uploaded to s3://bucket/a.png", font=FONT, fill=(31, 35, 40))
    elif kind == "dark":
        im = Image.new("RGB", (W, H), (13, 17, 23)); d = ImageDraw.Draw(im)
        d.text((20, 18), "Uploaded to s3://bucket/a.png", font=FONT, fill=(230, 237, 243))
    elif kind == "accent":
        im = Image.new("RGB", (W, H), (37, 99, 235)); d = ImageDraw.Draw(im)
        d.text((20, 18), "Upload and copy link", font=FONT, fill=(255, 255, 255))
    else:  # dark editor syntax
        im = Image.new("RGB", (W, H), (30, 30, 30)); d = ImageDraw.Draw(im)
        x = 20
        for text, color in (("const ", (86, 156, 214)), ("url", (156, 220, 254)), (" = ", (212, 212, 212)),
                            ('"put.gd/x"', (206, 145, 120)), (";", (212, 212, 212)), (" // ok", (106, 153, 85))):
            d.text((x, 19), text, font=MONO, fill=color); x += d.textlength(text, font=MONO)
    return im


def lum(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def mix(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def translucent(region):  # today's put.gd: alpha 105/255 source-over
    return Image.blend(region, Image.new("RGB", region.size, HL), 105 / 255)


def multiply(region):
    return ImageChops.multiply(region, Image.new("RGB", region.size, HL))


def darken(region):  # Greenshot's text highlighter: per-channel min
    return ImageChops.darker(region, Image.new("RGB", region.size, HL))


def ink_preserving(region):
    px = list(region.getdata())
    bins = Counter((r >> 4, g >> 4, b >> 4) for r, g, b in px)
    top, count = bins.most_common(1)[0]
    if count / len(px) < 0.35:  # no dominant background (photo, gradient)
        return multiply(region) if sum(lum(p) for p in px) / len(px) > 0.35 else translucent(region)
    members = [p for p in px if (p[0] >> 4, p[1] >> 4, p[2] >> 4) == top]
    bg = tuple(sum(c[i] for c in members) // len(members) for i in range(3))

    def dist(p):
        return sum((x - y) ** 2 for x, y in zip(p, bg)) ** 0.5

    # Ink colors: frequent bins far from the background (glyph cores, not edges).
    inks = [tuple(v * 16 + 8 for v in k) for k, n in bins.items()
            if n >= 0.01 * len(px) and k != top and dist(tuple(v * 16 + 8 for v in k)) > 90]
    if not inks:
        inks = [max(px, key=dist)]
    worst = min(contrast(i, bg) for i in inks)
    target = min(worst, 4.5)
    # Strongest tint of the highlight hue that keeps every ink readable.
    lo, hi = 0.0, 1.0
    if min(contrast(i, HL) for i in inks) >= target:
        lo = 1.0
    else:
        for _ in range(16):
            mid = (lo + hi) / 2
            if min(contrast(i, mix(bg, HL, mid)) for i in inks) >= target: lo = mid
            else: hi = mid
    new_bg = mix(bg, HL, max(lo, 0.28))
    shift = tuple(n - o for n, o in zip(new_bg, bg))
    T = 70.0
    out = []
    for p in px:
        a = min(1.0, dist(p) / T)  # 0 = pure background, 1 = ink
        out.append(tuple(max(0, min(255, round(c + (1 - a) * s))) for c, s in zip(p, shift)))
    res = Image.new("RGB", region.size); res.putdata(out)
    return res


def marker_recolor(region):
    """Full-strength marker everywhere; ink lighter than the marker turns dark, keeping its hue."""
    px = list(region.getdata())
    bins = Counter((r >> 4, g >> 4, b >> 4) for r, g, b in px)
    top, count = bins.most_common(1)[0]
    if count / len(px) < 0.35:
        return ink_preserving(region)
    members = [p for p in px if (p[0] >> 4, p[1] >> 4, p[2] >> 4) == top]
    bg = tuple(sum(c[i] for c in members) // len(members) for i in range(3))
    if lum(bg) > lum(HL) * 0.6:  # light page: same as the ink-preserving tint
        return ink_preserving(region)

    def dist(p):
        return sum((x - y) ** 2 for x, y in zip(p, bg)) ** 0.5
    T = 70.0
    cache = {}
    out = []
    for p in px:
        a = min(1.0, dist(p) / T)
        if a == 0:
            out.append(HL); continue
        ink = tuple(max(0, min(255, round(b + (c - b) / a))) for c, b in zip(p, bg)) if a < 1 else p
        if ink not in cache:
            f = 1.0
            while f > 0 and contrast(tuple(round(c * f) for c in ink), HL) < 4.5:
                f -= 0.05
            cache[ink] = tuple(round(c * max(f, 0)) for c in ink)
        out.append(mix(HL, cache[ink], a))
    res = Image.new("RGB", region.size); res.putdata(out)
    return res


MODES = [("Today: 41% translucent fill", translucent), ("Multiply", multiply),
         ("Darken (Greenshot)", darken), ("Ink-preserving background tint", ink_preserving),
         ("Full marker, light ink darkened", marker_recolor)]
KINDS = ["light", "dark", "accent", "syntax"]

pad, head = 12, 30
sheet = Image.new("RGB", (pad + len(MODES) * (W + pad), head + len(KINDS) * (H + pad) + pad), (246, 246, 246))
d = ImageDraw.Draw(sheet)
for col, (name, fn) in enumerate(MODES):
    x = pad + col * (W + pad)
    d.text((x, 8), name, font=LABEL, fill=(20, 20, 20))
    for row, kind in enumerate(KINDS):
        im = sample(kind)
        region = im.crop(BOX)
        im.paste(fn(region), BOX[:2])
        sheet.paste(im, (x, head + row * (H + pad)))
sheet.save(OUT)
print(OUT, sheet.size)
