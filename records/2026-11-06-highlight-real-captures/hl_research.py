#!/usr/bin/env python3
"""Highlight compositing and text snapping on real desktop captures (issue #1237).

Usage: hl_research.py CROPDIR OUTDIR

Reads crop-*.png cut from put.gd-evidence captures, applies a highlight box to
each with every candidate mode, measures ink preservation / contrast / tint
visibility, and prototypes text snapping (S1) and word boxes (S2) on the
background/ink segmentation that the ink-preserving mode uses.
"""
import json
import os
import sys
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HL = np.array([250, 204, 21], dtype=np.float64)  # put.gd default highlight #FACC15
ALPHA_TODAY = 105 / 255


# ---------- color helpers (sRGB in 0..255, WCAG luminance) ----------
def srgb_to_lin(c):
    c = np.asarray(c, dtype=np.float64) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def luminance(c):
    lin = srgb_to_lin(c)
    return 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = np.maximum(la, lb), np.minimum(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def mix(a, b, t):
    return a + (b - a) * t


# ---------- simple modes ----------
def mode_today(px, **_):
    return mix(px, HL, ALPHA_TODAY)


def mode_multiply(px, **_):
    return px * HL / 255.0


def mode_darken(px, **_):
    return np.minimum(px, HL)


def mode_screen(px, color):
    return 255 - (255 - px) * (255 - color) / 255.0


def mode_ms(px, **_):
    """Cheap pair: multiply on light content, screen with a dimmed marker on dark."""
    if luminance(px).mean() > 0.35:
        return mode_multiply(px)
    return mode_screen(px, HL * 0.5)


# ---------- background / ink segmentation ----------
def quantize(px, bits=5):
    q = (px.astype(np.int64) >> (8 - bits))
    return (q[..., 0] << (2 * bits)) | (q[..., 1] << bits) | q[..., 2]


def mode_color(px, q):
    """Most common quantized color and the mean of its members."""
    flat = q.reshape(-1)
    keys, counts = np.unique(flat, return_counts=True)
    i = int(np.argmax(counts))
    members = px.reshape(-1, 3)[flat == keys[i]]
    return members.mean(axis=0), counts[i] / flat.size, keys[i]


def segment(px, block=16, confident=0.5):
    """Per-pixel background estimate and ink coverage.

    Backgrounds come from the mode of each block; blocks without a dominant
    color borrow the nearest confident block's. A pixel's coverage is its
    distance to the closest of the backgrounds of its own and neighbouring
    blocks, so a box spanning two panels keeps both backgrounds.
    Returns (coverage 0..1, bg per pixel, list of distinct bg colors,
    confident pixel fraction).
    """
    h, w, _ = px.shape
    q = quantize(px)
    nby, nbx = max(1, (h + block - 1) // block), max(1, (w + block - 1) // block)
    bg_block = np.zeros((nby, nbx, 3))
    conf = np.zeros((nby, nbx), dtype=bool)
    for by in range(nby):
        for bx in range(nbx):
            sl = (slice(by * block, min(h, (by + 1) * block)), slice(bx * block, min(w, (bx + 1) * block)))
            color, frac, _ = mode_color(px[sl], q[sl])
            bg_block[by, bx] = color
            conf[by, bx] = frac >= confident
    confident_fraction = conf.mean()
    gbg, _, _ = mode_color(px, q)
    if not conf.any():
        bg_block[:] = gbg
    else:
        ys, xs = np.nonzero(conf)
        for by in range(nby):
            for bx in range(nbx):
                if not conf[by, bx]:
                    d = np.abs(ys - by) + np.abs(xs - bx)
                    j = int(np.argmin(d))
                    bg_block[by, bx] = bg_block[ys[j], xs[j]]
    # Merge near-identical block backgrounds into a few distinct colors.
    distinct = []
    for c in bg_block.reshape(-1, 3):
        if not any(np.linalg.norm(c - d) < 12 for d in distinct):
            distinct.append(c)
    distinct = np.array(distinct)
    T = 70.0
    # Candidate backgrounds per block: own and 8 neighbours.
    cov = np.ones((h, w))
    bgpix = np.zeros((h, w, 3))
    for by in range(nby):
        for bx in range(nbx):
            cands = []
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = by + dy, bx + dx
                    if 0 <= yy < nby and 0 <= xx < nbx:
                        c = bg_block[yy, xx]
                        if not any(np.linalg.norm(c - d) < 1e-6 for d in cands):
                            cands.append(c)
            sl = (slice(by * block, min(h, (by + 1) * block)), slice(bx * block, min(w, (bx + 1) * block)))
            blk = px[sl]
            best = None
            for c in cands:
                d = np.linalg.norm(blk - c, axis=-1) / T
                if best is None:
                    best, bestc = d, np.broadcast_to(c, blk.shape).copy()
                else:
                    better = d < best
                    best = np.where(better, d, best)
                    bestc[better] = c
            cov[sl] = np.clip(best, 0, 1)
            bgpix[sl] = bestc
    return cov, bgpix, distinct, confident_fraction


def ink_colors(px, cov, bg, min_frac=0.003, dist=None):
    """Frequent colors far from the background that are glyph cores, not edges.

    Anti-aliased edges (grey ramps, LCD subpixel fringes in blue and peach)
    are frequent, far from the background and low in contrast; counting them
    as ink would cap the tint for nothing. A bin whose pixels mostly sit next
    to a pixel further from the background is an edge bin and is dropped.
    Returns (ink colors, core mask)."""
    if dist is None:
        dist = np.linalg.norm(px - bg, axis=-1)
    far = cov >= 0.95
    if not far.any():
        flat = px.reshape(-1, 3)
        i = int(np.argmax(np.linalg.norm(flat - bg, axis=-1)))
        core = np.zeros(px.shape[:2], dtype=bool); core.reshape(-1)[i] = True
        return flat[i][None, :], core
    # LCD subpixel rendering splits a stem into a bluish and a reddish column
    # with no neutral core. The eye fuses them; so does a coverage-weighted
    # mean over each pixel and its horizontal neighbours (a lone 1 px stem
    # next to background keeps its own color because the neighbours weigh 0).
    # Weights grow with the cube of the distance so a strong core pulls its
    # grey anti-aliasing neighbours toward itself and not the other way round.
    wpad = np.pad(dist ** 3, ((0, 0), (1, 1)), mode='constant')[:, :, None]
    ppad = np.pad(px, ((0, 0), (1, 1), (0, 0)), mode='edge')
    fused = (wpad[:, :-2] * ppad[:, :-2] + wpad[:, 1:-1] * ppad[:, 1:-1] + wpad[:, 2:] * ppad[:, 2:]) / np.maximum(wpad[:, :-2] + wpad[:, 1:-1] + wpad[:, 2:], 1e-6)
    q = quantize(fused, 4)
    keys, counts = np.unique(q[far], return_counts=True)
    keep = counts >= max(4, min_frac * px.shape[0] * px.shape[1])
    if not keep.any():
        keep = counts == counts.max()
    # A pixel is "edged" when a 4-neighbour is clearly further from the background.
    pad = np.pad(dist, 1, mode='edge')
    stronger = np.zeros_like(dist, dtype=bool)
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        n = pad[1 + dy:1 + dy + dist.shape[0], 1 + dx:1 + dx + dist.shape[1]]
        stronger |= n >= 1.25 * dist + 8
    inks, core = [], np.zeros(px.shape[:2], dtype=bool)
    best, best_members = None, None
    for k in keys[keep]:
        members = far & (q == k)
        # Judge the bin by its strongest pixels: fusion pulls a stem's grey
        # edges into the stem's bin, and those edges do have stronger neighbours.
        strong_members = members & (dist >= 0.8 * np.percentile(dist[members], 90))
        edge_fraction = stronger[strong_members].mean() if strong_members.any() else 1.0
        if best is None or members.sum() > best:
            best, best_members = members.sum(), members
        if edge_fraction >= 0.5:
            continue
        inks.append(fused[members].mean(axis=0)); core |= members
    if not inks:
        inks.append(fused[best_members].mean(axis=0)); core |= best_members
    return np.array(inks), core


def tint_strength(bg, inks, floor=4.5, minimum=0.28):
    """Strongest tint of HL that keeps every ink at min(original contrast, floor)."""
    worst = min(contrast(i, bg) for i in inks)
    target = min(worst, floor)
    if min(contrast(i, HL) for i in inks) >= target:
        return 1.0, target
    lo, hi = 0.0, 1.0
    for _ in range(18):
        m = (lo + hi) / 2
        if min(contrast(i, mix(bg, HL, m)) for i in inks) >= target:
            lo = m
        else:
            hi = m
    return max(lo, minimum), target


def mode_ink_global(px, **_):
    """Issue option D as prototyped: one global background."""
    q = quantize(px)
    bg, frac, key = mode_color(px, q)
    if frac < 0.35:
        return mode_multiply(px) if luminance(px).mean() > 0.35 else mode_today(px)
    d = np.linalg.norm(px - bg, axis=-1)
    cov = np.clip(d / 70.0, 0, 1)
    inks, _ = ink_colors(px, cov, bg, dist=d)
    t, _ = tint_strength(bg, inks)
    shift = mix(bg, HL, t) - bg
    return np.clip(px + (1 - cov)[..., None] * shift, 0, 255)


def mode_ink_local(px, stats=None, **_):
    """Option D with block-local backgrounds (handles two panels / zebra rows)."""
    cov, bgpix, distinct, confident_fraction = segment(px)
    if confident_fraction < 0.5:
        if stats is not None:
            stats['fallback'] = 'multiply' if luminance(px).mean() > 0.35 else 'screen'
        return mode_multiply(px) if luminance(px).mean() > 0.35 else mode_screen(px, HL * 0.5)
    out = px.copy()
    ts = []
    idx = np.argmin(np.linalg.norm(bgpix[..., None, :] - distinct[None, None, :, :], axis=-1), axis=-1)
    for k, bg in enumerate(distinct):
        mask = idx == k
        if not mask.any():
            continue
        # Ink colors from the whole box (edges need 2-D neighbours), restricted to this background's pixels.
        inks, _ = ink_colors(np.where(mask[..., None], px, bg), np.where(mask, cov, 0.0), bg)
        t, target = tint_strength(bg, inks)
        ts.append(round(float(t), 3))
        shift = mix(bg, HL, t) - bg
        out[mask] = px[mask] + (1 - cov[mask])[:, None] * shift
    if stats is not None:
        stats['tints'] = ts
        stats['backgrounds'] = [[int(round(v)) for v in c] for c in distinct]
    return np.clip(out, 0, 255)


def mode_marker(px, **_):
    """Option E: full marker on dark, light ink darkened to 4.5:1 (hue kept)."""
    cov, bgpix, distinct, confident_fraction = segment(px)
    if confident_fraction < 0.5:
        return mode_ink_local(px)
    bg = distinct[0]
    if luminance(bg) > luminance(HL) * 0.6:
        return mode_ink_local(px)
    a = cov[..., None]
    with np.errstate(divide='ignore', invalid='ignore'):
        ink = np.where(a > 0.02, bgpix + (px - bgpix) / np.maximum(a, 0.02), px)
    ink = np.clip(ink, 0, 255)
    # Darken each pixel's unmixed ink until it reads on the marker.
    f = np.ones(px.shape[:2])
    for _ in range(20):
        bad = contrast(ink * f[..., None], HL) < 4.5
        if not bad.any():
            break
        f = np.where(bad, f - 0.05, f)
    dark = ink * np.clip(f, 0, 1)[..., None]
    return np.clip(mix(np.broadcast_to(HL, px.shape), dark, a), 0, 255)


def lin_to_srgb(l):
    l = np.clip(l, 0, 1)
    return np.where(l <= 0.0031308, l * 12.92, 1.055 * l ** (1 / 2.4) - 0.055) * 255


def hue_at_luminance(color, target):
    """The highlight hue scaled in linear light to a WCAG luminance."""
    lin = srgb_to_lin(color)
    l = 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
    return lin_to_srgb(lin * (target / max(l, 1e-6)))


def tinted_background(bg, brightest=None):
    """Where a background goes under the marker, from its luminance alone.

    Light (dark ink expected): multiply, the classic marker. Dark (light ink
    expected): the highlight hue at the luminance that keeps white text at
    4.5:1 (L = 0.183), or lower when the brightest ink in the box is dimmer,
    but always at least 0.06 above the background so the box is visible.
    """
    lb = float(luminance(bg))
    if lb >= 0.3:
        return bg * HL / 255.0, 'multiply'
    cap = 0.183
    if brightest is not None:
        cap = min(cap, (brightest + 0.05) / 4.5 - 0.05)
    target = max(cap, lb + 0.06)
    return hue_at_luminance(HL, target), 'amber'


def mode_tint(px, stats=None, **_):
    """D-prime: ink-preserving tint ruled by background luminance (no ink histogram)."""
    cov, bgpix, distinct, confident_fraction = segment(px)
    if confident_fraction < 0.5:
        if stats is not None:
            stats['fallback'] = 'multiply' if luminance(px).mean() > 0.35 else 'screen'
        return mode_multiply(px) if luminance(px).mean() > 0.35 else mode_screen(px, hue_at_luminance(HL, 0.183))
    out = px.copy()
    idx = np.argmin(np.linalg.norm(bgpix[..., None, :] - distinct[None, None, :, :], axis=-1), axis=-1)
    kinds = []
    for k, bg in enumerate(distinct):
        mask = idx == k
        if not mask.any():
            continue
        far = mask & (cov >= 0.95)
        brightest = float(np.percentile(luminance(px[far]), 98)) if far.sum() >= 8 else None
        a_c, kind = tinted_background(bg, brightest)
        kinds.append(kind)
        out[mask] = px[mask] + (1 - cov[mask])[:, None] * (a_c - bg)
    if stats is not None:
        stats['kinds'] = kinds
    return np.clip(out, 0, 255)


MODES = [
    ('today', 'Today: 41% fill', mode_today),
    ('multiply', 'Multiply', mode_multiply),
    ('darken', 'Darken', mode_darken),
    ('ms', 'Multiply/Screen by luminance', mode_ms),
    ('ink-global', 'Ink-preserving, global bg', mode_ink_global),
    ('ink-local', 'Ink-preserving, local bg', mode_ink_local),
    ('tint', 'Luminance-ruled tint (D-prime)', mode_tint),
    ('marker', 'Full marker, ink darkened', mode_marker),
]


# ---------- metrics ----------
def measure(px, out, cov, bgpix):
    bg = bgpix.reshape(-1, 3).mean(axis=0)
    inks, core = ink_colors(px, cov, bg)
    bgm = cov <= 0.05
    m = {}
    if core.any():
        d = np.linalg.norm(out[core] - px[core], axis=-1)
        m['ink_shift_mean'] = round(float(d.mean()), 1)
        m['ink_shift_max'] = round(float(d.max()), 1)
    if bgm.any():
        d = np.linalg.norm(out[bgm] - px[bgm], axis=-1)
        m['bg_shift_mean'] = round(float(d.mean()), 1)
    if core.any() and bgm.any():
        bg_out = out[bgm].mean(axis=0); bg_in = px[bgm].mean(axis=0)
        q = quantize(px, 4)
        cs, c0s = [], []
        for ink in inks:
            members = core & (np.linalg.norm(px - ink, axis=-1) < 24)
            if not members.any():
                continue
            cs.append(float(contrast(out[members].mean(axis=0), bg_out)))
            c0s.append(float(contrast(px[members].mean(axis=0), bg_in)))
        if cs:
            m['contrast_min'] = round(min(cs), 2); m['contrast_orig'] = round(min(c0s), 2)
    return m


# ---------- snapping ----------
def lines_from_rows(ink_rows, min_fill, extend_fill=None):
    """Text lines from a row projection: a line starts where the fill passes
    min_fill and extends over neighbouring rows above extend_fill (descenders
    and ascenders are sparse), then gaps under a third of a line merge."""
    extend_fill = min_fill * 0.4 if extend_fill is None else extend_fill
    strong = ink_rows >= min_fill
    weak = ink_rows >= max(1, extend_fill)
    lines, start = [], None
    for y, on in enumerate(strong):
        if on and start is None:
            start = y
        if not on and start is not None:
            lines.append([start, y - 1]); start = None
    if start is not None:
        lines.append([start, len(strong) - 1])
    if not lines:
        return []
    for line in lines:
        limit = max(1, int(round(0.25 * (line[1] - line[0] + 1))))
        for _ in range(limit):
            if line[0] > 0 and weak[line[0] - 1]:
                line[0] -= 1
        for _ in range(limit):
            if line[1] + 1 < len(weak) and weak[line[1] + 1]:
                line[1] += 1
    heights = [b - a + 1 for a, b in lines]
    med = float(np.median(heights))
    merged = [lines[0]]
    for a, b in lines[1:]:
        if a <= merged[-1][1] or a - merged[-1][1] - 1 < 0.34 * med:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    return merged


def snap_box(px, box):
    """S1: snap a dragged box to the text lines it covers; returns (rect, lines)."""
    x0, y0, x1, y1 = box
    sub = px[y0:y1, x0:x1]
    cov, bgpix, distinct, frac = segment(sub)
    ink = cov >= 0.5
    rows = ink.sum(axis=1)
    lines = lines_from_rows(rows, max(2, 0.08 * rows.max()))
    if not lines:
        return box, []
    med = float(np.median([b - a + 1 for a, b in lines]))
    pad = max(2, int(round(0.2 * med)))
    top, bottom = lines[0][0], lines[-1][1]
    cols = ink[top:bottom + 1].sum(axis=0)
    xs = np.nonzero(cols >= 1)[0]
    left, right = (int(xs[0]), int(xs[-1])) if xs.size else (0, sub.shape[1] - 1)
    rect = tuple(int(v) for v in (x0 + max(0, left - pad), y0 + max(0, top - pad), x0 + min(sub.shape[1], right + 1 + pad), y0 + min(sub.shape[0], bottom + 1 + pad)))
    return rect, [(int(y0 + a), int(y0 + b)) for a, b in lines]


def components(mask):
    """4-connected components by flood fill; returns list of (x0,y0,x1,y1) boxes."""
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    boxes = []
    ys, xs = np.nonzero(mask)
    for sy, sx in zip(ys, xs):
        if seen[sy, sx]:
            continue
        stack = [(sy, sx)]; seen[sy, sx] = True
        x0 = x1 = sx; y0 = y1 = sy
        while stack:
            y, x = stack.pop()
            x0, x1, y0, y1 = min(x0, x), max(x1, x), min(y0, y), max(y1, y)
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True; stack.append((ny, nx))
        boxes.append([x0, y0, x1 + 1, y1 + 1])
    return boxes


def word_at(px, point, search=(260, 60)):
    """S2: the word box under a point: glyph components on the same line merged by gap."""
    H, W, _ = px.shape
    cx, cy = point
    x0, y0 = max(0, cx - search[0]), max(0, cy - search[1])
    x1, y1 = min(W, cx + search[0]), min(H, cy + search[1])
    sub = px[y0:y1, x0:x1]
    cov, *_ = segment(sub)
    ink = cov >= 0.5
    rows = ink.sum(axis=1)
    lines = lines_from_rows(rows, max(2, 0.08 * rows.max()))
    line = next(((a, b) for a, b in lines if a <= cy - y0 <= b), None)
    if line is None:
        return None, None
    a, b = line
    lh = b - a + 1
    band = np.zeros_like(ink); band[a:b + 1] = ink[a:b + 1]
    boxes = sorted(components(band), key=lambda r: r[0])
    # Merge glyphs closer than 0.22 x line height into words (a space is wider).
    words = []
    for bx in boxes:
        if words and bx[0] - words[-1][2] < 0.22 * lh:
            words[-1][2] = max(words[-1][2], bx[2]); words[-1][1] = min(words[-1][1], bx[1]); words[-1][3] = max(words[-1][3], bx[3])
        else:
            words.append(list(bx))
    px_x = cx - x0
    hit = next((w for w in words if w[0] - 0.3 * lh <= px_x <= w[2] + 0.3 * lh), None)
    pad = max(2, int(round(0.2 * lh)))
    line_rect = (x0 + min(w[0] for w in words) - pad, y0 + a - pad, x0 + max(w[2] for w in words) + pad, y0 + b + 1 + pad)
    if hit is None:
        return None, tuple(int(v) for v in line_rect)
    return tuple(int(v) for v in (x0 + hit[0] - pad, y0 + a - pad, x0 + hit[2] + pad, y0 + b + 1 + pad)), tuple(int(v) for v in line_rect)


# ---------- driver ----------
CASES = {
    # crop name: (box inside the crop, note)
    'dark-table': ((40, 50, 520, 110), 'box across two zebra rows + icons'),
    'dark-settings-top': ((15, 45, 320, 65), 'muted grey text on dark'),
    'light-paragraph': ((10, 15, 520, 36), 'dark text on light grey'),
    'light-heading': ((20, 20, 500, 40), 'text on white'),
    'light-popup': ((10, 30, 240, 52), 'small text on white popup'),
    'light-menu': ((10, 80, 200, 112), 'menu items on white'),
    'dark-notify': ((12, 25, 262, 60), 'light text on dark brown notice'),
    'kde-notify': ((10, 45, 260, 85), 'white text on navy'),
    'photo': ((40, 100, 400, 200), 'painting: no dominant background'),
    'kde-wallpaper-text': ((150, 0, 400, 40), 'low-contrast wallpaper text'),
    'accent': ((135, 20, 470, 50), 'white text on red accent (photo crop top)'),
    'syn-syntax': ((14, 12, 386, 52), 'issue sample: dark-theme syntax colors (grayscale AA)'),
    'syn-button': ((14, 12, 386, 52), 'issue sample: white on accent button'),
}

SNAP_CASES = {
    'light-paragraph-3lines': ('light-paragraph', (30, 2, 500, 60)),
    'dark-table-rows': ('dark-table', (30, 15, 500, 230)),
    'light-menu-items': ('light-menu', (5, 70, 190, 300)),
}
WORD_CASES = {
    'light-paragraph-word': ('light-paragraph', (120, 25)),
    'dark-table-word': ('dark-table', (300, 95)),
    'light-menu-word': ('light-menu', (60, 96)),
}


def synthetic(kind):
    """The issue prototype's samples (Pillow grayscale AA, no subpixel fringes)."""
    W, H = 400, 64
    def tt(name, size):
        for d in ('/usr/share/fonts/dejavu-sans-fonts/', '/usr/share/fonts/truetype/dejavu/', '/usr/share/fonts/dejavu-sans-mono-fonts/'):
            if os.path.exists(d + name):
                return ImageFont.truetype(d + name, size)
        return ImageFont.load_default()
    if kind == 'syn-syntax':
        im = Image.new('RGB', (W, H), (30, 30, 30)); d = ImageDraw.Draw(im); mono = tt('DejaVuSansMono.ttf', 21); x = 20
        for text, color in (('const ', (86, 156, 214)), ('url', (156, 220, 254)), (' = ', (212, 212, 212)), ('"put.gd/x"', (206, 145, 120)), (';', (212, 212, 212)), (' // ok', (106, 153, 85))):
            d.text((x, 19), text, font=mono, fill=color); x += d.textlength(text, font=mono)
    else:
        im = Image.new('RGB', (W, H), (37, 99, 235)); d = ImageDraw.Draw(im)
        d.text((20, 18), 'Upload and copy link', font=tt('DejaVuSans.ttf', 22), fill=(255, 255, 255))
    return np.asarray(im, dtype=np.float64)


def load(crop_dir, name):
    if name.startswith('syn-'):
        return synthetic(name)
    return np.asarray(Image.open(os.path.join(crop_dir, f'crop-{name}.png')).convert('RGB'), dtype=np.float64)


def font(size):
    for p in ('/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def main():
    crop_dir, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    results = {}
    zoom = 2
    label = font(14)
    for name, (box, note) in CASES.items():
        src = 'photo' if name == 'accent' else name
        px = load(crop_dir, src)
        x0, y0, x1, y1 = box
        region = px[y0:y1, x0:x1]
        cov, bgpix, distinct, frac = segment(region)
        case = {'note': note, 'box': box, 'confident_fraction': round(float(frac), 2), 'modes': {}}
        tiles = []
        for key, title, fn in MODES:
            stats = {}
            t0 = time.perf_counter()
            out = fn(region, stats=stats) if key in ('ink-local', 'tint') else fn(region)
            ms = (time.perf_counter() - t0) * 1000
            m = measure(region, out, cov, bgpix)
            m['numpy_ms'] = round(ms, 1)
            m.update(stats)
            case['modes'][key] = m
            full = px.copy(); full[y0:y1, x0:x1] = out
            im = Image.fromarray(full.astype(np.uint8))
            im = im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)
            canvas = Image.new('RGB', (im.width, im.height + 22), (240, 240, 240))
            canvas.paste(im, (0, 22))
            ImageDraw.Draw(canvas).text((4, 3), f'{title}  ink shift {m.get("ink_shift_mean", "-")} / contrast {m.get("contrast_min", "-")}', font=label, fill=(0, 0, 0))
            tiles.append(canvas)
        results[name] = case
        W = max(t.width for t in tiles); Hh = sum(t.height + 6 for t in tiles)
        sheet = Image.new('RGB', (W, Hh), (255, 255, 255)); y = 0
        for t in tiles:
            sheet.paste(t, (0, y)); y += t.height + 6
        sheet.save(os.path.join(out_dir, f'modes-{name}.png'))
        print(name, json.dumps(case['modes'], indent=None)[:400], flush=True)

    # Snapping demos.
    snap = {}
    for name, (crop, box) in SNAP_CASES.items():
        px = load(crop_dir, crop)
        t0 = time.perf_counter()
        rect, lines = snap_box(px, box)
        ms = (time.perf_counter() - t0) * 1000
        snap[name] = {'dragged': box, 'snapped': rect, 'lines': lines, 'numpy_ms': round(ms, 1)}
        im = Image.fromarray(px.astype(np.uint8)).convert('RGB')
        d = ImageDraw.Draw(im)
        d.rectangle([box[0], box[1], box[2] - 1, box[3] - 1], outline=(255, 0, 255), width=1)
        d.rectangle([rect[0], rect[1], rect[2] - 1, rect[3] - 1], outline=(0, 200, 255), width=2)
        for a, b in lines:
            d.line([(box[0], a), (box[0] - 6, a)], fill=(0, 255, 0)); d.line([(box[0], b), (box[0] - 6, b)], fill=(255, 0, 0))
        im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
        im.save(os.path.join(out_dir, f'snap-{name}.png'))
        print(name, snap[name], flush=True)
    words = {}
    for name, (crop, point) in WORD_CASES.items():
        px = load(crop_dir, crop)
        t0 = time.perf_counter()
        w, l = word_at(px, point)
        ms = (time.perf_counter() - t0) * 1000
        words[name] = {'point': point, 'word': w, 'line': l, 'numpy_ms': round(ms, 1)}
        im = Image.fromarray(px.astype(np.uint8)).convert('RGB')
        d = ImageDraw.Draw(im)
        if l: d.rectangle([l[0], l[1], l[2] - 1, l[3] - 1], outline=(0, 200, 255), width=1)
        if w: d.rectangle([w[0], w[1], w[2] - 1, w[3] - 1], outline=(255, 0, 255), width=2)
        d.ellipse([point[0] - 3, point[1] - 3, point[0] + 3, point[1] + 3], outline=(0, 255, 0), width=2)
        im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
        im.save(os.path.join(out_dir, f'word-{name}.png'))
        print(name, words[name], flush=True)
    with open(os.path.join(out_dir, 'results.json'), 'w') as f:
        json.dump({'modes': results, 'snap': snap, 'words': words}, f, indent=1)


if __name__ == '__main__':
    main()
