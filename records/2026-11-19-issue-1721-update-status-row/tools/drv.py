#!/usr/bin/env python3
"""#1721 lab driver on f44: private put.gd resident on the GNOME Wayland desktop.
usage: drv.py start NAME RESIDENT CLI | cli NAME CLI METHOD [JSON] | shot OUT | click X Y | press NAME CLI X Y COUNT WAIT OUTPREFIX | stop NAME"""
import json, os, subprocess, sys, time, signal
sys.path.insert(0, os.path.expanduser('~/work/w1721/drv'))
import rfb
BASE = os.path.expanduser('~/work/w1721/lab')
def env(name):
    root = os.path.join(BASE, name)
    run = '/var/home/patrick/p1721' + name[0]
    for d in ('config', 'data', 'cache', 'state', 'logs'):
        os.makedirs(os.path.join(root, d), exist_ok=True)
    os.makedirs(run, mode=0o700, exist_ok=True); os.chmod(run, 0o700)
    e = {k: v for k, v in os.environ.items() if k in ('PATH', 'HOME', 'USER', 'LOGNAME', 'LANG', 'SHELL')}
    e.update(XDG_CONFIG_HOME=root + '/config', XDG_DATA_HOME=root + '/data', XDG_CACHE_HOME=root + '/cache', XDG_STATE_HOME=root + '/state',
             XDG_RUNTIME_DIR=run, WAYLAND_DISPLAY='/run/user/1000/wayland-1', QT_QPA_PLATFORM='wayland',
             DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus', XDG_CURRENT_DESKTOP='KDE', XDG_SESSION_TYPE='wayland',
             DESKTOP_SESSION='plasma', XDG_SESSION_DESKTOP='KDE', KDE_FULL_SESSION='true')
    sock = run + '/putgd/session.sock'
    assert len(sock.encode()) <= 107, sock
    return root, e
def cli(name, binary, method, params=None):
    _, e = env(name)
    r = subprocess.run([binary, method, json.dumps(params or {})], env=e, capture_output=True, text=True, timeout=90)
    return r.stdout.strip() or r.stderr.strip()
def shot(out):
    c = rfb.RFB(5900); c.screenshot(out); c.close()
def main(a):
    if a[0] == 'start':
        name, resident, binary = a[1:4]
        root, e = env(name)
        log = open(root + '/logs/resident.log', 'a')
        p = subprocess.Popen([resident], env=e, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        open(root + '/resident.pid', 'w').write(str(p.pid))
        for _ in range(120):
            out = cli(name, binary, 'update.status')
            if out.startswith('{') and json.loads(out).get('ok'):
                print('resident', p.pid, 'ready'); print(out[:600]); return
            time.sleep(0.5)
        print('not ready:', out[:400]); sys.exit(1)
    if a[0] == 'cli':
        print(cli(a[1], a[2], a[3], json.loads(a[4]) if len(a) > 4 else None)[:2000])
    if a[0] == 'shot':
        shot(a[1])
    if a[0] == 'click':
        c = rfb.RFB(5900); c.click(int(a[1]), int(a[2])); time.sleep(0.3); c.pointer(5, 5); c.close()
    if a[0] == 'key':
        c = rfb.RFB(5900); c.key(*a[1:]); c.close()
    if a[0] == 'press':
        name, binary, x, y, count, wait, prefix = a[1], a[2], int(a[3]), int(a[4]), int(a[5]), float(a[6]), a[7]
        for i in range(count):
            c = rfb.RFB(5900); c.click(x, y); time.sleep(0.2); c.pointer(5, 5); c.close()
            time.sleep(wait)
            st = json.loads(cli(name, binary, 'update.status') or '{}')
            res = (st.get('result') or {})
            shot('%s-%02d.png' % (prefix, i + 1))
            print(i + 1, 'checking', res.get('checking'), 'checkedAt', res.get('checkedAt'), 'latest', (res.get('result') or {}).get('latest'), flush=True)
    if a[0] == 'stop':
        name = a[1]; root, _ = env(name)
        pid = int(open(root + '/resident.pid').read())
        os.kill(pid, signal.SIGTERM); print('sent TERM to', pid)
main(sys.argv[1:])
