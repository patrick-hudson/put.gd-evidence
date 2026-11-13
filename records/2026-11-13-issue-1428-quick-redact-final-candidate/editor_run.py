"""All pages through the real editor and putgd-ocr, offscreen, in a private
headless resident: editor.open, redactText for every category, saveCopy, and
the receipt's measure (every pixel of an item's truth box black in the export)."""
import json, os, subprocess, sys, tempfile, time
from pathlib import Path
from PIL import Image
build = Path(sys.argv[1]); out = Path(sys.argv[2]); pages = [Path(p) for p in sys.argv[3:]]
out.mkdir(parents=True, exist_ok=True)
root = Path(tempfile.mkdtemp(prefix='pgq-', dir='/tmp')); runtime = root / 'run'; runtime.mkdir(mode=0o700)
env = {k: v for k, v in os.environ.items() if k not in ('DISPLAY', 'WAYLAND_DISPLAY', 'XDG_CURRENT_DESKTOP', 'DESKTOP_SESSION')}
env |= {'QT_QPA_PLATFORM': 'offscreen', 'XDG_RUNTIME_DIR': str(runtime), 'XDG_CONFIG_HOME': str(root / 'config'), 'XDG_DATA_HOME': str(root / 'data'),
        'XDG_STATE_HOME': str(root / 'state'), 'XDG_CACHE_HOME': str(root / 'cache'), 'XDG_SESSION_TYPE': 'unspecified'}
log = open(out / 'resident.log', 'w'); resident = subprocess.Popen([str(build / 'putgd'), '--background'], env=env, stdout=log, stderr=log)
def call(method, params):
    r = subprocess.run([str(build / 'putgd-cli'), method, json.dumps(params)], env=env, capture_output=True, text=True, timeout=90)
    try: return json.loads(r.stdout)
    except Exception: return {'ok': False, 'raw': r.stdout[-300:], 'err': r.stderr[-300:]}
def overlap(a, r): return a[0] < r[2] and a[2] > r[0] and a[1] < r[3] and a[3] > r[1]
rows = []
try:
    end = time.monotonic() + 30
    while time.monotonic() < end and call('capabilities', {}).get('ok') is not True: time.sleep(0.5)
    for path in pages:
        truth = json.loads(path.with_suffix('.truth.json').read_text())['words']
        positive = [t for t in truth if t['category'] not in ('clean', 'control')]; negative = [t for t in truth if t['category'] in ('clean', 'control')]
        row = {'page': path.name}; op = None
        try:
            end = time.monotonic() + 30
            while True:
                opened = call('editor.open', {'source': 'file', 'path': str(path)})
                if opened.get('ok') or time.monotonic() > end: break
                time.sleep(0.3)  # the previous editor is still closing (editor_active)
            op = opened['result']['operationId']
            end = time.monotonic() + 30
            while time.monotonic() < end:
                v = call('editor.inspect', {'id': op})
                if v.get('ok') and v['result'].get('phase') == 'editing': break
                time.sleep(0.2)
            t0 = time.monotonic()
            applied = call('editor.apply', {'id': op, 'commands': [{'op': 'redactText', 'categories': ['email', 'phone', 'ip', 'card', 'key']}]})
            row['seconds'] = round(time.monotonic() - t0, 2)
            if not applied.get('ok'): row['error'] = applied.get('error') or applied; raise RuntimeError('apply')
            state = call('editor.inspect', {'id': op})['result']
            rects = [[s['rect'][0], s['rect'][1], s['rect'][0] + s['rect'][2], s['rect'][1] + s['rect'][3]] for s in state['shapes'] if s['kind'] == 'redact']
            export = out / path.name; export.unlink(missing_ok=True)
            saved = call('editor.saveCopy', {'id': op, 'path': str(export)})
            if not saved.get('ok'): row['error'] = saved; raise RuntimeError('save')
            flat = Image.open(export).convert('RGB')
            covered = [flat.crop(tuple(t['box'])).getextrema() == ((0, 0), (0, 0), (0, 0)) for t in positive]
            extra = sum(1 for r in rects if not any(overlap(t['box'], r) for t in positive) or any(overlap(t['box'], r) for t in negative))
            row.update(items=len(positive), covered=sum(covered), uncovered=[i for i, c in enumerate(covered) if not c], marks=len(rects), extra=extra, counts=applied['result'].get('counts'))
        except Exception as e:
            row.setdefault('error', str(e))
        finally:
            if op: call('editor.cancel', {'id': op})
        rows.append(row); print(json.dumps(row), flush=True)
finally:
    call('ui.quit', {})
    try: resident.wait(20)
    except Exception: resident.kill()
(out / 'pages.json').write_text(json.dumps(rows, indent=1))
