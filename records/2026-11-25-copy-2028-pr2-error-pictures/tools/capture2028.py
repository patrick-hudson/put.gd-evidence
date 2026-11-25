#!/usr/bin/env python3
"""#2028 PR2 error-message pictures: one capture run on m74 (Cinnamon, X11).

Run on the desktop's host with the desktop lock held (desktop_lock.py run ...). Starts a PRIVATE resident
of the build under test (own XDG folders, own runtime folder, session-only credentials) on the real display,
drives it with putgd-cli and saves uncropped frames of the whole desktop with ImageMagick `import`.

  python3 capture2028.py --build DIR --run DIR --label before|after

Scenes (all offline; loopback receivers and synthetic PNGs only, no credentials):
  A (#2034, app/core)     queue_full: with Queued operations = 1 and Simultaneous uploads = 1, two uploads that
                          never get an answer fill the queue and a third upload is refused. Error log page.
  B (#2036, platform)     capture_target: the window capture started while put.gd's own window is focused.
  C (#2037, ui)           input_excessive in the editor: Largest file lowered, then Upload from the editor.
"""
import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

from PIL import Image, ImageDraw

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--build', required=True)
parser.add_argument('--run', required=True)
parser.add_argument('--label', required=True, choices=['before', 'after'])
options = parser.parse_args()

HOME = Path.home()
BUILD = Path(options.build)
R = Path(options.run)
LABEL = options.label
FRAMES = R / 'frames'
UID = os.getuid()
RT = Path('/run/user/%d/pg2028' % UID)
for folder in (R, FRAMES, R / 'keep', R / 'cfg', R / 'data', R / 'state', R / 'cache', R / 'own'):
    folder.mkdir(parents=True, exist_ok=True)
os.chmod(R, 0o700)
RT.mkdir(mode=0o700, exist_ok=True)
sock = str(RT / 'putgd/session.sock')
assert len(sock.encode()) <= 107, sock
BUS = 'unix:path=/run/user/%d/bus' % UID
ENV = dict(os.environ, DISPLAY=':0', XAUTHORITY=str(HOME / '.Xauthority'), DBUS_SESSION_BUS_ADDRESS=BUS, XDG_SESSION_TYPE='x11',
           XDG_CURRENT_DESKTOP='X-Cinnamon', XDG_CONFIG_HOME=str(R / 'cfg'), XDG_DATA_HOME=str(R / 'data'), XDG_STATE_HOME=str(R / 'state'),
           XDG_CACHE_HOME=str(R / 'cache'), XDG_RUNTIME_DIR=str(RT))
XENV = dict(os.environ, DISPLAY=':0', XAUTHORITY=str(HOME / '.Xauthority'), DBUS_SESSION_BUS_ADDRESS=BUS)
log = open(R / 'capture2028.log', 'a')
facts = {'label': LABEL, 'frames': {}}


def say(*parts):
    print(*parts, flush=True)
    print(*parts, file=log, flush=True)


def cli(method, params=None, timeout=120):
    out = subprocess.run([str(BUILD / 'putgd-cli'), '--params-stdin', method], input=json.dumps(params or {}), capture_output=True, text=True, env=ENV, timeout=timeout)
    try:
        return json.loads(out.stdout)
    except ValueError:
        return {'ok': False, 'error': {'code': 'no_reply', 'message': (out.stdout + out.stderr)[:300]}, 'result': {}}


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
        return [int(values['X']), int(values['Y']), int(values['WIDTH']), int(values['HEIGHT'])]
    except (KeyError, ValueError):
        return None


def put_windows():
    """Every visible window of a put.gd UI process: [(id, name, geometry)]."""
    ids = set()
    for pid in ui_pids():
        ids.update(x('xdotool', 'search', '--onlyvisible', '--pid', str(pid)).split())
    found = []
    for window in sorted(ids):
        g = geometry(window)
        if g and g[2] > 100 and g[3] > 60:
            found.append((window, x('xdotool', 'getwindowname', window), g))
    return found


def ui_pids():
    pids = []
    out = subprocess.run(['pgrep', '-u', str(UID), '-x', 'putgd-ui'], capture_output=True, text=True).stdout.split()
    for pid in out:
        try:
            if str(RT) in Path('/proc/%s/environ' % pid).read_bytes().decode(errors='replace'):
                pids.append(int(pid))
        except OSError:
            pass
    return pids


def frame(name):
    path = FRAMES / ('%s-%s-full.png' % (LABEL, name))
    time.sleep(0.6)
    subprocess.run(['import', '-window', 'root', str(path)], env=XENV)
    facts['frames'][name] = [{'id': w, 'name': n, 'geometry': g} for w, n, g in put_windows()]
    say('frame', path.name, Image.open(path).size, facts['frames'][name])
    return path


def park():
    x('xdotool', 'mousemove', '1900', '500')


def toast_showing():
    subprocess.run(['import', '-window', 'root', '-crop', '40x1+1700+11', '+repage', str(R / 'toast-probe.png')], env=XENV)
    r, g, b = Image.open(R / 'toast-probe.png').convert('RGB').getpixel((20, 0))
    return max(r, g, b) - min(r, g, b) > 50


