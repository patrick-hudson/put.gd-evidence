#!/usr/bin/env python3
"""w3drive.py RUN OUTDIR CASE... : issue 1487 cases on a two-head Omarchy guest (run on f44).

Cases: start (resident with PUTGD_REGION_DEBUG_LOG, settings), ordinary, reload-ordinary,
reload-qmp (drag through the QEMU tablet), early-driver, early-human, early-escape, log (fetch logs).
Each case appends one JSON line to OUTDIR/rows.jsonl and saves both heads' frames.
"""
import json, os, subprocess, sys, time
ROOT = os.path.expanduser('~/work/w3-1487'); sys.path.insert(0, os.path.join(ROOT, 'tools/lab'))
import lab  # noqa: E402
from PIL import Image  # noqa: E402
RUN, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]); os.makedirs(OUT, exist_ok=True)
ENV = '. /tmp/env.sh; '
def g(cmd, timeout=60): return lab.guest_session(RUN, cmd + '\n', timeout=timeout)
def cli(method, params=None):
    r = lab.cli(RUN, method, params)
    with open(os.path.join(OUT, 'session.jsonl'), 'a') as f: f.write(json.dumps({'t': time.time(), 'method': method, 'params': params, 'reply': r})[:4000] + '\n')
    return r
def frames(name):
    for head in (0, 1):
        lab.screenshot(RUN, 'witness', head); Image.open(os.path.join(RUN, 'witness-head%d.ppm' % head)).save(os.path.join(OUT, '%s-head%d.png' % (name, head)))
def row(name, ok, detail):
    line = {'case': name, 'passed': bool(ok), 'time': time.strftime('%H:%M:%S'), **detail}
    with open(os.path.join(OUT, 'rows.jsonl'), 'a') as f: f.write(json.dumps(line) + '\n')
    print(('ok   ' if ok else 'FAIL ') + json.dumps(line)[:900], flush=True)
def recent(): return {v['id'] for v in cli('operation.recent')['operations']}
def settle(old, limit=25):
    end = time.time() + limit
    while time.time() < end:
        new = [v for v in cli('operation.recent')['operations'] if v['id'] not in old]
        if new and new[0]['state'] in ('completed', 'cancelled', 'failed'): return new[0]
        time.sleep(0.2)
    new = [v for v in cli('operation.recent')['operations'] if v['id'] not in old]
    return new[0] if new else None
def monitors(): return json.loads(g(ENV + 'hyprctl monitors -j') or '[]')
def mon_brief(): return [(m['name'], m['x'], m['y'], m['width'], m['height'], m.get('scale')) for m in monitors()]
def layers(): return g(ENV + 'hyprctl layers')
def wait_selector(limit=6):
    end = time.time() + limit
    while time.time() < end:
        if 'putgd-region-selector' in layers(): return True
        time.sleep(0.1)
    return False
def vdrag(x1, y1, x2, y2, extra=''):
    return g(ENV + 'python3 /tmp/wayland_pointer.py drag %d %d %d %d --extent 2304 800 %s' % (x1, y1, x2, y2, extra))
from PIL import ImageChops, ImageStat
def fetch(op, name):
    path = op['items'][0]['local']['path']; local = os.path.join(OUT, name + '-capture.png'); lab.get(RUN, path, local)
    return Image.open(local).convert('RGB')
def result(name, op, extra, rect=(300, 300, 600, 500)):
    ok = bool(op) and op['state'] == 'completed'
    detail = {'state': op and op['state'], 'error': op and op.get('error'), 'expectRect': rect, **extra}
    frames(name)
    if ok:
        try:
            image = fetch(op, name); detail['size'] = list(image.size)
            head = 0 if rect[0] < 1280 else 1; ox = 0 if head == 0 else 1280
            frame = Image.open(os.path.join(OUT, '%s-head%d.png' % (name, head))).convert('RGB').crop((rect[0] - ox, rect[1], rect[2] - ox, rect[3]))
            detail['meanDiffVsFrame'] = round(sum(ImageStat.Stat(ImageChops.difference(image, frame)).mean) / 3, 3) if frame.size == image.size else None
        except Exception as e: detail['fetchError'] = repr(e)[:200]
    want = [rect[2] - rect[0], rect[3] - rect[1]]
    row(name, ok and detail.get('size') == want and detail.get('meanDiffVsFrame') is not None and detail['meanDiffVsFrame'] < 10, detail)
def ordinary(name, reload=False, qmp=False, roundb=False):
    before = mon_brief()
    if reload: g(ENV + 'hyprctl reload'); time.sleep(0.8 if roundb else 1.0)
    after = mon_brief(); old = recent()
    if roundb: g(ENV + 'python3 /tmp/wayland_pointer.py move 300 300 --extent 2304 800')
    lab.key(RUN, ['ctrl', 'shift', 'f9']); mapped = wait_selector(); time.sleep(0.3)
    lay = layers()
    if roundb: out = vdrag(300, 300, 600, 500, '--steps 8')
    elif qmp: out = subprocess.run([sys.executable, os.path.join(ROOT, 'qmp_early.py'), RUN, '0', '16', '12', '300', '300', '600', '500', '--no-key'], capture_output=True, text=True).stdout.strip()
    else: out = vdrag(300, 300, 600, 500)
    op = settle(old); result(name, op, {'reload': reload, 'qmp': qmp, 'monitorsBefore': before, 'monitorsAfter': after, 'selectorMapped': mapped, 'driver': out[-300:], 'layers': lay[-1500:]})
