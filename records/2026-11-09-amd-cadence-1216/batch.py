#!/usr/bin/env python3
"""#1216: alternate hardware and software 1080p60 fluidity runs, ABBA order. Each run is one CLI invocation."""
import glob, json, os, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(os.environ.get('I1216_ROOT', str(Path.home() / 'i1216'))).resolve()
TAG = sys.argv[1]            # output folder name
PAIRS = int(sys.argv[2])     # hw+sw pairs
EXTRA = sys.argv[3:]         # extra fluidity_run args, e.g. --env KEY=VALUE, applied to both modes
BASE = ROOT / TAG
BASE.mkdir(parents=True, exist_ok=True)
APP = next(ROOT.glob('putgd-*.AppImage'))
order = []
for p in range(PAIRS):
    order += ['hw', 'sw'] if p % 2 == 0 else ['sw', 'hw']
index = []
for n, mode in enumerate(order, 1):
    run = BASE / mode
    cmd = [sys.executable, str(ROOT / 'tools/lab/fluidity_run.py'), 'record', '--run', str(run), '--runtime-dir', '/run/user/1000/i1216',
           '--build', 'lab=' + str(APP), '--kwin-entry', 'lab', '--env', 'PIPEWIRE_RUNTIME_DIR=/run/user/1000', '--output', 'DP-2', '--frames', '--seconds', '10']
    if mode == 'sw':
        cmd += ['--env', 'LIBVA_DRIVER_NAME=none']
    cmd += EXTRA
    began = time.time()
    p = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stamp = 'r%02d-%s' % (n, mode)
    # One CLI run writes results.json and *-lab-1.* logs: keep them under this run's number.
    shutil.copy2(run / 'results.json', BASE / (stamp + '.json'))
    for f in glob.glob(str(run / 'logs' / '*-lab-1*')):
        os.rename(f, f.replace('-lab-1', '-' + stamp))
    for f in glob.glob(str(run / 'frames' / '*-lab-1*')):
        os.rename(f, f.replace('-lab-1', '-' + stamp))
    entry = {'n': n, 'mode': mode, 'rc': p.returncode, 'stdout': p.stdout.strip()[-400:], 'seconds': round(time.time() - began, 1)}
    index.append(entry)
    (BASE / 'index.json').write_text(json.dumps(index, indent=1) + '\n')
    print(entry, flush=True)
print('done', flush=True)
