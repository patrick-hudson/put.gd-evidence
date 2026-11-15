#!/usr/bin/env python3
"""Scores the session's real-page runs (sess.py) against the browsers' own
pictures with the tracker scorer's band comparison (tools/lab/scroll_tracker_score.py):
the share of 64-row bands equal outside what the page pins, and the scrollbar.

  score.py RUNS_DIR [--json FILE]
"""
import json, sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import scroll_tracker_score as S  # noqa: E402


def blur(gray):
    import numpy as np
    g = gray.astype(np.float32)
    for _ in range(2):
        g = (np.roll(g, 1, 0) + g + np.roll(g, -1, 0)) / 3
        g = (np.roll(g, 1, 1) + g + np.roll(g, -1, 1)) / 3
    return g


def tolerant(ref, image):
    """Bands equal to the browser's picture once both are grey and slightly
    blurred, at the horizontal shift that fits best: the screen draws text with
    subpixel antialiasing and the browser's screenshot with grey, and a page
    laid out at 1,920 px for the screenshot is centred 7.5 px off a 1,905 px
    viewport. A band is equal when at most 1% of its compared pixels differ by
    more than 16 grey levels; the pinned rectangles and the scrollbar are left
    out as in the strict comparison."""
    import numpy as np
    h = min(image.shape[0], ref.pixels.shape[0])
    width = min(image.shape[1], ref.pixels.shape[1]) - S.SCROLLBAR - 24
    a = blur(image[:h, :, :].mean(axis=2))
    b = blur(ref.pixels[:h, :, :].mean(axis=2))
    mid = slice(int(h * 0.1), max(int(h * 0.1) + 64, min(h, int(h * 0.1) + 2000)))
    best = min(range(-12, 13), key=lambda dx: float(np.abs(a[mid, 24:width] - b[mid, 24 + dx:width + dx]).mean()))
    equal = total = 0
    for _, lo, hi in ref.bands(0, h):
        mask = np.ones((hi - lo, width - 24), dtype=bool)
        for rx0, ry0, rx1, ry1 in ref.rects:
            y0, y1 = max(lo, ry0), min(hi, ry1)
            if y0 < y1:
                mask[y0 - lo:y1 - lo, max(0, rx0 - 24):max(0, min(width, rx1) - 24)] = False
        if mask.sum() < width:
            continue
        bad = (np.abs(a[lo:hi, 24:width] - b[lo:hi, 24 + best:width + best]) > 16) & mask
        total += 1
        equal += bad.sum() <= 0.01 * mask.sum()
    return [int(equal), int(total)]


def one(run):
    r = json.loads((run / 'result.json').read_text())
    c = r.get('capture') or {}
    row = {'name': run.name, 'browser': r['browser'], 'site': r['site'], 'mode': r['mode'], 'end': c.get('endReason') or ('failed' if r.get('failed') else 'none'),
           'height': c.get('height'), 'page': r['after']['docHeight'], 'placed': c.get('framesPlaced'), 'skipped': c.get('framesSkipped'),
           'by': c.get('scrolledBy'), 'seconds': r['seconds'], 'fps': (c.get('stats') or {}).get('framesPerSecond'), 'note': c.get('note')}
    if r.get('failed'):
        row['failed'] = r['failed'].get('error')
    if (run / 'capture.png').exists() and (run / 'reference.png').exists():
        view_h = r['rect'][3]
        ref = S.Reference(run, view_h)
        image = S.load_rgb(run / 'capture.png')
        ref.align(image[:view_h], 0)
        equal, total, _, _, worst = ref.score(run / 'capture.png', 0)
        row.update(bands=[equal, total], worst=worst[:6], tolerant=tolerant(ref, image))
    return row


def main():
    runs = Path(sys.argv[1])
    rows = [one(run) for run in sorted(runs.iterdir()) if (run / 'result.json').exists() and '-incomplete-' not in run.name]
    for row in rows:
        b = row.get('bands')
        t = row.get('tolerant')
        print('%-34s %-15s %6s/%-6s placed %4s skipped %4s by %-6s %6.1fs %5s fps bands %9s tolerant %9s' % (
            row['name'], row['end'], row['height'], row['page'], row['placed'], row['skipped'], row['by'], row['seconds'], row['fps'],
            '%d/%d' % tuple(b) if b else '-', '%d/%d' % tuple(t) if t else '-'))
    if '--json' in sys.argv:
        Path(sys.argv[sys.argv.index('--json') + 1]).write_text(json.dumps(rows, indent=1))


if __name__ == '__main__':
    main()