def early(name, kind, rect=(300, 300, 600, 500)):
    old = recent()
    if kind == 'driver':
        g(ENV + 'python3 /tmp/wayland_pointer.py move %d %d --extent 2304 800' % rect[:2]); lab.key(RUN, ['ctrl', 'shift', 'f9'])
        out = vdrag(*rect, extra='--settle-ms 0 --step-ms 10')
    elif kind == 'escape':
        lab.key(RUN, ['ctrl', 'shift', 'f9']); lab.key(RUN, ['esc']); out = ''
    else:
        delay, step = kind.split(':')[1:3]
        out = subprocess.run([sys.executable, os.path.join(ROOT, 'qmp_early.py'), RUN, delay, step, '12'] + [str(v) for v in rect], capture_output=True, text=True)
        out = (out.stdout + out.stderr).strip()
    op = settle(old, limit=5); second = False
    if kind != 'escape' and op and op['state'] not in ('completed', 'cancelled', 'failed'):
        # The early press was not taken: the selector must be open for an ordinary drag.
        second = wait_selector(); vdrag(*rect); op = settle(old)
    if kind == 'escape':
        row(name, bool(op) and op['state'] == 'cancelled', {'state': op and op['state'], 'error': op and op.get('error')}); frames(name); return
    result(name, op, {'kind': kind, 'driver': out[-300:], 'secondDrag': second, 'monitors': mon_brief()}, rect)
for case in sys.argv[3:]:
    try:
        if case == 'start':
            g("python3 - <<'PYENV'\nimport os,shlex\nopen('/tmp/env.sh','w').write('\\n'.join('export '+k+'='+shlex.quote(v) for k,v in os.environ.items())+'\\n')\nPYENV")
            for f in ('wayland_pointer.py', 'wayland_toplevels.py'): lab.put(RUN, os.path.join(ROOT, 'tools/lab', f), '/tmp/' + f)
            g('mkdir -p ~/putgd-lab\nexport PUTGD_REGION_DEBUG_LOG=$HOME/putgd-lab/region.log\nnohup putgd-launcher --background > ~/putgd-lab/app.log 2>&1 < /dev/null &')
            for _ in range(60):
                try: caps = cli('capabilities'); break
                except Exception: time.sleep(1)
            resident = lab.verify_running_app(RUN)
            diag = cli('diagnostics'); doc = cli('settings.get')
            cli('settings.patch', {'patch': {'archive': {'keepUploads': True}, 'preferences': {'notifications': False, 'regionSelectionMode': 'live'},
                'actions': {'region': {'destination': 'local', 'profileId': None, 'shortcut': 'Ctrl+Shift+F9'}}}, 'expectedRevision': doc['metadata']['observedRevision']})
            time.sleep(3)
            row('start', True, {'build': diag.get('build'), 'resident': resident, 'shortcuts': cli('capabilities').get('shortcuts'), 'monitors': mon_brief()})
        elif case == 'ordinary': ordinary('ordinary')
        elif case.startswith('reload-ordinary'): ordinary(case, reload=True)
        elif case.startswith('roundb-reload'): ordinary(case, reload=True, roundb=True)
        elif case.startswith('roundb-noreload'): ordinary(case, roundb=True)
        elif case.startswith('reload-qmp'): ordinary(case, reload=True, qmp=True)
        elif case.startswith('noreload-qmp'): ordinary(case, qmp=True)
        elif case.startswith('early-driver@'): early(case.split('@')[0] + '-' + case.split('@')[1].replace(',', '_'), 'driver', tuple(int(v) for v in case.split('@')[1].split(',')))
        elif case.startswith('early-driver'): early(case, 'driver')
        elif case.startswith('screenshot-first'):
            doc = cli('settings.get'); cli('settings.patch', {'patch': {'preferences': {'regionSelectionMode': 'screenshot_first'}}, 'expectedRevision': doc['metadata']['observedRevision']}); time.sleep(1)
            try: ordinary(case)
            finally:
                doc = cli('settings.get'); cli('settings.patch', {'patch': {'preferences': {'regionSelectionMode': 'live'}}, 'expectedRevision': doc['metadata']['observedRevision']}); time.sleep(1)
        elif case.startswith('early-escape'): early(case, 'escape')
        elif case.startswith('early-qmp'):
            # early-qmp-NAME@DELAY:STEP[@X1,Y1,X2,Y2]
            parts = case.split('@'); rect = tuple(int(v) for v in parts[2].split(',')) if len(parts) > 2 else (300, 300, 600, 500)
            early(parts[0], 'qmp:' + parts[1], rect)
        elif case == 'log':
            for remote, local in (('putgd-lab/region.log', 'region.log'), ('putgd-lab/app.log', 'app.log')):
                try: lab.get(RUN, '/home/lab/' + remote, os.path.join(OUT, local))
                except Exception as e: print('log', remote, e)
        else: print('unknown case', case)
    except Exception as e:
        row(case, False, {'driverError': repr(e)[:500]})
