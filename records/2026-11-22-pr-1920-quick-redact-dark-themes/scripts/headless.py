"""Run file controls and render evidence through a private offscreen put.gd editor."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import time

import capture

root = Path(sys.argv[1]).resolve()
build = sys.argv[2]
mode = sys.argv[3]
runtime = Path(tempfile.mkdtemp(prefix='h-', dir=root))
out = root / 'results' / build
out.mkdir(parents=True, exist_ok=True)
color = '#D7263D'

def setup():
    socket = runtime / 'putgd/session.sock'
    resolved = len(os.fsencode(socket.resolve()))
    address = os.environ['DBUS_SESSION_BUS_ADDRESS']
    if not address.startswith('unix:path='):
        raise RuntimeError('Expected a private Unix D-Bus socket')
    bus = Path(address.split('unix:path=',1)[1].split(',',1)[0])
    for path in (socket, bus):
        length = len(os.fsencode(path.resolve()))
        if length > 107:
            raise RuntimeError(f'Unix socket over 107 bytes: {path} ({length})')
        print(f'Socket preflight: {path} ({length} bytes)', flush=True)
    runtime.chmod(0o700)
    assert resolved <= 107
    os.environ.update({'XDG_RUNTIME_DIR': str(runtime), 'QT_QPA_PLATFORM': 'offscreen',
                       'DISPLAY': '', 'WAYLAND_DISPLAY': ''})
    for role in ('config','data','state','cache'):
        dest = root / ('off-' + role)
        dest.mkdir(mode=0o700, exist_ok=True)
        os.environ[f'XDG_{role.upper()}_HOME'] = str(dest)

def annotate():
    pictures = root / 'pictures'
    pictures.mkdir(exist_ok=True)
    for baseline in sorted((root / 'results/nightly').glob('*-verify.json')):
        scene = baseline.name.removesuffix('-verify.json')
        candidate = root / 'results/candidate' / baseline.name
        if not candidate.exists():
            continue
        reports = [json.loads(p.read_text()) for p in (baseline,candidate)]
        changed = [name for name, before in reports[0]['rows'].items()
                   if before['coverage'] != 'full' and reports[1]['rows'][name]['coverage'] == 'full'
                   and before['kind'] != 'decoy']
        if not changed:
            changed = [name for name, after in reports[1]['rows'].items()
                       if after['coverage'] != 'full' and (after['kind'] != 'decoy' or after['coverage'] != 'missed')]
            if not changed and scene.startswith('file-'):
                changed = list(reports[0]['rows'])
        for build_label, report in zip(('nightly','candidate'), reports):
            prefix = 'nightly' if build_label == 'nightly' else '#1920'
            if (pictures / f'{scene}-{build_label}.png').exists():
                continue
            op = capture.open_editor(root / 'results' / build_label / f'{scene}-red.png')
            try:
                commands = []
                def add(kind, **fields):
                    commands.append({'op':'add','shape':{'kind':kind,'color':color,**fields}})
                boxes = [report['rows'][name]['box'] for name in changed]
                if boxes:
                    min_x = min(box[0] for box in boxes)
                    for x0,y0,x1,y1 in boxes:
                        add('ellipse', rect=[x0-12, y0-5, x1-x0+24, y1-y0+10], width=4)
                    values = {report['rows'][name]['coverage'] for name in changed}
                    caption = 'covered' if values == {'full'} else next(iter(values)) if len(values)==1 else 'mixed coverage'
                    if caption == 'partly':
                        caption = 'partly covered'
                else:
                    min_x = 50
                    caption = 'all tokens covered'
                width,height = report['size']
                last_y = max(row['box'][3] for row in report['rows'].values())
                tx,ty = max(12,min_x-40), min(height-34,last_y+48)
                add('text', at=[tx,ty], text=f'{prefix}: {caption}', fontPixels=20)
                decoys = [row for row in report['rows'].values()
                          if row['kind'] == 'decoy' and row['coverage'] != 'missed']
                if decoys:
                    for row in decoys:
                        x0,y0,x1,y1 = row['box']
                        add('rectangle', rect=[x0-8,y0-3,x1-x0+16,y1-y0+6], width=4)
                    add('text', at=[tx,ty+29], text=f'Decoys covered: {len(decoys)}', fontPixels=20)
                if boxes:
                    x0,y0,x1,y1 = max(boxes,key=lambda box: box[3])
                    add('arrow', **{'from':[tx-12,ty+8], 'to':[x0-9,y1+4], 'width':4})
                if not scene.startswith('file-'):
                    last_x = max(row['box'][2] for row in report['rows'].values())
                    commands.append({'op':'crop','rect':[0,0,min(width,last_x+36),min(height,ty+(65 if decoys else 36))]})
                capture.cli('editor.apply', {**op, 'commands':commands})
                capture.save(op, pictures / f'{scene}-{build_label}.png')
            finally:
                capture.cli('editor.cancel', op)
        print('Annotated', scene, flush=True)

setup()
with (out / f'headless-{mode}.log').open('w') as log:
    with subprocess.Popen(['/usr/bin/putgd','--background'], stdout=log, stderr=log) as app:
        try:
            for _ in range(80):
                if (runtime / 'putgd/session.sock').is_socket():
                    break
                if app.poll() is not None:
                    raise RuntimeError('Offscreen resident exited')
                time.sleep(.25)
            identity = capture.cli('diagnostics')['build']
            expected = {'nightly':'65df546861260bcb92f41ce3f24d3130e90e0c11',
                        'candidate':'667738ff4495562fd1dc4be3315683ae841ce63d'}[build]
            if identity['gitTree'] != expected:
                raise RuntimeError(f'Wrong offscreen build: {identity}')
            if mode == 'controls':
                for scene in (sys.argv[4:] or ('file-whole','file-crop')):
                    if not (out / f'{scene}-verify.json').exists():
                        capture.run(out, scene, root / 'fixture' / (scene[5:]+'.png'))
                        capture.analyze(out, scene, root / 'fixture')
            elif mode == 'annotate':
                annotate()
            else:
                raise ValueError(f'Unknown mode: {mode}')
        finally:
            app.terminate()
            app.wait(timeout=10)
