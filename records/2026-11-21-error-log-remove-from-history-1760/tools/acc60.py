#!/usr/bin/env python3
"""#1760 Error log Remove from History only picture on aurora-amd: a private resident of the dev build
(Toolbx) on the real Plasma Wayland session, the loopback uploader fixture with no token, session
calls and VNC frames.  acc60.py start-receiver | start | stop | call METHOD [JSON] | shot NAME | click X Y
State lives in ~/work/errlog-1753/acc60/."""
import json, os, socket, subprocess, sys, time, uuid, urllib.request
from pathlib import Path

ROOT = Path.home() / 'work/errlog-1753'
ACC = ROOT / 'acc60'
TREE = ROOT / 'tree'
RUNTIME = '/run/user/1000/pe60'
SOCKET = RUNTIME + '/putgd/session.sock'
sys.path.insert(0, str(TREE / 'tools/lab'))


def session_env():
    pid = subprocess.run(['pgrep', '-u', 'patrick', '-x', 'plasmashell'], capture_output=True, text=True).stdout.split()[0]
    env = dict(item.split('=', 1) for item in Path(f'/proc/{pid}/environ').read_bytes().decode().split('\0') if '=' in item)
    if not env.get('WAYLAND_DISPLAY', '').startswith('/'):
        env['WAYLAND_DISPLAY'] = '/run/user/1000/' + env.get('WAYLAND_DISPLAY', 'wayland-0')
    for key, sub in (('XDG_CONFIG_HOME', 'config'), ('XDG_DATA_HOME', 'data'), ('XDG_STATE_HOME', 'state'), ('XDG_CACHE_HOME', 'cache')):
        env[key] = str(ACC / sub)
    env['XDG_RUNTIME_DIR'] = RUNTIME
    return env


def call(method, params=None, timeout=330):
    request = {'schemaVersion': 1, 'requestId': str(uuid.uuid4()), 'session': SOCKET, 'method': method, 'params': params or {}}
    with socket.socket(socket.AF_UNIX) as s:
        s.settimeout(timeout)
        s.connect(SOCKET)
        s.sendall((json.dumps(request) + '\n').encode())
        data = b''
        while chunk := s.recv(65536):
            data += chunk
    return json.loads(data)


def main():
    ACC.mkdir(parents=True, exist_ok=True)
    command = sys.argv[1]
    if command == 'start-receiver':
        process = subprocess.Popen([sys.executable, '-I', str(TREE / 'tests/fixtures/http_uploader_server.py')], stdout=subprocess.PIPE, text=True,
                                   stderr=open(ACC / 'receiver.log', 'w'), start_new_session=True)
        port = process.stdout.readline().strip()
        (ACC / 'receiver.json').write_text(json.dumps({'pid': process.pid, 'port': int(port)}))
        request = urllib.request.Request(f'http://127.0.0.1:{port}/__reset', data=json.dumps({'auth': 'none'}).encode(), headers={'Content-Type': 'application/json'}, method='POST')
        urllib.request.urlopen(request, timeout=10).read()
        print(port)
    elif command == 'start':
        os.makedirs(RUNTIME, mode=0o700, exist_ok=True)
        log = open(ACC / f'resident-{int(time.time())}.log', 'w')
        env = session_env()
        keep = ('XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'XDG_STATE_HOME', 'XDG_CACHE_HOME', 'XDG_RUNTIME_DIR', 'DBUS_SESSION_BUS_ADDRESS', 'WAYLAND_DISPLAY', 'XDG_CURRENT_DESKTOP', 'XDG_SESSION_TYPE', 'XDG_SESSION_DESKTOP', 'KDE_FULL_SESSION', 'DESKTOP_SESSION')
        command = ['toolbox', 'run', '-c', 'putgd-build', 'env'] + [f'{k}={env[k]}' for k in keep if k in env] + [str(TREE / 'build/dev/putgd'), '--background']
        process = subprocess.Popen(command, env=dict(os.environ, XDG_RUNTIME_DIR='/run/user/1000'), stdout=log, stderr=log, start_new_session=True)
        (ACC / 'resident.json').write_text(json.dumps({'pid': process.pid}))
        for _ in range(300):
            if Path(SOCKET).exists():
                break
            time.sleep(.1)
        print(json.dumps({'pid': process.pid, 'socket': Path(SOCKET).exists()}))
    elif command == 'stop':
        print(json.dumps(call('ui.quit')))
    elif command == 'call':
        params = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        print(json.dumps(call(sys.argv[2], params), indent=1))
    elif command in ('shot', 'click'):
        from rfb import RFB
        vnc = RFB(5900)
        try:
            if command == 'shot':
                (ACC / 'frames').mkdir(exist_ok=True)
                vnc.screenshot(str(ACC / 'frames' / (sys.argv[2] + '.png')))
                print(vnc.width, vnc.height)
            else:
                vnc.click(int(sys.argv[2]), int(sys.argv[3]))
        finally:
            vnc.close()


if __name__ == '__main__':
    main()
