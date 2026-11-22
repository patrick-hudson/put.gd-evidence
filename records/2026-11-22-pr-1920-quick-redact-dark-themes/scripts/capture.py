"""Drive the editor using the session method recipe from the PR #1631 evidence."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from PIL import Image, ImageChops, ImageDraw
from fixtures import THEMES

def cli(method, params=None):
    proc = subprocess.run(['putgd-cli', method, json.dumps(params or {})],
                          capture_output=True, text=True, timeout=100)
    try:
        answer = json.loads(proc.stdout)
    except ValueError:
        raise RuntimeError(f'{method} did not return JSON (exit {proc.returncode})') from None
    if not answer.get('ok'):
        raise RuntimeError(f'{method}: {answer.get("error", {}).get("code")}')
    return answer['result']

def retry(method, params=None, attempts=80, retry_codes=('editor_starting',)):
    for _ in range(attempts):
        try:
            return cli(method, params)
        except RuntimeError as error:
            if str(error).split(': ')[-1] not in retry_codes:
                raise
            time.sleep(.25)
    raise RuntimeError(f'{method}: still waiting after {attempts} attempts')

def open_editor(path=None):
    args = {'source': 'desktop'} if path is None else {'source': 'file', 'path': str(path)}
    opened = retry('editor.open', args, 12, ('editor_active', 'busy_selecting'))
    operation = {'id': opened['operationId']}
    try:
        retry('editor.inspect', operation)
    except Exception:
        cli('editor.cancel', operation)
        raise
    return operation

def save(op, path):
    cli('editor.saveCopy', {**op, 'path': str(path)})

def read_copy_text(op):
    cli('editor.recognize', op)
    for _ in range(200):
        result = cli('editor.inspect', op)['text']
        if result['state'] == 'completed':
            words = [w['text'] for w in result['words']]
            digest = hashlib.sha256(json.dumps(words, ensure_ascii=False).encode()).hexdigest()
            return {'wordSha256': digest, 'wordCount': len(words), 'truncated': result.get('truncated')}
        if result['state'] == 'failed':
            raise RuntimeError('Copy text recognition failed')
        time.sleep(.1)
    raise RuntimeError('Copy text recognition did not complete')

def run(out, scene, path=None):
    original = out / f'{scene}-orig.png'
    redacted = out / f'{scene}-red.png'
    op = open_editor(path)
    try:
        save(op, original)
        if path is None:
            verify_fullscreen(original, scene)
        then = time.monotonic()
        result = cli('editor.apply', {**op, 'commands': [{'op': 'redactText', 'categories': ['key']}]})
        elapsed = round(time.monotonic() - then, 3)
        inspect = cli('editor.inspect', op)
        save(op, redacted)
    finally:
        cli('editor.cancel', op)
    report = {'operationId': op['id'], 'applySeconds': elapsed, 'apply': result,
              'marks': [s['rect'] for s in inspect['shapes']]}
    if path is not None and scene.startswith('file-'):
        control = open_editor(path)
        try:
            report['copyText'] = read_copy_text(control)
        finally:
            cli('editor.cancel', control)
    write_json(out / f'{scene}-capture.json', report)
    return report

def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')

def marker_regions(im):
    points = []
    for y in range(im.height):
        for x in range(min(im.width, 600)):
            r, g, b = im.getpixel((x, y))[:3]
            if r > 185 and 55 < g < 130 and b > 115 and r-g > 90:
                points.append((x, y))
    bands = []
    for x, y in points:
        if not bands or y - bands[-1][2] > 3:
            bands.append([x, y, y, x])
        else:
            band = bands[-1]
            band[0] = min(x, band[0])
            band[2] = max(y, band[2])
            band[3] = max(x, band[3])
    if len(bands) != 2:
        raise RuntimeError(f'Expected two fixture registration marks, found {len(bands)}')
    return bands

def verify_fullscreen(original, scene):
    with Image.open(original) as source:
        im = source.convert('RGB')
    a, b = marker_regions(im)
    if abs(a[0]-b[0]) > 2 or abs(a[3]-b[3]) > 2 or b[1]-a[1] < 180:
        raise RuntimeError('Fullscreen fixture registration marks do not align')
    theme = scene.split('-')[-1]
    expected = tuple(bytes.fromhex(THEMES[theme][0]))
    bg = im.getpixel((a[3]+5, (a[1]+a[2])//2))
    if max(abs(x-y) for x,y in zip(bg, expected)) > 5:
        raise RuntimeError(f'Unexpected theme background {bg}, expected {expected}')
    right = min(im.width, a[0] + 116 * ((a[3]-a[0]+1)/6 + 1) + 30)
    left_region = (0, max(0, a[1]-20), int(right), min(im.height, b[2]+20))
    for box in ((0,0,im.width,left_region[1]), (0,left_region[3],im.width,im.height),
                (left_region[2],left_region[1],im.width,left_region[3])):
        zone = im.crop(box)
        if zone.width and zone.height:
            zone_bg = Image.new('RGB', zone.size, bg)
            if ImageChops.difference(zone, zone_bg).getbbox():
                raise RuntimeError('Unexpected pixels outside the fullscreen fixture')
    return im, bg, a, b

def desktop_boxes(original, scene, specs):
    im, bg, first, last = verify_fullscreen(original, scene)
    first_y = (first[1]+first[2])/2
    last_y = (last[1]+last[2])/2
    pitch = (last_y-first_y)/(len(specs)+1)
    if not 13 <= pitch <= 60:
        raise RuntimeError(f'Unexpected row pitch {pitch}')
    x0 = first[0]-3
    rows = {}
    pad_above = .32 if scene.startswith('terminal-') else .46
    for i, (name, length, kind) in enumerate(specs, start=1):
        if kind == 'other':
            continue
        y = first_y + i*pitch
        strip_box = (x0, max(0, int(y-pitch*pad_above)), im.width, int(y+pitch*(1-pad_above)))
        strip = im.crop(strip_box)
        diff = ImageChops.difference(strip, Image.new('RGB', strip.size, bg))
        r, g, b = diff.split()
        mask = ImageChops.lighter(ImageChops.lighter(r, g), b).point(lambda v: 255 if v >= 8 else 0)
        box = mask.getbbox()
        expected_width = (first[3]-first[0]+1)/6 * length
        if box is None or not expected_width*.85 <= box[2]-box[0] <= expected_width*1.24:
            raise RuntimeError(f'Fixture value clipped or misregistered at row {i}, found {box}, expected width near {expected_width}')
        rows[name] = {'kind': kind, 'box': [box[0]+x0, box[1]+strip_box[1],
                                            box[2]+x0, box[3]+strip_box[1]]}
    return rows

def analyze(out, scene, fixture):
    original = out / f'{scene}-orig.png'
    redacted = out / f'{scene}-red.png'
    o, r = (Image.open(p).convert('RGBA') for p in (original, redacted))
    if o.size != r.size:
        raise RuntimeError('Redacted export changed dimensions')
    meta = json.loads((out / f'{scene}-capture.json').read_text())
    mask = Image.new('1', o.size)
    ideal = o.copy()
    for x, y, w, h in meta['marks']:
        box = (x, y, x+w, y+h)
        mask.paste(1, box)
        ideal.paste((0,0,0,255), box)
    diff = ImageChops.difference(ideal, r)
    if any(channel.getbbox() for channel in diff.split()):
        raise RuntimeError('Redacted output differs from original with opaque black marks applied')
    if scene.startswith('file-'):
        filename = scene[5:]
        box = json.loads((fixture / 'file-boxes.json').read_text())[filename]
        rows = {'faint trailing comment PAT': {'kind': 'comment', 'box': box}}
    else:
        rows = desktop_boxes(original, scene, json.loads((fixture / 'rows.json').read_text()))
    for row in rows.values():
        box = row['box']
        covered = sum(n for n,v in mask.crop(box).getcolors() if v)
        pixels = (box[2]-box[0])*(box[3]-box[1])
        row.update({'opaqueBlackPixels': covered, 'pixels': pixels,
                    'coverage': 'full' if covered == pixels else 'partly' if covered else 'missed'})
    totals = {value: sum(row['coverage']==value for row in rows.values() if row['kind'] != 'decoy')
              for value in ('full', 'partly', 'missed')}
    totals['decoysCovered'] = sum(row['coverage']!='missed' for row in rows.values() if row['kind']=='decoy')
    write_json(out / f'{scene}-verify.json', {'size': o.size, 'rows': rows, 'totals': totals, **meta})
    print(scene, totals, f'{meta["applySeconds"]} s', flush=True)

if __name__ == '__main__':
    action, root, build, scene = sys.argv[1:]
    root = Path(root)
    out = root / 'results' / build
    out.mkdir(parents=True, exist_ok=True)
    fixture = root / 'fixture'
    if action == 'run':
        path = fixture / f'{scene[5:]}.png' if scene.startswith('file-') else None
        run(out, scene, path)
    analyze(out, scene, fixture)
