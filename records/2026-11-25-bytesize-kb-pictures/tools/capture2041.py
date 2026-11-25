#!/usr/bin/env python3
"""#2041 size-unit pictures: one capture run on m74 (Cinnamon, X11).

Run on the desktop's host with the desktop lock held (desktop_lock.py run ...). Starts a PRIVATE resident of the
build under test (own XDG folders, own runtime folder, session-only credentials) on the real display, drives it with
putgd-cli and saves uncropped frames of the whole desktop with ImageMagick `import`.

  python3 capture2041.py --build DIR --run DIR --label before|after [--offscreen]

--offscreen runs the same steps in a headless resident (QT_QPA_PLATFORM=offscreen, no frames) to check the steps
without taking the desktop.

Scenes (offline; loopback receivers and synthetic files only, no credentials):
  A  History file details for a 300-byte text file uploaded to a loopback receiver: the Size row.
  B  The editor's size-limit warning: Largest file lowered to 300,000 bytes, a noisy JPEG opened in the editor, Upload.
"""
import argparse
import http.server
import json
import os
import signal
import subprocess
import threading
import time
from pathlib import Path

from PIL import Image

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--build', required=True)
parser.add_argument('--run', required=True)
parser.add_argument('--label', required=True, choices=['before', 'after'])
parser.add_argument('--offscreen', action='store_true')
options = parser.parse_args()

HOME = Path.home()
BUILD = Path(options.build).resolve()
R = Path(options.run).resolve()
LABEL = options.label
OFFSCREEN = options.offscreen
FRAMES = R / 'frames'
UID = os.getuid()
RT = Path('/run/user/%d/pg2041' % UID)
for folder in (R, FRAMES, R / 'keep', R / 'cfg', R / 'data', R / 'state', R / 'cache', R / 'own'):
    folder.mkdir(parents=True, exist_ok=True)
os.chmod(R, 0o700)
RT.mkdir(mode=0o700, exist_ok=True)
sock = str(RT / 'putgd/session.sock')
assert len(sock.encode()) <= 107, sock
BUS = 'unix:path=/run/user/%d/bus' % UID
base = dict(XDG_CONFIG_HOME=str(R / 'cfg'), XDG_DATA_HOME=str(R / 'data'), XDG_STATE_HOME=str(R / 'state'), XDG_CACHE_HOME=str(R / 'cache'), XDG_RUNTIME_DIR=str(RT))
if OFFSCREEN:
    ENV = dict(os.environ, QT_QPA_PLATFORM='offscreen', **base)
    ENV.pop('DISPLAY', None)
else:
    ENV = dict(os.environ, DISPLAY=':0', XAUTHORITY=str(HOME / '.Xauthority'), DBUS_SESSION_BUS_ADDRESS=BUS, XDG_SESSION_TYPE='x11', XDG_CURRENT_DESKTOP='X-Cinnamon', **base)
XENV = dict(os.environ, DISPLAY=':0', XAUTHORITY=str(HOME / '.Xauthority'), DBUS_SESSION_BUS_ADDRESS=BUS)
log = open(R / 'capture2041.log', 'a')
facts = {'label': LABEL, 'offscreen': OFFSCREEN, 'frames': {}}


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


def put_windows():
    """Every visible window of this run's put.gd UI process: [(id, name, geometry)]."""
    if OFFSCREEN:
        return []
    ids = set()
    for pid in ui_pids():
        ids.update(x('xdotool', 'search', '--onlyvisible', '--pid', str(pid)).split())
    found = []
    for window in sorted(ids):
        g = geometry(window)
        if g and g[2] > 100 and g[3] > 60:
            found.append((window, x('xdotool', 'getwindowname', window), g))
    return found


def frame(name):
    if OFFSCREEN:
        return None
    path = FRAMES / ('%s-%s-full.png' % (LABEL, name))
    time.sleep(0.6)
    subprocess.run(['import', '-window', 'root', str(path)], env=XENV)
    facts['frames'][name] = [{'id': w, 'name': n, 'geometry': g} for w, n, g in put_windows()]
    say('frame', path.name, Image.open(path).size, facts['frames'][name])
    return path


def park():
    if not OFFSCREEN:
        x('xdotool', 'mousemove', '1900', '500')


def place(window, left, top, width, height):
    x('xdotool', 'windowactivate', window)
    x('xdotool', 'windowsize', window, str(width), str(height))
    x('xdotool', 'windowmove', window, str(left), str(top))
    time.sleep(1.0)


procs = {}
servers = []


class Receiver(http.server.BaseHTTPRequestHandler):
    """A loopback receiver that accepts an upload and answers with a link."""

    def do_POST(self):
        length = int(self.headers.get('Content-Length') or 0)
        self.rfile.read(length)
        port = self.server.server_address[1]
        body = json.dumps({'files': [{'url': 'http://127.0.0.1:%d/f/synthetic' % port, 'delete': 'http://127.0.0.1:%d/d/synthetic' % port}]}).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        facts['received'] = facts.get('received', 0) + 1

    def log_message(self, *args):
        pass


def receiver():
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Receiver)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    servers.append(server)
    return server.server_address[1]


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


