#!/usr/bin/env python3
"""FIX-5 step 4: the GNOME rows that matter, with the installed package. rows.py DIR STEP...
Steps: setup plain long scaled user record finish. Uses the confirmation pass's pass2.capture and verifiers."""
import sys, json, time, subprocess, os, signal, hashlib, shutil, argparse
from pathlib import Path
sys.path.insert(0, '/home/patrick/work/pc2')
import pass2 as p, rfb
P = Path.home() / 'work/fx5' / sys.argv[1]
p.P = P
PC2 = Path('/home/patrick/work/pc2')
REAL = dict(os.environ, XDG_RUNTIME_DIR='/run/user/1000', DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus')
rpc = p.rpc


def env():
    return json.loads((P / 'env.json').read_text())


def owned(prefix):
    mark = ('XDG_CONFIG_HOME=' + str(P / 'c')).encode(); found = []
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit():
            continue
        try:
            if (proc / 'comm').read_text().strip().startswith(prefix) and mark in (proc / 'environ').read_bytes().split(b'\0'):
                found.append(int(proc.name))
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            pass
    return found


def patch(v):
    s = rpc('settings.get'); return rpc('settings.patch', {'patch': v, 'expectedRevision': s['metadata']['observedRevision']})


def fixture(name, cmd, call, wait=3):
    f = subprocess.Popen(cmd, env=env(), stdout=open(P / (name + '-fixture.log'), 'w'), stderr=subprocess.STDOUT, start_new_session=True)
    try:
        time.sleep(wait); return call()
    finally:
        f.terminate(); f.wait(15)


def shell():
    return subprocess.run(['pgrep', '-u', str(os.getuid()), '-x', 'gnome-shell'], capture_output=True, text=True).stdout.split()


def step(name):
    if name == 'setup':
        P.mkdir(exist_ok=True)
        rpm = sorted((Path.home() / 'work/fx5/ci').glob('*.rpm'))[-1]
        if not list(P.glob('*.rpm')):
            shutil.copyfile(rpm, P / rpm.name)
        p.setup()
        for pid in owned('putgd-ui'):
            os.kill(pid, signal.SIGTERM)
        patch({'preferences': {'notifications': False, 'scrollCaptureFromTop': True}})
        print(json.dumps({'setup': json.loads((P / 'identity.json').read_text())['build'], 'shell': shell()}))
    elif name == 'plain':
        for i in range(3):
            fixture('plain-%d' % i, ['python3', str(PC2 / 'qt_fixture.py'), '--rows', '60', '--start', '0'], lambda: p.capture('plain-%d' % i, 60, 40000))
    elif name == 'long':
        for i in range(3):
            fixture('long-bottom-%d' % i, ['python3', str(PC2 / 'qt_fixture.py'), '--rows', '600', '--start', '23400'], lambda: p.capture('long-bottom-%d' % i, 600, 40000))
    elif name == 'scaled':
        import dbus
        o = dbus.SessionBus().get_object('org.gnome.Mutter.DisplayConfig', '/org/gnome/Mutter/DisplayConfig')
        state = o.GetCurrentState(dbus_interface='org.gnome.Mutter.DisplayConfig'); old = float(state[2][0][2])
        (P / 'scale-original.txt').write_text(str(old))
        try:
            subprocess.run(['python3', str(Path.home() / 'work/p4/gnome_scale.py'), '1.25'], check=True, env=REAL, stdout=subprocess.DEVNULL)
            fixture('scaled', ['python3', str(PC2 / 'qt_fixture.py')], lambda: p.capture('scaled-00', 60, None, 1.25))
        finally:
            subprocess.run(['python3', str(Path.home() / 'work/p4/gnome_scale.py'), str(old)], check=True, env=REAL, stdout=subprocess.DEVNULL)
            subprocess.run(['systemctl', '--user', 'restart', 'putgd-gnome-vnc.service'], env=REAL); time.sleep(3)
    elif name == 'user':
        s = rpc('settings.get'); old = s['document']['actions']['scroll']['shortcut']
        patch({'actions': {'scroll': {'shortcut': 'Ctrl+Shift+F7'}}})
        out = P / 'user'; out.mkdir(exist_ok=True)

        def run():
            v = rfb.RFB(5901); before = rpc('history.list', {'limit': 200})
            v.key('ctrl', 'shift', 'f7'); time.sleep(1); v.screenshot(out / 'selector.png'); v.drag(100, 200, 1060, 800)
            for i in range(25):
                v.screenshot(out / ('screen-%02d.png' % i)); time.sleep(.3)
            v.sock.close()
            after = rpc('history.list', {'limit': 200})
            known = {r['id'] for r in before['records']}; new = [r for r in after['records'] if r['id'] not in known]
            result = {'newRecords': new}
            if len(new) == 1:
                shutil.copyfile(new[0]['local']['path'], out / 'capture.png')
                import scroll_run
                a = argparse.Namespace(scale=1, height=2400, rows=60, first_pixel=0, header=0, footer=0, code_width=960, format='fixture', scrollbar=0)
                result['verification'] = scroll_run.verify(out / 'capture.png', a)
            result['pass'] = len(new) == 1 and bool(result.get('verification', {}).get('pass'))
            (out / 'result.json').write_text(json.dumps(result, indent=2))
            print(json.dumps({'name': 'user', 'new': len(new), 'pass': result['pass'], 'verification': {k: v for k, v in result.get('verification', {}).items() if k in ('pass', 'height', 'width')}}))
        try:
            fixture('user', ['python3', str(PC2 / 'qt_fixture.py')], run)
        finally:
            patch({'actions': {'scroll': {'shortcut': old}}})
    elif name == 'record':
        out = P / 'record'; out.mkdir(exist_ok=True)

        def run():
            v = rpc('recording.prepare', {'target': {'kind': 'region', 'rect': [100, 200, 960, 600]}, 'format': 'mp4', 'fps': 30, 'audio': {'system': False}})
            rid = v['recordingId']
            for _ in range(200):
                v = rpc('recording.inspect', {'id': rid})
                if v['state'] != 'preparing':
                    break
                time.sleep(.1)
            ready = v; time.sleep(1)
            rpc('recording.start', {'id': rid}); time.sleep(1)
            vnc = rfb.RFB(5901); vnc.screenshot(out / 'recording.png'); vnc.sock.close()
            time.sleep(3)
            stopped = rpc('recording.stop', {'id': rid}); copy = out / 'copy.mp4'
            rpc('recording.saveCopy', {'id': rid, 'path': str(copy), 'overwrite': True})
            for _ in range(600):
                done = rpc('recording.inspect', {'id': rid})
                if done['state'] == 'reviewing' and (done.get('lastExport') or {}).get('status') not in (None, 'running', 'exporting'):
                    break
                time.sleep(.2)
            rpc('recording.cancel', {'id': rid})
            result = {'ready': {k: ready.get(k) for k in ('state', 'overlayPlacement', 'overlayExcluded')}, 'stopped': {k: stopped.get(k) for k in ('state', 'durationUs')},
                      'export': done.get('lastExport'), 'copyBytes': copy.stat().st_size if copy.is_file() else 0}
            if copy.is_file():
                probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_frames', '-show_entries',
                                                            'stream=codec_name,width,height,nb_read_frames,duration', '-of', 'json', str(copy)]))
                result['video'] = probe['streams'][0]
                sums = []
                for t in ('0.5', '1.5', '2.5'):
                    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', t, '-i', str(copy), '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True).stdout
                    sums.append(hashlib.sha256(raw).hexdigest()[:16] if raw else None)
                result['frameHashes'] = sums
                result['motion'] = None not in sums and len(set(sums)) == 3
            result['pass'] = stopped.get('state') == 'reviewing' and bool(result.get('motion')) and int(result.get('video', {}).get('nb_read_frames', 0)) > 60
            (out / 'result.json').write_text(json.dumps(result, indent=2)); print(json.dumps(dict(name='record', **result)))
        fixture('record', ['python3', str(Path.home() / 'work/fx5/anim_fixture.py')], run)
    elif name == 'finish':
        try:
            print(rpc('ui.quit'))
        except Exception as ex:
            print(type(ex).__name__)
        time.sleep(3)
        left = owned('putgd')
        for pid in left:
            os.kill(pid, signal.SIGTERM)
        print(json.dumps({'terminatedOwned': left, 'shell': shell()}))


for s in sys.argv[2:]:
    print('== ' + s, flush=True)
    step(s)
