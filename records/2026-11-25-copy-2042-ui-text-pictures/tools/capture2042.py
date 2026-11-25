#!/usr/bin/env python3
"""#2042 UI wording pictures: one capture run on m74 (Cinnamon, X11).

Run on the desktop's host with the desktop lock held (desktop_lock.py run ...). Starts a PRIVATE resident of
the build under test (own XDG folders, own runtime folder) on the real display, drives it with putgd-cli
and xdotool, and saves uncropped frames of the whole desktop with ImageMagick `import`.

  python3 capture2042.py --build DIR --run DIR --label before|after [--scenes history,editor,scroll]

Scenes (offline; a loopback receiver, synthetic images and a text file the run writes; no credentials):
  history  One synthetic upload to a loopback receiver, then History: the window title, and the "Delete from
           destination" confirmation (ui.history deleteSelected).
  editor   The image editor with a mark on a synthetic image and the Blur tool chosen (its warning and the
           Switch to Redact button), the Upload button's tooltip, and the Discard edits confirmation.
  scroll   A scrolling capture of a text file in xed (a window this run opens): the bar waiting, Paused (mouse
           moved) and the Auto-scroll tooltip.
"""
import argparse
import http.server
import json
import subprocess
import sys
import threading
import time
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib2042  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument('--build', required=True)
parser.add_argument('--run', required=True)
parser.add_argument('--label', required=True, choices=['before', 'after'])
parser.add_argument('--scenes', default='history,editor,scroll')
parser.add_argument('--probe', action='store_true', help='also save a frame at each step of the editor scene')
options = parser.parse_args()
R = lib2042.Run(options.build, options.run, options.label)
say = R.say
HOVER = Path.home() / 'work/c2042/hover.json'
OWN = R.run / 'own'
OWN.mkdir(exist_ok=True)
servers = []
children = []
state = {'port': 0}


