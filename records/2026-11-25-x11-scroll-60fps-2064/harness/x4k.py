#!/usr/bin/env python3
"""x4k.py TAG DRIVER HELPER FIXTURE W H [CPUS]: auto-scroll on the ruler fixture
on a private Xvfb of WxH, helper and Xvfb CPU and helper memory metered."""
import json, os, subprocess, sys, time, importlib.util
from pathlib import Path
tag, driver, helper, fixture, W, H = sys.argv[1:7]
cpus = sys.argv[7] if len(sys.argv) > 7 else None
W, H = int(W), int(H)
os.environ.setdefault('LAB_DRIVER', driver); os.environ.setdefault('LAB_HELPER', helper)
spec = importlib.util.spec_from_file_location('r', str(Path.home() / 'work/x2064/lab/run.py'))
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
out = Path.home() / 'work/x2064/x4k' / tag
out.mkdir(parents=True)
disp = ':77'
pre = ['taskset', '-c', cpus] if cpus else []
xv = subprocess.Popen(['Xvfb', disp, '-screen', '0', '%dx%dx24' % (W, H), '-noreset', '-nolisten', 'tcp'], stderr=open(out / 'xvfb.err', 'w'))
time.sleep(2)
env = {k: v for k, v in os.environ.items() if k not in ('WAYLAND_DISPLAY',)}
env.update(DISPLAY=disp, XDG_SESSION_TYPE='x11', QT_QPA_PLATFORM='xcb', PUTGD_RECORD_DEBUG_LOG=str(out / 'helper.log'), XDG_RUNTIME_DIR=str(out / 'rt'))
(out / 'rt').mkdir(mode=0o700)
fx = subprocess.Popen([fixture, '--geometry=0,0,%d,%d' % (W, H), '--rows=' + os.environ.get('X4K_ROWS', '600'), '--notch=100', '--smooth'], env=env, stdout=subprocess.PIPE, text=True)
while 'ready' not in (fx.stdout.readline() or 'ready'):
    pass
time.sleep(1)
(out / 'stage').mkdir(mode=0o700)
d = subprocess.Popen(pre + [driver, '--helper', helper, '--rect', '0,0,%d,%d' % (W, H), '--out', str(out / 'stage'), '--max-height', '60000', '--driver', 'putgd'],
                     env=env, stdout=subprocess.PIPE, stderr=open(out / 'driver.err', 'w'), text=True)
m = r.Meter(d.pid)
m.xorg = xv.pid
lines = d.stdout.read().splitlines()
d.wait(timeout=600)
meter = m.done()
fin = next((json.loads(l) for l in lines if l.startswith('{') and '"finished"' in l), None)
for f in (out / 'stage').iterdir():
    f.unlink()
fx.terminate(); fx.wait(5); xv.terminate(); xv.wait(5)
res = {'tag': tag, 'size': [W, H], 'cpus': cpus, 'meter': meter, 'end': fin and fin.get('endReason'), 'height': fin and fin.get('height'),
       'skipped': fin and fin.get('framesSkipped'), 'fps': fin and fin.get('stats', {}).get('framesPerSecond'), 'source': fin and fin.get('stats', {}).get('sourceRate')}
(out / 'result.json').write_text(json.dumps(res, indent=1))
(out / 'driver.log').write_text('\n'.join(lines))
print(json.dumps(res), flush=True)