def clear_toasts(limit=60):
    count = 0
    while count < limit and toast_showing():
        x('xdotool', 'mousemove', '1700', '80')
        time.sleep(0.5)
        x('xdotool', 'mousemove', '1877', '36')
        time.sleep(0.5)
        x('xdotool', 'mousedown', '1')
        time.sleep(0.15)
        x('xdotool', 'mouseup', '1')
        time.sleep(0.9)
        count += 1
    park()
    time.sleep(0.8)
    say('dismissed notifications:', count, 'still showing:', toast_showing())
    return count


procs = {}
servers = []


def hang_server():
    """A loopback receiver that takes the request and never answers."""
    listener = socket.socket()
    listener.bind(('127.0.0.1', 0))
    listener.listen(8)
    held = []

    def run():
        while True:
            try:
                connection, _ = listener.accept()
            except OSError:
                return
            held.append(connection)
            facts['hangConnections'] = len(held)

    threading.Thread(target=run, daemon=True).start()
    servers.append((listener, held))
    return listener.getsockname()[1]


def revision():
    return cli('settings.get')['result']['metadata']['observedRevision']


def sxcu(name, url):
    path = R / 'own' / (name + '.sxcu')
    path.write_text(json.dumps({'Version': '17.0.0', 'Name': name, 'DestinationType': 'ImageUploader, FileUploader', 'RequestMethod': 'POST', 'RequestURL': url,
                                'Headers': {'Authorization': 'Bearer putgd-synthetic-uploader-token-not-real'}, 'Body': 'MultipartFormData', 'FileFormName': 'file',
                                'URL': '{json:files[0].url}', 'DeletionURL': '{json:files[0].delete}'}))
    path.chmod(0o600)
    return path


def add_destination(profile, url):
    added = cli('settings.importUploader', {'path': str(sxcu(profile, url)), 'expectedRevision': revision(), 'profileId': profile, 'credentialMode': 'session', 'allowInsecureHttp': False})
    say('destination', profile, url, added['ok'], added['error'].get('code'))
    assert added['ok'], added


def png(name, color, noisy=False):
    path = R / 'own' / name
    if noisy:
        image = Image.frombytes('RGB', (640, 400), os.urandom(640 * 400 * 3))
        path = path.with_suffix('.jpg')
        image.save(path, quality=30)  # about 200 KB as a JPEG, over 700 KB once exported as PNG
        return path
    else:
        image = Image.new('RGB', (480, 270), color)
        ImageDraw.Draw(image).text((24, 24), 'put.gd #2028 synthetic ' + name, fill=(255, 255, 255))
    image.save(path)
    return path


def upload(profile, path):
    return until(lambda: (lambda reply: reply if reply['ok'] or reply['error'].get('code') != 'initializing' else None)(cli('upload.files', {'paths': [str(path)], 'profileId': profile})), 20, 0.5)


def place(window, left, top, width, height):
    x('xdotool', 'windowactivate', window)
    x('xdotool', 'windowsize', window, str(width), str(height))
    x('xdotool', 'windowmove', window, str(left), str(top))
    time.sleep(1.0)


def cleanup():
    cli('ui.quit')
    time.sleep(1.5)
    for listener, held in servers:
        listener.close()
        for connection in held:
            connection.close()
    for process in procs.values():
        if process.poll() is None:
            process.send_signal(signal.SIGTERM)
            try:
                process.wait(8)
            except subprocess.TimeoutExpired:
                process.kill()
    for leftover in (RT / 'putgd/session.sock', RT / 'dconf/user'):
        leftover.unlink(missing_ok=True)
    for folder in (RT / 'putgd', RT / 'dconf', RT):
        try:
            folder.rmdir()
        except OSError:
            pass
    say('cleanup done; runtime folder gone:', not RT.exists())
    (R / 'facts.json').write_text(json.dumps(facts, indent=1))


