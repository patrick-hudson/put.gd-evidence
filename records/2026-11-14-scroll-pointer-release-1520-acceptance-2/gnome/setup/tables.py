#!/usr/bin/env python3
"""tables.py DIR: Markdown tables of the try logs in DIR/tries/*.jsonl."""
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1]) / 'tries'
sets = [
    ('k72', 'Plasma 6.6.6 Wayland', [('nightly-k72-vnc', 'v26.1113.4757-nightly', 'VNC'), ('nightly-k72-rel', 'v26.1113.4757-nightly', 'uinput'),
                                     ('dev-k72-jitter', 'first commit 552cc0d, no watch', 'uinput, random start'), ('dev2-k72-vnc', 'this PR', 'VNC'), ('dev2-k72-rel', 'this PR', 'uinput'), ('dev2-k72-jitter', 'this PR', 'uinput, random start')]),
    ('m74', 'Cinnamon X11', [('nightly-m74-vnc', 'v26.1113.4757-nightly', 'VNC'), ('nightly-m74-rel', 'v26.1113.4757-nightly', 'uinput'),
                             ('dev-m74-vnc', 'this PR', 'VNC'), ('dev-m74-rel', 'this PR', 'uinput'), ('dev-m74-jitter', 'this PR', 'uinput, random start')]),
]
out = []
for host, desktop, runs in sets:
    out.append(f'### {host} ({desktop})\n')
    out.append('| Build | Input | First click stopped it | Paused after the first motion (ms) | put.gd pointer moves after the first motion |')
    out.append('| --- | --- | --- | --- | --- |')
    for name, build, inp in runs:
        path = root / f'{name}.jsonl'
        if not path.exists():
            continue
        rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
        stopped = sum(1 for r in rows if r.get('stoppedByClick'))
        paused = [max(0.0, r['pausedMs']) for r in rows if r.get('pausedMs') is not None]
        moves = [r.get('movesAfter', 0) for r in rows]
        p = f'{min(paused):.0f} to {max(paused):.0f} (median {sorted(paused)[len(paused) // 2]:.0f})' if paused else 'never'
        m = ', '.join(str(v) for v in moves)
        out.append(f'| {build} | {inp} | {stopped} of {len(rows)} | {p} | {m} |')
    out.append('')
print('\n'.join(out))