def noisy_jpeg(name):
    path = (R / 'own' / name).with_suffix('.jpg')
    Image.frombytes('RGB', (640, 400), os.urandom(640 * 400 * 3)).save(path, quality=30)  # about 200 KB as a JPEG, over 700 KB once exported as PNG
    return path


def upload(profile, path):
    return until(lambda: (lambda reply: reply if reply['ok'] or reply['error'].get('code') != 'initializing' else None)(cli('upload.files', {'paths': [str(path)], 'profileId': profile})), 20, 0.5)


def cleanup():
    cli('ui.quit')
    time.sleep(1.5)
    for server in servers:
        server.shutdown()
        server.server_close()
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
    (RT / 'putgd').mkdir(exist_ok=True)
    (RT / 'putgd/session.sock').unlink(missing_ok=True)
    procs['resident'] = subprocess.Popen([str(BUILD / 'putgd'), '--background'], env=ENV, stdout=open(R / 'resident.log', 'w'), stderr=subprocess.STDOUT)
    facts['residentPid'] = procs['resident'].pid
    assert until(lambda: (RT / 'putgd/session.sock').exists(), 20), 'resident did not start'
    time.sleep(5)
    document = cli('settings.get')['result']['document']
    actions = {name: dict(action, shortcut='') for name, action in document['actions'].items()}
    patch = {'actions': actions, 'archive': dict(document['archive'], keepUploads=True, root=str(R / 'keep'))}
    if 'updates' in document.get('preferences', {}):
        patch['preferences'] = {'updates': dict(document['preferences']['updates'], check=False)}
    patched = cli('settings.patch', {'patch': patch, 'expectedRevision': revision()})
    say('patched', patched['ok'], patched['error'].get('code'), patched['error'].get('message', ''))
    add_destination('lab-ok', 'http://127.0.0.1:%d/upload' % receiver())

    # Scene A: History file details of a 300-byte text file.
    tiny = R / 'own' / 'note-300-bytes.txt'
    text = ('put.gd #2041 synthetic note. ' * 12)[:300]
    tiny.write_text(text)
    assert tiny.stat().st_size == 300, tiny.stat().st_size
    facts['tinyBytes'] = tiny.stat().st_size
    sent = upload('lab-ok', tiny)
    say('upload.files', sent['ok'], sent['error'], json.dumps(sent['result'])[:300])
    op = sent['result'].get('operationId')
    done = until(lambda: cli('operation.inspect', {'id': op})['result'].get('state') in ('completed', 'partial', 'failed', 'cancelled', 'interrupted') and cli('operation.inspect', {'id': op})['result']['state'], 40)
    say('operation state', done)
    facts['operationState'] = done
    shown = cli('ui.show', {'view': 'history'})
    say('ui.show history', shown['ok'], shown['error'])
    time.sleep(3.0)
    inspect = cli('ui.history', {'action': 'inspect'})
    say('ui.history inspect', json.dumps(inspect)[:3000])
    windows = put_windows()
    say('windows', windows)
    if windows:
        place(windows[0][0], 120, 20, 1240, 1000)
    listed = cli('history.list', {'limit': 10})
    say('history.list', json.dumps(listed)[:1500])
    items = listed['result'].get('records') or []
    ids = [item.get('id') for item in items if item.get('id')]
    say('row ids', ids)
    if ids:
        say('select', json.dumps(cli('ui.history', {'action': 'select', 'ids': ids[:1]}))[:300])
        say('openDetails', json.dumps(cli('ui.history', {'action': 'openDetails'}))[:300])
    time.sleep(2.0)
    inspect = cli('ui.history', {'action': 'inspect'})
    say('ui.history inspect 2', json.dumps(inspect)[:4000])
    facts['historyState'] = {key: inspect['result'].get(key) for key in ('detailsOpen', 'detailsWanted', 'layout', 'selectedIds', 'rows')}
    park()
    frame('history-details')

    # Scene B: the editor, edited image over the Largest file limit.
    limits = cli('settings.get')['result']['document']['limits']
    patched = cli('settings.patch', {'patch': {'limits': dict(limits, maxFileBytes=300000)}, 'expectedRevision': revision()})
    say('limit lowered', patched['ok'], patched['error'].get('code'), patched['error'].get('message'))
    source = noisy_jpeg('noisy')
    facts['editorSourceBytes'] = source.stat().st_size
    opened = cli('editor.open', {'source': 'file', 'path': str(source)})
    say('editor.open', opened['ok'], opened['error'])
    editor = opened['result'].get('operationId')
    time.sleep(3.0)
    say('editor windows', put_windows())
    submitted = cli('editor.submit', {'id': editor})
    say('editor.submit', submitted['ok'], submitted['error'], json.dumps(submitted['result'])[:600])
    time.sleep(2.0)
    inspect = cli('editor.inspect', {'id': editor})
    say('editor.inspect', json.dumps(inspect)[:3000])
    facts['editorNotice'] = inspect['result']
    park()
    frame('editor-over-limit')
    cli('editor.cancel', {'id': editor})


try:
    main()
finally:
    cleanup()