class Receiver(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length') or 0)
        remaining = length
        while remaining > 0:
            chunk = self.rfile.read(min(65536, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
        base = 'http://127.0.0.1:%d' % state['port']
        body = json.dumps({'files': [{'url': base + '/f/synthetic.png', 'delete': base + '/d/synthetic'}]}).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_DELETE(self):
        self.send_response(200)
        self.send_header('Content-Length', '0')
        self.end_headers()

    def log_message(self, *args):
        pass


def receiver():
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Receiver)
    state['port'] = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    servers.append(server)
    return state['port']


def revision():
    return R.cli('settings.get')['result']['metadata']['observedRevision']


def sxcu(name, url):
    path = OWN / (name + '.sxcu')
    path.write_text(json.dumps({'Version': '17.0.0', 'Name': name, 'DestinationType': 'ImageUploader, FileUploader', 'RequestMethod': 'POST', 'RequestURL': url,
                                'Headers': {'Authorization': 'Bearer putgd-synthetic-uploader-token-not-real'}, 'Body': 'MultipartFormData', 'FileFormName': 'file',
                                'URL': '{json:files[0].url}', 'DeletionURL': '{json:files[0].delete}'}))
    path.chmod(0o600)
    return path


def add_destination(profile, url):
    added = R.cli('settings.importUploader', {'path': str(sxcu(profile, url)), 'expectedRevision': revision(), 'profileId': profile, 'credentialMode': 'session', 'allowInsecureHttp': False})
    say('destination', profile, url, added['ok'], added['error'].get('code'), added['error'].get('message', ''))
    assert added['ok'], added


def picture(name, size=(640, 400)):
    image = Image.new('RGB', size, (52, 84, 140))
    draw = ImageDraw.Draw(image)
    for i in range(0, size[1], 40):
        draw.rectangle((0, i, size[0], i + 20), fill=(60 + i % 90, 96, 150))
    draw.text((28, 28), 'put.gd #2042 synthetic picture', fill=(255, 255, 255))
    draw.text((28, 60), 'Not a real screenshot: no private data.', fill=(255, 255, 255))
    path = OWN / name
    image.save(path)
    return path


def find(substr, windows=None):
    for w, n, g in (windows if windows is not None else R.windows()):
        if substr in n:
            return w, n, g
    return None


def scene_history():
    say('--- scene history')
    port = receiver()
    add_destination('lab-receiver', 'http://127.0.0.1:%d/upload' % port)
    for n in (1, 2):
        sent = R.until(lambda: (lambda r: r if r['ok'] or r['error'].get('code') != 'initializing' else None)(
            R.cli('upload.files', {'paths': [str(picture('upload-%d.png' % n))], 'profileId': 'lab-receiver'})), 20, 0.5)
        say('upload', n, sent['ok'], sent['error'])
        R.until(lambda: len([r for r in R.cli('history.list', {'limit': 10})['result'].get('records', []) if r.get('phase') == 'uploaded']) >= n, 40)
    listed = R.cli('history.list', {'limit': 10})
    items = listed['result'].get('records') or []
    say('history.list', [(i.get('id'), i.get('name'), i.get('phase')) for i in items])
    ids = [i.get('id') for i in items if isinstance(i, dict) and i.get('id')]
    shown = R.cli('ui.show', {'view': 'history'})
    say('ui.show history', shown['ok'], shown['error'])
    time.sleep(3.0)
    win = R.until(lambda: next((w for w in R.windows() if w[1] == 'put.gd'), None), 15)
    say('main window', win)
    if win:
        R.place(win[0], 80, 40, 1160, 760)
    time.sleep(1.5)
    if ids:
        say('select', json.dumps(R.cli('ui.history', {'action': 'select', 'ids': ids[:2]}))[:300])
    time.sleep(1.0)
    R.park()
    R.frame('history-list')
    deleted = R.cli('ui.history', {'action': 'deleteSelected'})
    say('deleteSelected', deleted['ok'], deleted['error'], json.dumps(deleted['result'])[:600])
    time.sleep(2.0)
    R.park()
    R.frame('history-delete-dialog')
    say('cancelConfirmation', R.cli('ui.history', {'action': 'cancelConfirmation'})['ok'])
    time.sleep(1.0)
    # Clear history: the History window's own menu has no session method; the delete confirmation is the dialog shown.
    R.cli('ui.show', {'view': 'dashboard'})


def hover_upload_candidates(editor_geom):
    left, top, width, height = editor_geom
    return left, top, width, height


def scene_editor():
    say('--- scene editor')
    # The editor's Upload tooltip names its destination: give the edit action a real one, so it does not read
    # "... to Save to the local archive".
    if 'lab-receiver' not in json.dumps(R.cli('settings.get')['result']['document'].get('destinations', R.cli('settings.get')['result']['document'])):
        add_destination('lab-receiver', 'http://127.0.0.1:%d/upload' % (state['port'] or receiver()))
    document = R.cli('settings.get')['result']['document']
    actions = {name: dict(action) for name, action in document['actions'].items()}
    actions['edit'] = dict(actions['edit'], destination='upload', profileId='lab-receiver')
    patched = R.cli('settings.patch', {'patch': {'actions': actions}, 'expectedRevision': revision()})
    say('edit action destination', patched['ok'], patched['error'].get('code'), patched['error'].get('message', ''))
    source = picture('editor-source.png', (760, 460))
    opened = R.cli('editor.open', {'source': 'file', 'path': str(source)})
    say('editor.open', opened['ok'], opened['error'])
    editor = opened['result'].get('operationId')
    time.sleep(3.0)
    win = R.until(lambda: find('Edit image') or find('put.gd'), 15)
    say('editor window', win, R.windows())
    ew = None
    for w, n, g in R.windows():
        if g[2] > 600:
            ew = (w, n, g)
    if ew:
        R.place(ew[0], 60, 30, 1280, 900)
    time.sleep(1.5)
    applied = R.cli('editor.apply', {'id': editor, 'commands': [{'op': 'add', 'shape': {'kind': 'rectangle', 'rect': [60, 120, 300, 90], 'color': '#D7263D', 'width': 4}}]})
    say('editor.apply', applied['ok'], applied['error'])
    chosen = R.cli('editor.view', {'id': editor, 'action': 'tool', 'tool': 'blur'})
    say('tool blur', chosen['ok'], chosen['error'], json.dumps(chosen['result'])[:500])
    time.sleep(1.5)
    R.park()
    R.frame('editor-blur')
    say('editor windows', R.windows())
    # Upload tooltip: the pointer must come to rest over the Upload button.
    pos = json.loads(HOVER.read_text()) if HOVER.exists() else None
    if pos:
        R.hover(pos['upload'][0], pos['upload'][1], wait=2.6)
        R.frame('editor-upload-tooltip', settle=0.3)
        R.park()
        time.sleep(0.8)
    discard = R.cli('editor.view', {'id': editor, 'action': 'discard'})
    say('discard', discard['ok'], discard['error'])
    time.sleep(2.0)
    R.park()
    R.frame('editor-discard-dialog')
    say('windows with dialog', R.windows())
    R.cli('editor.view', {'id': editor, 'action': 'keepEditing'})
    time.sleep(0.8)
    R.cli('editor.cancel', {'id': editor})
    time.sleep(1.5)


def scene_scroll():
    say('--- scene scroll')
    text = OWN / 'long.txt'
    text.write_text(''.join('put.gd #2042 synthetic line %04d: the quick brown fox jumps over the lazy dog\n' % i for i in range(1, 3001)))
    xed = subprocess.Popen(['xed', '--standalone', str(text)], env=R.xenv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    children.append(xed)
    time.sleep(5.0)
    ids = R.x('xdotool', 'search', '--onlyvisible', '--pid', str(xed.pid)).split()
    say('xed windows', ids)
    if not ids:
        say('xed has no window of its own pid; falling back to the newest xed window by name')
        ids = R.x('xdotool', 'search', '--onlyvisible', '--name', 'long.txt').split()
    window = ids[-1]
    R.place(window, 120, 80, 900, 760)
    R.x('xdotool', 'windowactivate', window)
    time.sleep(1.0)
    geometry = R.geometry(window)
    say('xed geometry', geometry)
    rect = [geometry[0] + 20, geometry[1] + 90, geometry[2] - 40, geometry[3] - 140]
    prepared = R.cli('scroll.prepare', {'rect': rect, 'driver': 'user'})
    say('scroll.prepare', prepared['ok'], prepared['error'], json.dumps(prepared['result'])[:500])
    sid = prepared['result'].get('id')
    started = R.cli('scroll.start', {'id': sid})
    say('scroll.start', started['ok'], started['error'], json.dumps(started['result'])[:400])
    time.sleep(3.0)
    R.park()
    R.frame('scroll-waiting')
    say('inspect', json.dumps(R.cli('scroll.inspect', {'id': sid})['result'])[:500])
    auto = R.cli('scroll.autoScroll', {'id': sid, 'on': True})
    say('scroll.autoScroll', auto['ok'], auto['error'], json.dumps(auto['result'])[:300])
    time.sleep(2.5)
    R.frame('scroll-autoscrolling')
    # The pointer moves: auto-scroll pauses by itself.
    for i in range(6):
        R.x('xdotool', 'mousemove', str(1500 + i * 25), str(300 + i * 10))
        time.sleep(0.15)
    time.sleep(1.2)
    inspect = R.cli('scroll.inspect', {'id': sid})
    say('inspect after mouse', json.dumps(inspect['result'])[:600])
    R.frame('scroll-paused-mouse')
    say('windows', R.windows())
    pos = json.loads(HOVER.read_text()) if HOVER.exists() else None
    if pos and 'autoscroll' in pos:
        R.hover(pos['autoscroll'][0], pos['autoscroll'][1], wait=2.6)
        R.frame('scroll-autoscroll-tooltip', settle=0.3)
    R.cli('scroll.cancel', {'id': sid})
    time.sleep(1.5)


def main():
    R.start()
    scenes = options.scenes.split(',')
    for name, fn in (('history', scene_history), ('editor', scene_editor), ('scroll', scene_scroll)):
        if name in scenes:
            try:
                fn()
            except Exception as problem:  # keep the other scenes; the log says what happened
                say('SCENE FAILED', name, repr(problem))
                R.facts.setdefault('failed', []).append(name)


try:
    main()
finally:
    for child in children:
        if child.poll() is None:
            child.terminate()
            try:
                child.wait(8)
            except subprocess.TimeoutExpired:
                child.kill()
    for server in servers:
        server.shutdown()
    R.cleanup()