def main():
    version = json.loads(subprocess.run([str(BUILD / 'putgd-cli'), '--version-json'], capture_output=True, text=True).stdout)
    facts['build'] = version
    say('build', version.get('version'), version.get('gitCommit'))
    facts['dismissedBeforeStart'] = clear_toasts()
    (RT / 'putgd').mkdir(exist_ok=True)
    (RT / 'putgd/session.sock').unlink(missing_ok=True)
    procs['resident'] = subprocess.Popen([str(BUILD / 'putgd'), '--background'], env=ENV, stdout=open(R / 'resident.log', 'w'), stderr=subprocess.STDOUT)
    facts['residentPid'] = procs['resident'].pid
    assert until(lambda: (RT / 'putgd/session.sock').exists(), 20), 'resident did not start'
    time.sleep(5)
    document = cli('settings.get')['result']['document']
    actions = {name: dict(action, shortcut='') for name, action in document['actions'].items()}
    limits = dict(document['limits'], pendingOperations=1, concurrentUploads=1)
    (R / 'keep').mkdir(exist_ok=True)
    patch = {'actions': actions, 'limits': limits, 'archive': dict(document['archive'], keepUploads=True, root=str(R / 'keep'))}
    if 'updates' in document.get('preferences', {}):
        patch['preferences'] = {'updates': dict(document['preferences']['updates'], check=False)}
    patched = cli('settings.patch', {'patch': patch, 'expectedRevision': revision()})
    say('patched', patched['ok'], patched['error'].get('code'), patched['error'].get('message', ''))
    facts['limitsAfterPatch'] = cli('settings.get')['result']['document']['limits']
    port_hang = hang_server()
    add_destination('lab-hang', 'http://127.0.0.1:%d/upload' % port_hang)

    # Scene A: queue_full.
    first = upload('lab-hang', png('queue-1.png', (60, 90, 150)))
    until(lambda: facts.get('hangConnections'), 20, 0.3)
    second = upload('lab-hang', png('queue-2.png', (90, 60, 150)))
    say('first', first['ok'], 'second', second['ok'], second['error'].get('code'))
    third = upload('lab-hang', png('queue-3.png', (150, 90, 60)))
    facts['queueFull'] = third['error']
    say('third (queue_full)', third['ok'], third['error'])
    time.sleep(1.0)
    frame('toast-queue-full')
    facts['dismissedA'] = clear_toasts()
    say('errors.list', json.dumps(cli('errors.list', {'limit': 10})['result'])[:1500])
    shown = cli('ui.show', {'view': 'errors'})
    say('ui.show errors', shown['ok'], shown['error'])
    time.sleep(3.0)
    windows = put_windows()
    say('windows', windows)
    inspect = cli('ui.errorLog', {'action': 'inspect'})
    say('ui.errorLog inspect', json.dumps(inspect)[:2500])
    if windows:
        place(windows[0][0], 120, 20, 1240, 1000)
    park()
    frame('errorlog-queue-full')
    # The two uploads that never get an answer would keep the queue full for the next scenes: cancel them
    # and put the queue limits back.
    for op in (first['result']['operationId'], second['result']['operationId']):
        cancelled = cli('operation.cancel', {'id': op})
        say('cancel', op, cancelled['ok'], cancelled['error'].get('code'))
        until(lambda: cli('operation.inspect', {'id': op})['result'].get('state') in ('completed', 'partial', 'failed', 'cancelled', 'interrupted'), 30)
    restored = cli('settings.patch', {'patch': {'limits': dict(cli('settings.get')['result']['document']['limits'], pendingOperations=8, concurrentUploads=document['limits']['concurrentUploads'])}, 'expectedRevision': revision()})
    say('limits restored', restored['ok'], restored['error'].get('code'))
    # Scene B: the window capture while put.gd's own window is focused.
    windows = put_windows()
    if windows:
        x('xdotool', 'windowactivate', windows[0][0])
    time.sleep(1.0)
    captured = cli('action.invoke', {'action': 'window'}, timeout=60)
    facts['ownWindow'] = captured['error']
    say('action.invoke window', captured['ok'], captured['error'], json.dumps(captured['result'])[:300])
    time.sleep(1.2)
    frame('toast-own-window')
    time.sleep(1.5)
    frame('toast-own-window-late')
    facts['dismissedB'] = clear_toasts()
    cli('ui.show', {'view': 'errors'})
    time.sleep(1.5)
    inspect = cli('ui.errorLog', {'action': 'inspect'})
    say('ui.errorLog inspect 2', json.dumps(inspect)[:3000])
    park()
    frame('errorlog-own-window')
    # Scene C: the editor.
    # Largest file 300 KB: the JPEG source (about 200 KB) opens, but the edited image is exported as a PNG of
    # over 700 KB, which is over the limit when Upload is pressed.
    patched = cli('settings.patch', {'patch': {'limits': dict(cli('settings.get')['result']['document']['limits'], maxFileBytes=300000)}, 'expectedRevision': revision()})
    say('limit lowered', patched['ok'], patched['error'].get('code'), patched['error'].get('message'))
    facts['limitsC'] = cli('settings.get')['result']['document']['limits']
    source = png('noisy.png', None, noisy=True)
    facts['editorSourceBytes'] = source.stat().st_size
    opened = cli('editor.open', {'source': 'file', 'path': str(source)})
    say('editor.open', opened['ok'], opened['error'])
    editor = opened['result'].get('operationId')
    time.sleep(3.0)
    say('editor.inspect before submit', json.dumps(cli('editor.inspect', {'id': editor}))[:1500])
    say('editor windows', put_windows())
    submitted = cli('editor.submit', {'id': editor})
    say('editor.submit', submitted['ok'], submitted['error'], json.dumps(submitted['result'])[:600])
    facts['editorSubmit'] = submitted['error']
    time.sleep(2.0)
    inspect = cli('editor.inspect', {'id': editor})
    say('editor.inspect', json.dumps(inspect)[:3000])
    park()
    frame('editor-over-limit')
    cli('editor.cancel', {'id': editor})


try:
    main()
finally:
    cleanup()
