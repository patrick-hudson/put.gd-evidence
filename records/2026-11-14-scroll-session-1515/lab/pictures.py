#!/usr/bin/env python3
"""Side-by-side pictures of captures and the browsers' own full-page pictures (evidence)."""
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None


def side(cap, ref, out, y0, y1, scale, labels):
    a = Image.open(cap).convert("RGB")
    b = Image.open(ref).convert("RGB")
    y1 = min(y1, a.height, b.height)
    a = a.crop((0, y0, a.width, y1))
    b = b.crop((0, y0, b.width, y1))
    w, h = int(a.width * scale), int(a.height * scale)
    a = a.resize((w, h))
    b = b.resize((int(b.width * scale), h))
    o = Image.new("RGB", (w + b.width + 30, h + 40), (255, 255, 255))
    o.paste(a, (0, 40))
    o.paste(b, (w + 30, 40))
    d = ImageDraw.Draw(o)
    d.text((10, 12), labels[0], fill=(0, 0, 0))
    d.text((w + 40, 12), labels[1], fill=(0, 0, 0))
    o.save(out, optimize=True)


side("aurora/chromium-guide-auto/capture.png", "aurora/chromium-guide-auto/reference.png", "ev/guide-chrome-auto.png", 0, 3392, 0.35,
     ["put.gd, auto-scroll, Plasma 6.8.2 (end_of_content, 3,392 px)", "Chrome's own full-page picture"])
side("aurora/chromium-python-user/capture.png", "aurora/chromium-python-user/reference.png", "ev/python-chrome-you-scroll-top.png", 0, 6000, 0.3,
     ["put.gd, you scroll, Plasma 6.8.2 (first 6,000 of 60,000 px, height_cap)", "Chrome's own full-page picture"])
side("m74/firefox-wiki-auto/capture.png", "m74/firefox-wiki-auto/reference.png", "ev/wiki-firefox-auto-cinnamon-top.png", 0, 6000, 0.3,
     ["put.gd, auto-scroll, Cinnamon X11 (first 6,000 of 24,117 px, end_of_content)", "Firefox's own full-page picture"])
side("aurora/chromium-python-auto/capture.png", "aurora/chromium-python-auto/reference.png", "ev/shortfall-python-chrome-auto-black-cells.png", 17000, 18000, 0.5,
     ["put.gd, auto-scroll, Chrome on Plasma: black cells (open)", "Chrome's own full-page picture"])
side("aurora/chromium-news-user/capture.png", "aurora/chromium-news-user/reference.png", "ev/shortfall-news-chrome-you-scroll-banner-strips.png", 0, 7497, 0.2,
     ["put.gd, you scroll, Chrome on Plasma: done, 324 of 563 frames skipped, the banner in strips", "Chrome's own full-page picture"])
