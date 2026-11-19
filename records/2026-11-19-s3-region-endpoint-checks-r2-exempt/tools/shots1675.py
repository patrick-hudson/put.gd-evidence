#!/usr/bin/env python3
"""#1675/#1676 Settings pictures on m74 (Cinnamon X11), one step per call. Hold the desktop lock.

  python3 shots1675.py --build DIR --run DIR start
  python3 shots1675.py --build DIR --run DIR shot NAME
  python3 shots1675.py --build DIR --run DIR click RX RY | type TEXT | key KEYS | wheel N | clear RX RY | stop

A PRIVATE resident of the build under test (own XDG folders, own runtime folder; nothing of the desktop user's
configuration or keyring) shows Settings on :0. No credentials are involved; account and bucket are synthetic.
"""
import argparse
import json
import os
import signal
import subprocess
import time
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--build', required=True)
parser.add_argument('--run', required=True)
parser.add_argument('step')
parser.add_argument('args', nargs='*')
options = parser.parse_args()
HOME = Path.home()
BUILD, R = Path(options.build), Path(options.run)
SHOTS = R / 'shots'
UID = os.getuid()
RT = Path('/run/user/%d/pg1675' % UID)
ENV = dict(os.environ, DISPLAY=':0', XAUTHORITY=str(HOME / '.Xauthority'), DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/%d/bus' % UID,
           XDG_SESSION_TYPE='x11', XDG_CURRENT_DESKTOP='X-Cinnamon', XDG_CONFIG_HOME=str(R / 'cfg'), XDG_DATA_HOME=str(R / 'data'),
           XDG_STATE_HOME=str(R / 'state'), XDG_CACHE_HOME=str(R / 'cache'), XDG_RUNTIME_DIR=str(RT))
XENV = dict(os.environ, DISPLAY=':0', XAUTHORITY=str(HOME / '.Xauthority'))
W, H = 1240, 1000


def cli(method, params=None, timeout=60):
    out = subprocess.run([str(BUILD / 'putgd-cli'), '--params-stdin', method], input=json.dumps(params or {}), capture_output=True, text=True, env=ENV, timeout=timeout)
    try:
        return json.loads(out.stdout)
    except ValueError:
        return {'ok': False, 'error': {'code': 'no_reply', 'message': (out.stdout + out.stderr)[:200]}, 'result': {}}


def x(*args):
    return subprocess.run(list(args), capture_output=True, text=True, env=XENV).stdout.strip()


def until(check, seconds=30, step=0.3):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        value = check()
        if value:
            return value
        time.sleep(step)
    return None


def geometry(window):
    values = dict(line.split('=') for line in x('xdotool', 'getwindowgeometry', '--shell', window).splitlines() if '=' in line)
    try:
        return int(values['X']), int(values['Y']), int(values['WIDTH']), int(values['HEIGHT'])
    except (KeyError, ValueError):
        return None


def window():
    pid = cli('ui.snapshot')['result'].get('diagnostics', {}).get('ui', {}).get('pid')
    best, area = None, 0
    for candidate in x('xdotool', 'search', '--onlyvisible', '--pid', str(pid)).split() if pid else []:
        g = geometry(candidate)
        if g and g[2] * g[3] > area:
            best, area = candidate, g[2] * g[3]
    return best


def park():
    x('xdotool', 'mousemove', '1900', '1060')


step = options.step
if step == 'start':
    for folder in (R, SHOTS, R / 'cfg', R / 'data', R / 'state', R / 'cache'):
        folder.mkdir(parents=True, exist_ok=True)
    os.chmod(R, 0o700)
    RT.mkdir(mode=0o700, exist_ok=True)
    (RT / 'putgd').mkdir(exist_ok=True)
    (RT / 'putgd/session.sock').unlink(missing_ok=True)
    version = json.loads(subprocess.run([str(BUILD / 'putgd-cli'), '--version-json'], capture_output=True, text=True).stdout)
    (SHOTS / 'build.json').write_text(json.dumps(version, indent=1))
    print('build', version.get('version'), version.get('gitCommit'))
    resident = subprocess.Popen([str(BUILD / 'putgd'), '--background'], env=ENV, stdout=open(R / 'resident.log', 'a'), stderr=subprocess.STDOUT, start_new_session=True)
    (R / 'resident.pid').write_text(str(resident.pid))
    assert until(lambda: (RT / 'putgd/session.sock').exists(), 20), 'resident did not start'
    time.sleep(3)
    print('settings', json.dumps(cli('settings.get')['result'].get('metadata', {}).get('validation')))
    assert cli('ui.show', {'view': 'destinations'})['ok']
    w = until(window, 20)
    assert w, 'no put.gd window'
    x('xdotool', 'windowsize', w, str(W), str(H))
    x('xdotool', 'windowmove', w, '120', '20')
    time.sleep(1.2)
    print('window', w, geometry(window()))
elif step == 'shot':
    w = window()
    g = geometry(w)
    park()
    time.sleep(0.6)
    path = SHOTS / (options.args[0] + '.png')
    subprocess.run(['import', '-window', 'root', '-crop', '%dx%d+%d+%d' % (g[2], g[3], g[0], g[1]), '+repage', str(path)], env=XENV)
    print('shot', path, g)
elif step in ('click', 'clear'):
    g = geometry(window())
    x('xdotool', 'mousemove', str(g[0] + int(options.args[0])), str(g[1] + int(options.args[1])))
    time.sleep(0.2)
    x('xdotool', 'click', '1')
    if step == 'clear':
        time.sleep(0.2)
        x('xdotool', 'key', 'ctrl+a', 'BackSpace')
elif step == 'type':
    x('xdotool', 'type', '--delay', '25', options.args[0])
elif step == 'key':
    x('xdotool', 'key', *options.args)
elif step == 'wheel':
    g = geometry(window())
    x('xdotool', 'mousemove', str(g[0] + 1180), str(g[1] + 620))
    n = int(options.args[0])
    for _ in range(abs(n)):
        x('xdotool', 'click', '5' if n > 0 else '4')
        time.sleep(0.03)
elif step == 'profile':
    # One synthetic S3 destination, as Settings saves it, from the development template.
    current = cli('settings.get')['result']
    template = cli('settings.developmentTemplate')['result']['document']['profiles'][0]
    template.update(id='r2', label='Cloudflare R2', credentials={'mode': 'session', 'reference': None})
    template['settings'].update(json.loads(options.args[0]))
    document = current['document']
    document['profiles'] = [template]
    document['actions'] = {name: dict(action, shortcut='') for name, action in document['actions'].items()}
    print(json.dumps(cli('settings.save', {'document': document, 'expectedRevision': current['metadata']['observedRevision']})['error']))
elif step == 'inspect':
    print(json.dumps(cli('settings.get')['result']['document']['profiles'], indent=1)[:3000])
    print(json.dumps(cli('ui.viewState')['result'], indent=1)[:1500])
elif step == 'stop':
    cli('ui.quit')
    time.sleep(1.5)
    pid = int((R / 'resident.pid').read_text())
    try:
        os.kill(pid, 0)
        os.kill(pid, signal.SIGTERM)
        print('resident', pid, 'sent SIGTERM')
    except ProcessLookupError:
        print('resident', pid, 'gone')
    for leftover in (RT / 'putgd/session.sock', RT / 'dconf/user'):
        leftover.unlink(missing_ok=True)
    for folder in (RT / 'putgd', RT / 'dconf', RT):
        try:
            folder.rmdir()
        except OSError:
            pass
    print('runtime folder gone:', not RT.exists())
