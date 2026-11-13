"""Score Quick redact matches against ground truth with the receipt's measure:
an item is covered only when every pixel of its truth box lies under a mark."""
import json, sys
from pathlib import Path
pages_dir = Path(sys.argv[1]); result = json.loads(Path(sys.argv[2]).read_text()); verbose = len(sys.argv) > 3
def covered(box, marks):
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        x = x0
        while x < x1:
            hit = next((m for m in marks if m[0] <= x < m[0]+m[2] and m[1] <= y < m[1]+m[3]), None)
            if not hit: return False
            x = hit[0]+hit[2]
    return True
def overlap(a, r): return a[0] < r[0]+r[2] and a[2] > r[0] and a[1] < r[1]+r[3] and a[3] > r[1]
rows = []
for name in sorted(result):
    page = result[name]; truth = json.loads((pages_dir / name.replace('.png', '.truth.json')).read_text())['words']
    marks = [m for match in page['matches'] for m in match['marks']]
    positive = [t for t in truth if t['category'] not in ('clean', 'control')]
    negative = [t for t in truth if t['category'] in ('clean', 'control')]
    status = [covered(t['box'], marks) for t in positive]
    extra = sum(1 for m in marks if not any(overlap(t['box'], m) for t in positive) or any(overlap(t['box'], m) for t in negative))
    rows.append((name, sum(status), len(positive), [i for i, s in enumerate(status) if not s], len(marks), extra))
    if verbose:
        cand = page['candidates']
        for i, t in enumerate(positive):
            if status[i]: continue
            text = ''.join(map(chr, t['text_codepoints']))
            near = [(k, c['text'], c['rect'], c['confidence']) for k, c in enumerate(cand) if overlap(t['box'], c['rect'])]
            by = [(m['category'], [cand[w]['text'] for w in m['words']], m['marks']) for m in page['matches'] if any(overlap(t['box'], r) for r in m['marks'])]
            print(f'{name} item {i} {t["category"]} truth={text!r} box={t["box"]}')
            print(f'   candidates: {[(n[1], n[3]) for n in near]}')
            print(f'   cand rects: {[n[2] for n in near]}')
            print(f'   matched:    {by}')
for r in rows: print(f'{r[0]:45s} {r[1]:2d}/{r[2]:2d} miss={r[3]} marks={r[4]} extra={r[5]}')
