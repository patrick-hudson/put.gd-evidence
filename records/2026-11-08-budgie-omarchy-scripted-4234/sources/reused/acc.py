#!/usr/bin/env python3
"""In-guest acceptance driver for put.gd on Hyprland (Omarchy golden).

acc.py start [BIN]        start the resident in the session environment (BIN: /usr/bin/putgd or an AppImage)
acc.py cli METHOD [JSON]  run putgd-cli
acc.py local              local-only output for every capture (archive.keepUploads + captureDefaults local)
acc.py caps               adapter, capture and shortcut summary
acc.py last [N]           newest N operations with their local files and image facts
acc.py img PATH           size and colour facts of an image
acc.py quit               ui.quit and wait for the socket to go
"""
import json, os, subprocess, sys, time, glob, collections, shutil

HOME = os.path.expanduser('~')
STATE = os.path.join(HOME, 'd', 'acc'); os.makedirs(STATE, exist_ok=True)

def session_env():
    pid = subprocess.run(['pgrep', '-u', str(os.getuid()), '-x', 'quickshell'], capture_output=True, text=True).stdout.split()[0]
    env = {}
    for kv in open(f'/proc/{pid}/environ', 'rb').read().split(b'\0'):
        if b'=' in kv:
            k, v = kv.decode(errors='replace').split('=', 1); env[k] = v
    keep = {k: v for k, v in env.items() if k.startswith(('XDG_', 'QT_', 'GDK_', 'OMARCHY_')) or k in (
        'WAYLAND_DISPLAY', 'DISPLAY', 'HYPRLAND_INSTANCE_SIGNATURE', 'PATH', 'DESKTOP_SESSION', 'DBUS_SESSION_BUS_ADDRESS', 'LANG', 'HOME', 'USER')}
    keep.setdefault('HOME', HOME)
    return keep

def cli_binary():
    saved = os.path.join(STATE, 'cli')
    if os.path.exists(saved): return open(saved).read().strip()
    return shutil.which('putgd-cli') or 'putgd-cli'

def cli(method, params=None, timeout=60):
    args = [cli_binary(), method] + ([json.dumps(params)] if params is not None else [])
    r = subprocess.run(args, capture_output=True, text=True, env=session_env(), timeout=timeout)
    try: return json.loads(r.stdout)
    except ValueError: return {'ok': False, 'raw': r.stdout[-2000:], 'stderr': r.stderr[-2000:], 'exit': r.returncode}

def image_facts(path):
    from PIL import Image
    im = Image.open(path).convert('RGBA'); w, h = im.size
    px = im.getdata(); step = max(1, (w * h) // 200000)
    cnt = collections.Counter(px[i] for i in range(0, w * h, step))
    return {'path': path, 'size': [w, h], 'top': [[list(c), n] for c, n in cnt.most_common(4)], 'alphaZero': sum(n for c, n in cnt.items() if c[3] == 0)}

def main():
    a = sys.argv[1:]
    if a[0] == 'start':
        binary = a[1] if len(a) > 1 else '/usr/bin/putgd'
        env = session_env()
        if binary.endswith('.AppImage'):
            # The AppImage's own CLI: extract-free through the mounted image's usr/bin once the resident runs.
            open(os.path.join(STATE, 'appimage'), 'w').write(binary)
        log = open(os.path.join(STATE, 'resident.log'), 'ab')
        p = subprocess.Popen([binary, '--background'], env=env, stdout=log, stderr=log, stdin=subprocess.DEVNULL, start_new_session=True)
        open(os.path.join(STATE, 'resident.pid'), 'w').write(str(p.pid))
        sock = os.path.join(env['XDG_RUNTIME_DIR'], 'putgd', 'session.sock')
        for _ in range(60):
            if os.path.exists(sock): break
            time.sleep(0.5)
        if binary.endswith('.AppImage'):
            mounts = sorted(glob.glob('/tmp/.mount_putgd*/usr/bin/putgd-cli'), key=os.path.getmtime)
            if mounts: open(os.path.join(STATE, 'cli'), 'w').write(mounts[-1])
        elif os.path.exists(os.path.join(STATE, 'cli')): os.remove(os.path.join(STATE, 'cli'))
        time.sleep(2)
        print(json.dumps({'pid': p.pid, 'socket': os.path.exists(sock), 'cli': cli_binary()}))
    elif a[0] == 'cli':
        print(json.dumps(cli(a[1], json.loads(a[2]) if len(a) > 2 else None, timeout=int(a[3]) if len(a) > 3 else 60), indent=1))
    elif a[0] == 'local':
        got = cli('settings.get'); rev = got['result']['metadata']['observedRevision']
        patch = {'archive': {'keepUploads': True}, 'captureDefaults': {'destination': 'local', 'profileId': None, 'publicationMode': 'default'}}
        for action in ('region', 'window', 'desktop', 'clipboard'):
            patch.setdefault('actions', {})[action] = {'destination': 'default', 'profileId': None, 'publicationMode': 'default'}
        print(json.dumps(cli('settings.patch', {'patch': patch, 'expectedRevision': rev})))
    elif a[0] == 'caps':
        c = cli('capabilities')['result']; s = c.get('source', c)
        print(json.dumps({'adapter': s.get('adapter'), 'capture': {k: {kk: vv for kk, vv in v.items() if kk != 'helper'} for k, v in s.get('capture', {}).items()},
                          'shortcuts': s.get('shortcuts'), 'clipboard': s.get('clipboard', {}).get('available')}, indent=1))
    elif a[0] == 'last':
        n = int(a[1]) if len(a) > 1 else 1
        records = cli('history.list', {'limit': n, 'offset': 0})['result'].get('records', [])
        out = []
        for r in records[:n]:
            path = (r.get('local') or {}).get('path')
            entry = {'id': r['id'], 'operation': r.get('operationId'), 'name': r.get('name'), 'created': r.get('created'), 'local': path}
            if path and os.path.exists(path) and path.endswith('.png'): entry['image'] = image_facts(path)
            out.append(entry)
        print(json.dumps(out, indent=1))
    elif a[0] == 'img':
        print(json.dumps(image_facts(a[1])))
    elif a[0] == 'quit':
        print(json.dumps(cli('ui.quit')))
        sock = os.path.join(session_env()['XDG_RUNTIME_DIR'], 'putgd', 'session.sock')
        for _ in range(40):
            if not os.path.exists(sock): break
            time.sleep(0.5)
        print(json.dumps({'socketGone': not os.path.exists(sock)}))

main()
