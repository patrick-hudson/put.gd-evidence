"""Pixel check of an uploaded image against the capture's original and the fixture truth.

check.py TRUTH FIXTURE_ID ORIGINAL UPLOAD --cover card,key,... [--offset X Y] [--fixture-png PATH] [--json OUT]

- D = pixels where UPLOAD differs from ORIGINAL (RGBA).
- Every changed pixel must be opaque black.
- Each token of a kind in --cover: its glyph box must be entirely opaque black in UPLOAD.
- Every other token (near misses and kinds not covered): no pixel of its glyph box changed.
- Changed pixels outside the allowed area (the covered tokens' whole words, padded the way
  Quick redact pads a mark: up to 2 character widths sideways and 45% of the line height
  vertically) are reported as over-covering.
- ORIGINAL is compared with the fixture to prove the capture showed it 1:1.
"""
import argparse
import json
import sys

import numpy as np
from PIL import Image
from scipy import ndimage


def load(path):
    return np.asarray(Image.open(path).convert('RGBA')).astype(np.int16)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('truth')
    ap.add_argument('fixture')
    ap.add_argument('original')
    ap.add_argument('upload')
    ap.add_argument('--cover', default='')
    ap.add_argument('--offset', type=int, nargs=2, default=[0, 0])
    ap.add_argument('--fixture-png')
    ap.add_argument('--json')
    a = ap.parse_args()
    truth = json.load(open(a.truth))
    fx = next(f for f in truth['fixtures'] if f['id'] == a.fixture)
    cover = set(filter(None, a.cover.split(',')))
    O, U = load(a.original), load(a.upload)
    res = {'fixture': a.fixture, 'cover': sorted(cover), 'size': [O.shape[1], O.shape[0]]}
    if O.shape != U.shape:
        res['error'] = f'size differs: original {O.shape} upload {U.shape}'
        print(json.dumps(res))
        return
    H, W = O.shape[:2]
    ox, oy = a.offset
    if a.fixture_png:
        F = load(a.fixture_png)
        crop = F[oy:oy + H, ox:ox + W]
        if crop.shape == O.shape:
            bad = np.any(np.abs(crop[..., :3] - O[..., :3]) > 2, axis=2)
            res['originalVsFixture'] = {'differingPixels': int(bad.sum())}
            if bad.any():
                ys, xs = np.nonzero(bad)
                res['originalVsFixture']['box'] = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
    D = np.any(U != O, axis=2)
    black = (U[..., 0] == 0) & (U[..., 1] == 0) & (U[..., 2] == 0) & (U[..., 3] == 255)
    res['changedPixels'] = int(D.sum())
    res['changedNotBlack'] = int((D & ~black).sum())
    labels, n = ndimage.label(D)
    rects = []
    for sl in ndimage.find_objects(labels):
        rects.append([int(sl[1].start), int(sl[0].start), int(sl[1].stop), int(sl[0].stop)])
    res['coverRects'] = rects
    allowed = np.zeros((H, W), bool)
    tokens = []
    for t in fx['tokens']:
        x0, y0, x1, y1 = t['bbox']
        x0, x1, y0, y1 = x0 - ox, x1 - ox, y0 - oy, y1 - oy
        cx0, cy0, cx1, cy1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
        entry = {'kind': t['kind'], 'text': t['text'] if t['kind'] in ('miss', 'name', 'list') or len(t['text']) < 26 else t['text'][:12] + '…',
                 'bbox': [x0, y0, x1, y1]}
        if cx1 <= cx0 or cy1 <= cy0:
            entry['outside'] = True
            tokens.append(entry)
            continue
        if cx0 != x0 or cy0 != y0 or cx1 != x1 or cy1 != y1:
            entry['clipped'] = True
        box = (slice(cy0, cy1), slice(cx0, cx1))
        area = (cy1 - cy0) * (cx1 - cx0)
        entry['blackFraction'] = round(float(black[box].sum()) / area, 4)
        entry['changedFraction'] = round(float(D[box].sum()) / area, 4)
        if t['kind'] in cover:
            entry['expect'] = 'covered'
            entry['pass'] = entry['blackFraction'] >= 0.999
            wx0, wy0, wx1, wy1 = t['wordbox']
            px, py = int(2 * t['charw']) + 2, int(0.45 * t['lineh']) + 2
            allowed[max(0, wy0 - oy - py):min(H, wy1 - oy + py), max(0, wx0 - ox - px):min(W, wx1 - ox + px)] = True
        else:
            entry['expect'] = 'untouched'
            entry['pass'] = entry['changedFraction'] == 0
        tokens.append(entry)
    res['tokens'] = tokens
    extra = D & ~allowed
    res['overCoverPixels'] = int(extra.sum())
    if extra.any():
        el, _ = ndimage.label(extra)
        res['overCoverRects'] = [[int(s[1].start), int(s[0].start), int(s[1].stop), int(s[0].stop)] for s in ndimage.find_objects(el)]
        # Slivers at most 4 px thin beside a mark are its padding, not covering other content.
        res['paddingSlivers'] = [r for r in res['overCoverRects'] if min(r[2] - r[0], r[3] - r[1]) <= 4]
        res['overCoverRects'] = [r for r in res['overCoverRects'] if r not in res['paddingSlivers']]
        res['overCoverPixels'] = int(sum(extra[r[1]:r[3], r[0]:r[2]].sum() for r in res['overCoverRects']))
    expected = [t for t in tokens if t.get('expect') == 'covered']
    res['summary'] = {
        'expectedCovered': len(expected), 'covered': sum(t['pass'] for t in expected),
        'missed': [t for t in expected if not t['pass']],
        'untouchedExpected': sum(1 for t in tokens if t.get('expect') == 'untouched'),
        'wronglyChanged': [t for t in tokens if t.get('expect') == 'untouched' and not t['pass']],
        'notBlack': res['changedNotBlack'], 'overCoverPixels': res['overCoverPixels'],
    }
    res['pass'] = not res['summary']['missed'] and not res['summary']['wronglyChanged'] and not res['changedNotBlack'] and not res['overCoverPixels']
    out = json.dumps(res, indent=1)
    if a.json:
        open(a.json, 'w').write(out)
    s = res['summary']
    print(json.dumps({'fixture': a.fixture, 'pass': res['pass'], 'covered': f"{s['covered']}/{s['expectedCovered']}",
                      'missed': [(t['kind'], t['text']) for t in s['missed']], 'wronglyChanged': [(t['kind'], t['text']) for t in s['wronglyChanged']],
                      'notBlack': s['notBlack'], 'overCover': s['overCoverPixels'], 'overCoverRects': res.get('overCoverRects', []), 'rects': len(rects),
                      'origVsFixture': res.get('originalVsFixture')}))


if __name__ == '__main__':
    main()
