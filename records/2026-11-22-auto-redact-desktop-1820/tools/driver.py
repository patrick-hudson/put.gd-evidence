"""#1820 acceptance controller: a private put.gd resident on the real desktop, a loopback
HTTP receiver that keeps every uploaded object, a fullscreen fixture viewer and RFB
frames/input. Commands arrive as JSON lines on a Unix socket (dc.py is the client).
Adapted from the #1806 record's driver. Synthetic test values only."""
import argparse
import contextlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import traceback

from rfb import RFB
from text_proof import Input, session_environment

DONE = {'completed', 'failed', 'cancelled', 'partial'}


class Receiver(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_POST(self):
        if self.path != '/upload':
            return self.send_error(404)
        data = self.rfile.read(int(self.headers['Content-Length']))
        with self.server.lock:
            index = len(self.server.objects) + 1
            self.server.objects[index] = data
        (self.server.store / f'object-{index:04d}.bin').write_bytes(data)
        body = json.dumps({'url': f'{self.server.origin}/image/{index}'}).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        match = re.fullmatch(r'/image/(\d+)', self.path)
        data = self.server.objects.get(int(match[1])) if match else None
        if data is None:
            return self.send_error(404)
        self.send_response(200)
        self.send_header('Content-Type', 'application/octet-stream')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class Run:
    def __init__(self, args, stack):
        self.args, self.stack = args, stack
        self.root = args.root.resolve()
        self.out = self.root / 'out'
        self.out.mkdir(exist_ok=True)
        self.session, leader = session_environment(args.leader)
        self.session.setdefault('DBUS_SESSION_BUS_ADDRESS', f'unix:path={self.session["XDG_RUNTIME_DIR"]}/bus')
        try:
            manager = subprocess.check_output(['systemctl', '--user', 'show-environment'], env=self.session, text=True)
        except subprocess.CalledProcessError:
            manager = ''
        for line in manager.splitlines():
            name, _, value = line.partition('=')
            if name in ('WAYLAND_DISPLAY', 'XAUTHORITY', 'XDG_SESSION_TYPE', 'DISPLAY') and not self.session.get(name):
                self.session[name] = value
        if self.session.get('XDG_SESSION_TYPE') == 'x11':
            self.session.pop('WAYLAND_DISPLAY', None)
            self.session['QT_QPA_PLATFORM'] = 'xcb'
        runtime = self.root / 'r'
        socket_paths = [runtime / 'putgd/session.sock', self.root / 'c.sock']
        real_runtime = Path(self.session['XDG_RUNTIME_DIR'])
        if self.session.get('WAYLAND_DISPLAY') and args.private_runtime:
            socket_paths.append(real_runtime / self.session['WAYLAND_DISPLAY'])
        for path in socket_paths:
            size = len(os.fsencode(path.resolve()))
            if size > 107:
                raise RuntimeError(f'Unix socket path {path} is {size} bytes')
        if args.private_runtime:
            self.socket = socket_paths[0]
            runtime.mkdir(mode=0o700, exist_ok=True)
            self.private = dict(self.session, XDG_RUNTIME_DIR=str(runtime))
            if self.session.get('WAYLAND_DISPLAY'):
                self.private['WAYLAND_DISPLAY'] = str(real_runtime / self.session['WAYLAND_DISPLAY'])
        else:
            # Hyprland and other compositors whose IPC lives in the real runtime directory.
            self.socket = real_runtime / 'putgd/session.sock'
            self.private = dict(self.session)
        for folder in ('CONFIG', 'DATA', 'STATE', 'CACHE'):
            self.private[f'XDG_{folder}_HOME'] = str(self.root / folder.lower())
        self.record = {'leader': leader, 'session': self.session.get('XDG_SESSION_TYPE'),
                       'socketBytes': {str(p): len(os.fsencode(p)) for p in [self.socket, self.root / 'c.sock']}, 'checks': []}
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Receiver)
        self.server.origin = f'http://127.0.0.1:{self.server.server_port}'
        self.server.objects = {}
        self.server.lock = threading.Lock()
        self.server.store = self.root / 'received'
        self.server.store.mkdir(exist_ok=True)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        stack.callback(self.server.server_close)
        stack.callback(self.server.shutdown)
        self.rfb = None
        self.input = None
        self.viewer = None
        self.save()

    def save(self):
        (self.root / 'receipt.json').write_text(json.dumps(self.record, indent=1))

    def spawn(self, argv, label, env):
        with (self.root / (label + '.log')).open('a') as log:
            process = subprocess.Popen(argv, env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        self.record.setdefault('pids', {})[label] = process.pid
        self.save()
        self.stack.callback(self.stop, process)
        return process

    @staticmethod
    def stop(process):
        if process.poll() is None:
            os.kill(process.pid, signal.SIGTERM)
            try:
                process.wait(5)
            except subprocess.TimeoutExpired:
                os.kill(process.pid, signal.SIGKILL)
                process.wait(5)

    def cli(self, name, params=None, allow_error=False, timeout=60):
        proc = subprocess.run([*shlex.split(self.args.cli), '--socket', str(self.socket), '--params-stdin', name],
                              env=self.private, input=json.dumps(params or {}), text=True, capture_output=True, timeout=timeout)
        try:
            reply = json.loads(proc.stdout)
        except ValueError:
            if allow_error:
                return None
            raise RuntimeError(f'{name}: no JSON reply: {proc.stdout[-300:]} {proc.stderr[-300:]}')
        if not reply['ok']:
            if allow_error:
                return None
            raise RuntimeError(f'{name}: {reply["error"]}')
        return reply['result']

    def cli_raw(self, name, params=None):
        proc = subprocess.run([*shlex.split(self.args.cli), '--socket', str(self.socket), '--params-stdin', name],
                              env=self.private, input=json.dumps(params or {}), text=True, capture_output=True, timeout=60)
        return json.loads(proc.stdout)

    def wait(self, what, predicate, seconds=30, period=.1):
        limit = time.monotonic() + seconds
        while time.monotonic() < limit:
            result = predicate()
            if result:
                return result
            time.sleep(period)
        raise RuntimeError(f'Timed out waiting for {what}')

    def patch(self, document):
        revision = self.cli('settings.get')['metadata']['observedRevision']
        return self.cli('settings.patch', {'patch': document, 'expectedRevision': revision})

    # -- setup -------------------------------------------------------------
    def start(self, notifications=True):
        self.resident = self.spawn([*shlex.split(self.args.app), '--background'], 'resident', self.private)
        self.wait('resident socket', self.socket.exists, 40)
        build = self.wait('resident diagnostics', lambda: self.cli('diagnostics', allow_error=True), 40)['build']
        self.record['build'] = build
        self.save()
        if build['gitTree'] != self.args.tree:
            raise RuntimeError(f'wrong build {build}')
        caps = self.cli('capabilities')
        self.record['source'] = caps.get('source')
        self.record['text'] = caps.get('text')
        settings = self.cli('settings.get')
        sxcu = self.root / 'receiver.sxcu'
        sxcu.write_text(json.dumps({'Version': '17.0.0', 'Name': 'Isolated HTTP receiver', 'DestinationType': 'ImageUploader, FileUploader',
                                    'RequestMethod': 'POST', 'RequestURL': self.server.origin + '/upload', 'Body': 'Binary', 'URL': '{json:url}'}))
        self.cli('settings.importUploader', {'path': str(sxcu), 'profileId': 'lab1820', 'credentialMode': 'session',
                                             'expectedRevision': settings['metadata']['observedRevision'], 'allowInsecureHttp': True})
        self.patch({'archive': {'keepUploads': True, 'root': str(self.root / 'archive')},
                    'preferences': {'notifications': notifications, 'launchAtLogin': False, 'textRecognitionLanguages': ['eng'],
                                    'fileManagerMenu': False, 'quickRedactTerms': ['Project Aurora', 'acme-build-7'],
                                    'quickRedactPatterns': ['\\bJIRA-\\d+\\b']},
                    'captureDefaults': {'destination': 'upload', 'profileId': 'lab1820', 'publicationMode': 'default'},
                    'actions': {action: {'destination': 'upload', 'profileId': 'lab1820',
                                         'shortcut': {'region': 'Ctrl+Shift+F9', 'monitor': 'Ctrl+Shift+F10'}.get(action, '')}
                                for action in ('region', 'desktop', 'monitor', 'window', 'clipboard', 'edit', 'scroll')}})
        if self.args.vnc:
            self.rfb = RFB(self.args.vnc)
            self.stack.callback(self.rfb.sock.close)
            self.width, self.height = self.rfb.width, self.rfb.height
        else:
            self.width, self.height = self.args.size
        self.record['screen'] = [self.width, self.height]
        if self.args.input:
            self.input = Input(self.args.input, self.width, self.height)
        self.control = self.root / 'viewer.json'
        self.control.write_text(json.dumps({'path': '', 'fullscreen': False}))
        self.viewer = self.spawn(['/usr/bin/python3', str(Path(__file__).with_name('viewer.py')), str(self.control)], 'viewer', self.session)
        self.save()
        return {'screen': self.record['screen'], 'adapter': (self.record['source'] or {}).get('adapter'),
                'ocr': (self.record['text'] or {}).get('available'), 'build': build}

    def kinds(self, kinds, enabled=True, **prefs):
        doc = {'preferences': {'sensitiveTextCheck': {'enabled': enabled, 'kinds': kinds}, **prefs}}
        self.patch(doc)
        value = self.cli('settings.get')['document']['preferences']
        return {'sensitiveTextCheck': value.get('sensitiveTextCheck'), 'languages': value.get('textRecognitionLanguages')}

    def prefs(self, document):
        self.patch(document)
        return True

    # -- fixture -----------------------------------------------------------
    def show(self, path, fullscreen=True, check=True):
        self.control.write_text(json.dumps({'path': str(Path(path).resolve()) if path else '', 'fullscreen': fullscreen, 'n': time.time()}))
        time.sleep(.8)
        if check and path and self.rfb:
            from PIL import Image
            want = Image.open(path).convert('RGB')
            pts = [(7, 7), (want.width // 2, want.height // 2), (want.width - 9, want.height - 9), (want.width // 3, 31), (31, want.height // 3)]
            def visible():
                w, h, px = self.rfb.frame()
                for x, y in pts:
                    i = 4 * (y * w + x)
                    got = (px[i + 2], px[i + 1], px[i])
                    if max(abs(a - b) for a, b in zip(got, want.getpixel((x, y)))) > 2:
                        return False
                return True
            self.wait('fixture visible fullscreen', visible, 12, .3)
        return True

    def window(self, argv, label='app', settle=2.0):
        proc = self.spawn(argv, label, self.session)
        time.sleep(settle)
        return proc.pid

    def kill(self, pid):
        with contextlib.suppress(ProcessLookupError):
            os.kill(int(pid), signal.SIGTERM)
        return True

    # -- input and frames ----------------------------------------------------
    def shot(self, name):
        filename = self.out / (name + '.png')
        time.sleep(.3)
        self.rfb.frame()
        self.rfb.screenshot(filename)
        return str(filename)

    def key(self, *keys):
        if self.input:
            self.input.chord(keys)
        else:
            self.rfb.key(*keys)
        return True

    def type(self, text):
        self.rfb.type(text)
        return True

    def move(self, x, y):
        if self.input:
            self.input.move(int(x), int(y))
        else:
            self.rfb.pointer(int(x), int(y))
        return True

    def click(self, x, y, button='left'):
        if button != 'left':
            self.rfb.pointer_button(int(x), int(y), button, True)
            time.sleep(.05)
            self.rfb.pointer_button(int(x), int(y), button, False)
        elif self.input:
            self.input.click(int(x), int(y))
        else:
            self.rfb.click(int(x), int(y))
        return True

    def scroll(self, x, y, amount):
        self.rfb.scroll(int(x), int(y), int(amount))
        return True

    def drag(self, x1, y1, x2, y2):
        if self.input:
            self.input.drag((x1, y1), (x2, y2))
        else:
            self.rfb.drag(x1, y1, x2, y2)
        return True

    # -- operations ----------------------------------------------------------
    def recent(self):
        return self.cli('operation.recent')['operations']

    def capture(self, label, action='monitor', mode='agent', region=None, pointer=None):
        before = {op['id'] for op in self.recent()}
        check = {'label': label, 'action': action, 'mode': mode, 'receiverBefore': len(self.server.objects), 'states': [], 't0': time.time()}
        self.record['checks'].append(check)
        if pointer and self.rfb:
            self.move(*pointer)
        if mode == 'hotkey':
            self.key('ctrl', 'shift', 'f9' if action == 'region' else 'f10')
            op = self.wait('new hotkey operation', lambda: next((o for o in self.recent() if o['id'] not in before), None), 10)
            check['id'] = op['id']
        else:
            params = {'action': action}
            if mode == 'prompt':
                params['sensitiveText'] = 'prompt'
            check['id'] = self.cli('action.invoke', params)['operationId']
        if action == 'region':
            time.sleep(1.0)
            self.drag(*region)
        self.save()
        return check['id']

    def inspect(self, oid):
        return self.cli('operation.inspect', {'id': oid})

    def observe(self, oid, phase='end', timeout=90):
        check = next((c for c in self.record['checks'] if c.get('id') == oid), {'states': []})
        t0 = check.get('t0', time.time())
        def state():
            value = self.inspect(oid)
            marker = [value.get('state'), value.get('phase')]
            if not check['states'] or marker != check['states'][-1][1:]:
                check['states'].append([round(time.time() - t0, 3), *marker])
            check['last'] = value
            if value.get('state') in DONE or value.get('phase') == phase:
                return value
        try:
            return self.wait(phase, state, timeout, .1)
        finally:
            self.save()

    def decide(self, oid, choice, prompt=None):
        params = {'id': oid, 'choice': choice}
        if prompt:
            params['prompt'] = prompt
        return self.cli('operation.decide', params)

    def collect(self, oid, label):
        """Save the uploaded objects, the archive copies and the original of an operation under out/label-*."""
        op = self.inspect(oid)
        saved = {'op': op, 'uploads': [], 'local': [], 'original': []}
        for n, item in enumerate(op.get('items', [])):
            link = (item.get('receipt') or {}).get('directUrl', '')
            m = re.search(r'/image/(\d+)$', link)
            if m:
                data = self.server.objects[int(m[1])]
                dest = self.out / f'{label}-upload{n}.png'
                dest.write_bytes(data)
                saved['uploads'].append(str(dest))
            local = (item.get('local') or {}).get('path')
            if local and Path(local).is_file():
                dest = self.out / f'{label}-local{n}.png'
                shutil.copyfile(local, dest)
                saved['local'].append({'from': local, 'to': str(dest)})
        for n, path in enumerate(((op.get('sensitive') or {}).get('original') or {}).get('paths', [])):
            if Path(path).is_file():
                dest = self.out / f'{label}-original{n}.png'
                shutil.copyfile(path, dest)
                saved['original'].append({'from': path, 'to': str(dest)})
        (self.out / f'{label}-op.json').write_text(json.dumps(op, indent=1))
        return {k: v for k, v in saved.items() if k != 'op'} | {'state': op.get('state'), 'sensitive': op.get('sensitive'),
                                                                'items': [{'uploadStatus': i.get('uploadStatus'), 'local': (i.get('local') or {}).get('status')} for i in op.get('items', [])]}

    def notifications(self, since=0):
        found = []
        for log in sorted(self.root.glob('state/**/*.jsonl')) + sorted(self.root.glob('state/**/*.log')):
            with contextlib.suppress(OSError):
                for line in log.read_text(errors='replace').splitlines():
                    if 'Notification shown' in line:
                        with contextlib.suppress(ValueError):
                            found.append(json.loads(line))
        found += [json.loads(l) for l in (self.root / 'resident.log').read_text(errors='replace').splitlines() if 'Notification shown' in l and l.startswith('{')]
        return found[since:]

    def logfiles(self):
        return [str(p) for p in self.root.glob('state/**/*') if p.is_file()] + [str(p) for p in self.root.glob('data/**/*.log')]

    def files(self, label, paths, mode='agent'):
        check = {'label': label, 'action': 'files', 'mode': mode, 'receiverBefore': len(self.server.objects), 'states': [], 't0': time.time()}
        self.record['checks'].append(check)
        params = {'paths': paths}
        if mode == 'prompt':
            params['sensitiveText'] = 'prompt'
        check['id'] = self.cli('upload.files', params)['operationId']
        self.save()
        return check['id']

    def objects(self):
        return len(self.server.objects)

    def ls(self, path):
        return sorted(str(p) for p in Path(path).rglob('*'))

    def note(self, label, value):
        self.record.setdefault('observations', {})[label] = value
        self.save()
        return True

    def quit(self):
        with contextlib.suppress(Exception):
            self.cli('ui.quit', allow_error=True)
            self.resident.wait(10)
        return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    parser.add_argument('--leader', nargs='+', required=True)
    parser.add_argument('--vnc', type=int)
    parser.add_argument('--size', type=int, nargs=2)
    parser.add_argument('--input')
    parser.add_argument('--tree', required=True)
    parser.add_argument('--app', default='/usr/bin/putgd')
    parser.add_argument('--cli', default='/usr/bin/putgd-cli')
    parser.add_argument('--shared-runtime', dest='private_runtime', action='store_false')
    args = parser.parse_args()
    with contextlib.ExitStack() as stack:
        run = Run(args, stack)
        stack.callback(run.quit)
        server = socket.socket(socket.AF_UNIX)
        path = run.root / 'c.sock'
        with contextlib.suppress(FileNotFoundError):
            path.unlink()
        server.bind(str(path))
        server.listen(4)
        print('listening', path, flush=True)
        while True:
            conn, _ = server.accept()
            with conn, conn.makefile('rwb') as stream:
                line = stream.readline()
                try:
                    action, *params = json.loads(line)
                    if action == 'exit':
                        stream.write(b'{"result": "bye"}\n')
                        break
                    answer = run.cli_raw(*params) if action == 'cli' else getattr(run, action)(*params)
                    stream.write(json.dumps({'result': answer}).encode() + b'\n')
                except Exception as error:
                    run.record.setdefault('errors', []).append({'command': line.decode().strip()[:400], 'error': str(error)})
                    run.save()
                    stream.write(json.dumps({'error': str(error), 'trace': traceback.format_exc()[-800:]}).encode() + b'\n')


if __name__ == '__main__':
    os.umask(0o077)
    main()
