#!/usr/bin/env python3
"""Desktop pipeline check for Copy text (put.gd issue 1428). Stdlib only.

Runs on the desktop's own host, under its desktop lock. It starts the installed
resident with private configuration and data folders in the running desktop
session, sets a hotkey for the text action, and for each trigger (the real
hotkey, the tray entry, the window button) selects a region with real pointer
input and reads the clipboard back with an independent client.

Input comes from tools/lab/host_input.py (kernel uinput devices), so the
compositor sees it as hardware input. Everything on screen during the run is a
window this script opened. Nothing recognized is written anywhere but the
clipboard and this run's receipt.
"""
import argparse, json, os, re, signal, socket, struct, subprocess, sys, tempfile, time
from pathlib import Path

SESSION_KEYS = ('DISPLAY', 'XAUTHORITY', 'WAYLAND_DISPLAY', 'XDG_RUNTIME_DIR', 'DBUS_SESSION_BUS_ADDRESS', 'XDG_CURRENT_DESKTOP',
                'XDG_SESSION_TYPE', 'XDG_SESSION_DESKTOP', 'DESKTOP_SESSION', 'KDE_FULL_SESSION', 'KDE_SESSION_VERSION',
                'XDG_SESSION_ID', 'XDG_SEAT', 'XDG_VTNR', 'LANG', 'PATH', 'HOME', 'USER', 'LOGNAME', 'SHELL', 'GDMSESSION',
                'HYPRLAND_INSTANCE_SIGNATURE', 'XDG_DATA_DIRS', 'XDG_CONFIG_DIRS', 'QT_QPA_PLATFORM')


def session_environment(leaders):
    for name in leaders:
        pids = subprocess.run(['pgrep', '-u', str(os.getuid()), '-x', name], capture_output=True, text=True).stdout.split()
        for pid in pids:
            try:
                raw = Path(f'/proc/{pid}/environ').read_bytes().split(b'\0')
            except OSError:
                continue
            found = dict(item.decode(errors='replace').split('=', 1) for item in raw if b'=' in item)
            if found.get('XDG_RUNTIME_DIR') and (found.get('DISPLAY') or found.get('WAYLAND_DISPLAY')):
                return {key: found[key] for key in SESSION_KEYS if key in found}, name
    raise SystemExit('no desktop session process found among ' + ', '.join(leaders))


class Input:
    """A client of host_input.py: QMP input-send-event, absolute pointer in pixels."""
    def __init__(self, path, width, height):
        self.width, self.height = width, height
        self.socket = socket.socket(socket.AF_UNIX); self.socket.connect(path)
        self.stream = self.socket.makefile('rwb'); self.stream.readline()
        self.call('qmp_capabilities')

    def call(self, name, arguments=None):
        request = {'execute': name}
        if arguments is not None:
            request['arguments'] = arguments
        self.stream.write(json.dumps(request).encode() + b'\n'); self.stream.flush()
        reply = json.loads(self.stream.readline())
        if 'error' in reply:
            raise RuntimeError(f'input agent refused {name}: {reply["error"]}')

    def events(self, events):
        self.call('input-send-event', {'events': events})

    def chord(self, keys):
        for key in keys:
            self.events([{'type': 'key', 'data': {'down': True, 'key': {'type': 'qcode', 'data': key}}}]); time.sleep(.04)
        for key in reversed(keys):
            self.events([{'type': 'key', 'data': {'down': False, 'key': {'type': 'qcode', 'data': key}}}]); time.sleep(.04)

    def move(self, x, y):
        self.events([{'type': 'abs', 'data': {'axis': 'x', 'value': max(0, min(32767, round(x * 32767 / (self.width - 1))))}},
                     {'type': 'abs', 'data': {'axis': 'y', 'value': max(0, min(32767, round(y * 32767 / (self.height - 1))))}}])

    def button(self, down):
        self.events([{'type': 'btn', 'data': {'down': down, 'button': 'left'}}])

    def click(self, x, y):
        self.move(x, y); time.sleep(.15); self.button(True); time.sleep(.06); self.button(False)

    def drag(self, start, end, steps=12):
        self.move(*start); time.sleep(.25); self.button(True); time.sleep(.15)
        for step in range(1, steps + 1):
            self.move(start[0] + (end[0] - start[0]) * step / steps, start[1] + (end[1] - start[1]) * step / steps); time.sleep(.03)
        time.sleep(.2); self.button(False)


class Run:
    def __init__(self, args):
        self.args = args
        self.env, self.leader = session_environment(args.leader)
        self.root = Path(tempfile.mkdtemp(prefix='tp-', dir='/tmp'))
        self.private = dict(self.env, XDG_CONFIG_HOME=str(self.root / 'config'), XDG_DATA_HOME=str(self.root / 'data'),
                            XDG_STATE_HOME=str(self.root / 'state'), XDG_CACHE_HOME=str(self.root / 'cache'))
        self.scan = [self.root]
        if os.environ.get('PUTGD_TEXT_SCALE'): self.private['PUTGD_TEXT_SCALE']=os.environ['PUTGD_TEXT_SCALE']
        runtime = self.root / 'rt'
        runtime.mkdir(mode=0o700)
        if self.env.get('WAYLAND_DISPLAY') and not self.env['WAYLAND_DISPLAY'].startswith('/'):
            self.private['WAYLAND_DISPLAY'] = str(Path(self.env['XDG_RUNTIME_DIR']) / self.env['WAYLAND_DISPLAY'])
        self.private['XDG_RUNTIME_DIR'] = str(runtime)
        if args.real_profile:  # a disposable guest: the resident runs as its user would run it
            self.private = dict(self.env)
            home = Path.home()
            self.scan = [home / '.config/putgd', home / '.local/share/putgd', home / '.local/state/putgd', home / '.cache/putgd']
        self.appimage_user_data = None
        if args.app.endswith('.AppImage') and not args.real_profile:
            data = Path.home()/'.local/share/putgd'
            if data.exists(): raise RuntimeError('Refusing to share existing app data: '+str(data))
            self.appimage_user_data = data
            self.private['XDG_DATA_HOME'] = str(Path.home()/'.local/share')
            self.scan.append(data)
        self.socket = str(Path(self.private['XDG_RUNTIME_DIR']) / 'putgd/session.sock')
        paths = [self.socket, str(Path(self.env['XDG_RUNTIME_DIR']) / 'putgd-text-proof-input.sock')]
        if args.input_socket != 'start': paths.append(str(Path(args.input_socket).resolve()))
        for path in paths:
            if len(path.encode('utf-8')) > 107: raise RuntimeError('overlong socket: ' + path)
        self.receiptSocketLengths = {p: len(p.encode('utf-8')) for p in paths}
        self.x11 = not self.env.get('WAYLAND_DISPLAY')
        self.started = []
        self.receipt = {'desktop': args.desktop, 'sessionProcess': self.leader, 'sessionType': self.env.get('XDG_SESSION_TYPE'),
                        'currentDesktop': self.env.get('XDG_CURRENT_DESKTOP'), 'hotkey': args.hotkey, 'triggers': [], 'socketPathsUtf8Bytes': self.receiptSocketLengths}

    def cli(self, method, params=None, check=True):
        result = subprocess.run([*self.args.cli.split(), '--socket', self.socket, method, json.dumps(params or {})], capture_output=True,
                                text=True, timeout=90, env=self.private)
        reply = json.loads(result.stdout)
        if check and not reply['ok']:
            raise RuntimeError(f'{method} failed: {reply["error"]["code"]}: {reply["error"]["message"]}')
        return reply

    def spawn(self, argv, **options):
        process = subprocess.Popen(argv, env=self.private, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True, **options)
        self.started.append(process); return process

    def wait(self, predicate, what, seconds=20):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            value = predicate()
            if value:
                return value
            time.sleep(.2)
        raise RuntimeError('timed out waiting for ' + what)

    # The clipboard through a client that is not put.gd.
    def copy_sentinel(self, text):
        argv = ['xclip', '-selection', 'clipboard', '-i'] if self.x11 else ['wl-copy']
        subprocess.run(argv, input=text.encode(), env=self.env, timeout=10, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def paste(self):
        argv = ['xclip', '-selection', 'clipboard', '-o'] if self.x11 else ['wl-paste', '-n']
        result = subprocess.run(argv, env=self.env, capture_output=True, timeout=10)
        return result.stdout.decode(errors='replace')

    def text_operation(self):
        for operation in self.cli('operation.recent')['result'].get('operations', []):
            if operation.get('action') == 'text' and operation.get('state') in ('accepted', 'acquiring', 'recognizing'):
                return operation['id']
        return None

    def trigger(self, name, start):
        entry = {'trigger': name}
        self.receipt['triggers'].append(entry)
        sentinel = f'sentinel-{name}-{int(time.time())}'
        self.input.click(self.args.screen[0]//2,self.args.screen[1]//2)
        time.sleep(.3)
        self.copy_sentinel(sentinel); time.sleep(.5)
        entry['clipboardBefore'] = self.paste()
        start()
        operation = self.wait(self.text_operation, f'a text operation after the {name} trigger')
        entry['operationId'] = operation
        self.wait(lambda: self.cli('text.inspect', {'id': operation})['result'].get('state') == 'acquiring', 'the selector')
        time.sleep(1.0)
        if not self.x11 and self.args.rfb != 'none':
            subprocess.run([sys.executable, self.args.rfb, str(self.args.rfb_port), str(self.root / f'selector-{name}.png')], timeout=60, check=True)
        if self.args.frame and self.x11:
            subprocess.run(['import', '-window', 'root', str(self.root / f'selector-{name}.png')], env=self.env, timeout=30)
            entry['selectorFrame'] = str(self.root / f'selector-{name}.png')
        a, b = self.args.region[:2], self.args.region[2:]
        self.input.drag(a, b)
        record = self.wait(lambda: (lambda r: r if r.get('state') in ('completed', 'failed', 'cancelled') else None)(
            self.cli('text.inspect', {'id': operation})['result']), 'the text operation to end', 40)
        entry['record'] = {key: record.get(key) for key in ('state', 'source', 'characterCount', 'codeCount', 'copyStatus', 'timings', 'error',
                                                            'truncated', 'banded', 'languagesUsed', 'languagesSkipped')}
        time.sleep(.5)
        entry['paste'] = self.paste()
        entry['helperProcessesAfter'] = subprocess.run(['pgrep','-x','putgd-ocr'],capture_output=True,text=True).stdout.split()
        entry['helperAbsentAfter'] = not entry['helperProcessesAfter']
        match = re.fullmatch(self.args.expect, entry['paste'], re.S)
        entry['pasteMatches'] = bool(match)
        entry['passed'] = bool(match) and record.get('state') == 'completed' and record.get('copyStatus') == 'copied' and entry['clipboardBefore'] == sentinel
        print(json.dumps(entry), flush=True)
        time.sleep(1.0)
        return entry['passed']

    def resident_pid(self):
        for pid in subprocess.run(['pgrep', '-u', str(os.getuid()), '-x', 'putgd'], capture_output=True, text=True).stdout.split():
            try:
                if ('XDG_CONFIG_HOME=' + self.private['XDG_CONFIG_HOME']).encode() in Path(f'/proc/{pid}/environ').read_bytes().split(b'\0'):
                    return int(pid)
            except OSError:
                pass
        raise RuntimeError('the private resident process was not found')

    def memory(self, pid):
        values = {}
        for line in Path(f'/proc/{pid}/smaps_rollup').read_text().splitlines():
            parts = line.split()
            if parts and parts[0] in ('Rss:', 'Pss:', 'Pss_Anon:', 'Pss_File:', 'Private_Dirty:'):
                values[parts[0][:-1] + 'Kb'] = int(parts[1])
        return values

    def first_light_before(self):
        light = self.receipt['firstLight'] = {}
        self.resident = self.resident_pid()
        try:
            light['helper'] = subprocess.run([str(Path(self.args.app).parent / 'putgd-ocr'), '--version'], capture_output=True, text=True, timeout=20,
                                             stdin=subprocess.DEVNULL).stdout.strip()
        except (OSError, subprocess.SubprocessError) as error:
            light['helper'] = 'not answered: ' + str(error)
        self.watch_log = self.root / 'helper-runs.jsonl'
        self.watcher = subprocess.Popen(['sudo', '-n', 'python3', '-I', self.args.helper_watch, str(self.watch_log)])
        time.sleep(self.args.settle)
        light['residentPid'] = self.resident
        light['residentBefore'] = self.memory(self.resident)

    def first_light_after(self, ended):
        light = self.receipt['firstLight']
        light['residentRightAfter'] = self.memory(self.resident)
        time.sleep(1)
        light['secondsAfter'] = round(time.monotonic() - ended)
        light['residentAfter'] = self.memory(self.resident)
        mapped = sorted({line.split(None, 5)[5].strip() for line in Path(f'/proc/{self.resident}/maps').read_text().splitlines() if len(line.split(None, 5)) == 6 and line.split(None, 5)[5].startswith('/')})
        light['mappedFiles'] = mapped
        forbidden = ('libtesseract', 'libleptonica', 'liblept', 'libZXing', 'libcurl', 'libarchive')
        light['forbiddenMapped'] = [path for path in mapped if any(word.lower() in path.lower() for word in forbidden)]
        light['libgompMapped'] = [path for path in mapped if 'libgomp' in path]
        subprocess.run(['sudo', '-n', 'kill', str(self.watcher.pid)]); self.watcher.wait(10)
        light['helperRuns'] = [json.loads(line) for line in self.watch_log.read_text().splitlines()][1:]
        light['helperProcessesNow'] = subprocess.run(['pgrep', '-x', 'putgd-ocr'], capture_output=True, text=True).stdout.split()
        ours = [run for run in light['helperRuns'] if run.get('parent') == self.resident]
        light['helperRunsOfThisResident'] = len(ours)
        self.receipt['passed'] = self.receipt['passed'] and not light['forbiddenMapped'] and not light['helperProcessesNow'] and all(
            run.get('exitCode') == 0 and run.get('exitSignal') == 0 for run in ours) and bool(ours)
        print(json.dumps({'firstLight': {key: light[key] for key in light if key != 'mappedFiles'}}), flush=True)

    def region_capture(self, action, rect):
        """One region capture (or Repeat last region) kept as a local copy; returns its state and the picture's size."""
        active = ('accepted', 'acquiring', 'stored', 'running', 'editing', 'recording', 'recognizing')
        operation = self.cli('action.invoke', {'action': action})['result']['operationId']
        if rect:
            self.wait(lambda: self.cli('operation.inspect', {'id': operation})['result'].get('state') != 'accepted', 'the region selector'); time.sleep(1.5)
            self.input.drag(rect[:2], rect[2:])
        record = self.wait(lambda: (lambda r: r if r.get('state') not in active else None)(self.cli('operation.inspect', {'id': operation})['result']), f'the {action} capture to end', 40)
        paths = [item.get('local', {}).get('path') for item in record.get('items', [])]
        size = None
        if paths and paths[0] and Path(paths[0]).is_file():
            size = list(struct.unpack('>II', Path(paths[0]).read_bytes()[16:24]))
        time.sleep(1.0)
        return {'action': action, 'rect': rect, 'state': record.get('state'), 'error': (record.get('error') or {}).get('code'), 'size': size}

    def tray_click(self):
        names = subprocess.run(['gdbus', 'call', '--session', '--dest', 'org.freedesktop.DBus', '--object-path', '/org/freedesktop/DBus',
                                '--method', 'org.freedesktop.DBus.ListNames'], env=self.env, capture_output=True, text=True, timeout=10).stdout
        items = re.findall(r"org\.kde\.StatusNotifierItem\.putgd_[0-9a-f]+", names)
        if not items:
            raise RuntimeError('put.gd registered no tray item')
        # What the panel sends when the entry is chosen: dbusmenu Event(41, "clicked").
        sent = subprocess.run(['dbus-send', '--session', '--print-reply', '--dest=' + items[0], '/Menu', 'com.canonical.dbusmenu.Event',
                               'int32:41', 'string:clicked', 'variant:int32:0', 'uint32:0'], env=self.env, capture_output=True, text=True, timeout=10)
        if sent.returncode:
            raise RuntimeError('dbusmenu Event failed: ' + sent.stderr.strip())

    def window_click(self):
        self.cli('ui.show', {'view': 'history'})
        if self.args.ask_click:
            time.sleep(1)
            self.input.chord(['alt','tab'])
            time.sleep(1)
        if self.x11:
            window = self.wait(lambda: subprocess.run(['xdotool', 'search', '--onlyvisible', '--class', 'putgd-ui'], env=self.env, capture_output=True,
                                                      text=True).stdout.split(), 'the put.gd window')[-1]
            subprocess.run(['xdotool', 'windowmove', window, '120', '60', 'windowsize', window, '1440', '960', 'windowactivate', window], env=self.env, timeout=10)
            time.sleep(1.5)
            geometry = subprocess.run(['xdotool', 'getwindowgeometry', '--shell', window], env=self.env, capture_output=True, text=True).stdout
            values = dict(line.split('=') for line in geometry.split())
            x, y = int(values['X']), int(values['Y'])
        elif self.args.kwin_place:
            x, y = self.kwin_place()
        elif self.args.ask_click:
            # GNOME Wayland tells no client where a window is. One frame of the
            # desktop is kept, and whoever runs this reads the button's centre
            # off it and writes "X Y" to the named file.
            time.sleep(2.5)
            frame = self.root / 'window-frame.png'
            if self.args.rfb != 'none':  # a guest's frame is taken on its host instead
                subprocess.run([sys.executable, self.args.rfb, str(self.args.rfb_port), str(frame)], timeout=60, check=True, stdout=subprocess.DEVNULL)
            print('FRAME ' + str(frame), flush=True)
            answer = Path(self.args.ask_click)
            self.wait(answer.exists, 'the click position in ' + str(answer), 900); time.sleep(.3)
            x, y = (int(value) for value in answer.read_text().split())
            self.receipt['windowButtonAt'] = [x, y]; self.receipt['windowFrame'] = str(frame)
            self.input.click(x, y)
            return
        else:
            x, y = self.args.window_origin
        # The Copy text button's centre in a 1440 px wide window (UI catalog, band-full).
        self.input.click(x + self.args.button[0], y + self.args.button[1])

    def kwin_place(self):
        """Plasma Wayland gives no window positions to clients: a temporary KWin
        script puts put.gd's window at a known place, and a second one, once the
        resize has settled, reports its client area."""
        def bus(*argv):
            return subprocess.run(['dbus-send', '--session', '--print-reply', '--dest=org.kde.KWin', *argv], env=self.env, capture_output=True, text=True, timeout=10)
        def script(name, body):
            path = self.root / (name + '.js')
            path.write_text('for (const w of workspace.windowList()) { if (w.resourceClass == "putgd-ui" && w.normalWindow) { ' + body + ' } }')
            loaded = bus('/Scripting', 'org.kde.kwin.Scripting.loadScript', 'string:' + str(path), 'string:' + name)
            ident = re.search(r'int32 (\d+)', loaded.stdout)
            if not ident:
                raise RuntimeError('KWin did not load the placement script: ' + loaded.stderr.strip())
            bus(f'/Scripting/Script{ident.group(1)}', 'org.kde.kwin.Script.run')
            return name
        marker = f'putgd-proof-1428-{int(time.time())}'
        time.sleep(2.5)
        names = [script(marker + '-place', 'w.frameGeometry = {x: 120, y: 60, width: 1440, height: 960}; workspace.activeWindow = w;')]
        try:
            time.sleep(2.5)
            names.append(script(marker + '-report', f'print("{marker} " + w.clientGeometry.x + " " + w.clientGeometry.y + " " + w.clientGeometry.width + " " + w.clientGeometry.height);'))
            def reported():
                log = subprocess.run(['journalctl', '--user', '--since', '-30s', '--no-pager', '-o', 'cat'], capture_output=True, text=True, timeout=10).stdout
                found = re.findall(marker + r' (-?[\d.]+) (-?[\d.]+) (-?[\d.]+) (-?[\d.]+)', log)
                return found[-1] if found else None
            x, y, width, height = (round(float(value)) for value in self.wait(reported, 'KWin to report the put.gd window'))
        finally:
            for name in names:
                bus('/Scripting', 'org.kde.kwin.Scripting.unloadScript', 'string:' + name)
        self.receipt['windowClientGeometry'] = [x, y, width, height]
        if width != 1440:
            raise RuntimeError(f'the put.gd window is {width} px wide, not the 1440 px the button position is known for')
        time.sleep(1.0)
        return x, y

    def run(self):
        size = self.args.screen
        agent = None
        try:
            if self.args.input_socket == 'start':
                path = str(Path(self.env['XDG_RUNTIME_DIR']) / 'putgd-text-proof-input.sock')
                agent = subprocess.Popen(['sudo', '-n', 'python3', self.args.host_input, 'serve', '--socket', path, '--user', os.environ['USER']],
                                         stdout=subprocess.PIPE, text=True)
                agent.stdout.readline(); self.receipt['inputAgent'] = 'tools/lab/host_input.py'
            else:
                path = self.args.input_socket
            self.input = Input(path, *size)
            for key in self.args.first_keys or []:
                self.input.chord([key]); time.sleep(1.0)
            resident = self.spawn([*self.args.app.split(), '--background'])
            self.wait(lambda: Path(self.socket).exists(), 'the resident session socket', 30); time.sleep(2)
            self.receipt['build'] = self.cli('diagnostics')['result'].get('build')
            capabilities = self.cli('capabilities')['result']
            self.receipt['adapter'] = capabilities['source'].get('adapter')
            text = capabilities['text']
            self.receipt['text'] = {'available': text['available'], 'error': text.get('error'), 'region': text['sources']['region'], 'landlockAbi': text.get('landlockAbi')}
            if not text['sources']['region']['available']:
                raise RuntimeError('Copy text from a region is unavailable: ' + json.dumps(text['sources']['region']))
            revision = self.cli('settings.get')['result']['metadata']['acceptedRevision']
            patch = {'actions': {'text': {'shortcut': self.args.hotkey}}, 'preferences': {'notifications': True}}
            if self.args.repeat_check:
                (self.root / 'archive').mkdir()
                patch['archive'] = {'keepUploads': True, 'root': str(self.root / 'archive')}
            self.cli('settings.patch', {'patch': patch, 'expectedRevision': revision})
            time.sleep(2)
            self.receipt['binding'] = self.cli('capabilities')['result']['source'].get('shortcuts', {}).get('bindings', {}).get('text')
            if self.args.fixture:
                self.spawn(self.args.fixture); time.sleep(2.5)
            if self.args.ask_region:
                # The fixture's text is wherever the desktop put the window: one
                # frame is kept and whoever runs this writes "X1 Y1 X2 Y2" (and four
                # more numbers for --repeat-check's earlier rectangle) to the named file.
                frame = self.root / 'fixture-frame.png'
                if self.x11:
                    subprocess.run(['import', '-window', 'root', str(frame)], env=self.env, timeout=30, check=True)
                else:
                    subprocess.run([sys.executable, self.args.rfb, str(self.args.rfb_port), str(frame)], timeout=60, check=True, stdout=subprocess.DEVNULL)
                print('REGION-FRAME ' + str(frame), flush=True)
                answer = Path(self.args.ask_region)
                self.wait(answer.exists, 'the region in ' + str(answer), 900); time.sleep(.3)
                numbers = [int(value) for value in answer.read_text().split()]
                self.args.region = numbers[:4]; self.receipt['region'] = numbers[:4]
                if self.args.repeat_check:
                    self.repeat_rect = numbers[4:8]
            if self.args.first_light:
                self.first_light_before()
            if self.args.repeat_check:
                self.receipt['repeat'] = {'earlierRegion': self.region_capture('region', self.repeat_rect)}
            starts = {'hotkey': lambda: self.input.chord(self.args.keys), 'tray': self.tray_click, 'window': self.window_click}
            results = []
            for name in self.args.triggers:
                try:
                    results.append(self.trigger(name, starts[name]))
                except Exception as error:  # one trigger's failure does not hide the others
                    self.receipt['triggers'][-1]['error'] = str(error) if self.receipt['triggers'] and self.receipt['triggers'][-1].get('trigger') == name else None
                    self.receipt.setdefault('errors', []).append(f'{name}: {error}')
                    print(json.dumps({'trigger': name, 'error': str(error)}), flush=True)
                    results.append(False)
                    # Leave no selector up for the next trigger.
                    self.input.chord(['esc']); time.sleep(1.5)
            self.receipt['passed'] = all(results) and len(results) == len(self.args.triggers)
            ended = time.monotonic()
            if self.args.repeat_check:
                # Repeat last region after a text capture: it must be the earlier rectangle, not the text one.
                repeat = self.receipt['repeat']
                repeat['remembered'] = self.cli('capabilities')['result']['source'].get('capture', {}).get('repeat', {}).get('remembered')
                repeat['repeat'] = self.region_capture('repeat', None)
                first, again = repeat['earlierRegion'].get('size'), repeat['repeat'].get('size')
                text = [abs(self.args.region[2] - self.args.region[0]), abs(self.args.region[3] - self.args.region[1])]
                repeat['textRegionSize'] = text
                repeat['passed'] = bool(first) and first == again and first != text
                self.receipt['passed'] = self.receipt['passed'] and repeat['passed']
                print(json.dumps({'repeat': repeat}), flush=True)
            if self.args.first_light:
                self.first_light_after(ended)
            if Path(__file__).with_name('extra.py').exists():
                from extra import extra
                extra(self)
            # No region capture ran in this resident: Repeat last region must have nothing to repeat.
            self.receipt['repeatRemembered'] = self.cli('capabilities')['result']['source'].get('capture', {}).get('repeat', {}).get('remembered')
            # A text capture leaves no journal row and nothing recognized on disk.
            self.receipt['operationsLeft'] = [o.get('action') + ':' + o.get('state') for o in self.cli('operation.recent')['result'].get('operations', [])]
            needle = self.args.needle.encode()
            self.receipt['recognizedTextOnDisk'] = [str(p) for folder in self.scan for p in folder.rglob('*') if p.is_file() and needle in p.read_bytes()]
            self.receipt['scanned'] = [str(folder) for folder in self.scan]
        finally:
            try:
                revision = self.cli('settings.get')['result']['metadata']['acceptedRevision']
                self.cli('settings.patch', {'patch': {'actions': {'text': {'shortcut': ''}}}, 'expectedRevision': revision}, check=False)
                time.sleep(1)
                self.cli('ui.quit', check=False)
            except Exception as error:
                self.receipt.setdefault('errors', []).append(f'cleanup: {error}')
            time.sleep(2)
            for process in self.started:
                if process.poll() is None:
                    try:
                        os.killpg(process.pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
            if hasattr(self, 'watcher') and self.watcher.poll() is None:
                subprocess.run(['sudo','-n','kill',str(self.watcher.pid)]);self.watcher.wait(10)
            if agent is not None:
                subprocess.run(['sudo', '-n', 'kill', str(agent.pid)]); agent.wait(10)
            if self.appimage_user_data and self.appimage_user_data.exists():
                retained = Path.home()/'work/a1428'/('data-'+self.root.name+'-retained')
                if retained.exists(): raise RuntimeError('retention target exists')
                self.appimage_user_data.rename(retained)
                self.receipt['appimageUserDataRetained'] = str(retained)
            self.receipt['root'] = str(self.root)
            (self.root / 'receipt.json').write_text(json.dumps(self.receipt, indent=1))
            print('RECEIPT ' + str(self.root / 'receipt.json'), flush=True)
        return 0 if self.receipt.get('passed') else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--desktop', required=True)
    parser.add_argument('--leader', nargs='+', required=True, help='desktop session process names to take the environment from')
    parser.add_argument('--app', default='/usr/bin/putgd'); parser.add_argument('--cli', default='/usr/bin/putgd-cli')
    parser.add_argument('--host-input', default='host_input.py'); parser.add_argument('--input-socket', default='start')
    parser.add_argument('--screen', nargs=2, type=int, required=True, metavar=('WIDTH', 'HEIGHT'))
    parser.add_argument('--region', nargs=4, type=int, required=True, metavar=('X1', 'Y1', 'X2', 'Y2'))
    parser.add_argument('--hotkey', default='Ctrl+Shift+9'); parser.add_argument('--keys', nargs='+', default=['ctrl', 'shift', '9'])
    parser.add_argument('--triggers', nargs='+', default=['hotkey', 'tray', 'window'])
    parser.add_argument('--fixture', nargs='+', help='a window of synthetic content to select over')
    parser.add_argument('--expect', default=r'put\.gd fake helper 1428: region \d+ x \d+')
    parser.add_argument('--button', nargs=2, type=int, default=[1190, 82]); parser.add_argument('--window-origin', nargs=2, type=int, default=[0, 0])
    parser.add_argument('--kwin-place', action='store_true', help='Plasma Wayland: place the put.gd window with a temporary KWin script')
    parser.add_argument('--ask-click', help='GNOME Wayland: keep a frame, then wait for "X Y" in this file and click there')
    parser.add_argument('--rfb', default='rfb.py'); parser.add_argument('--rfb-port', type=int, default=5901)
    parser.add_argument('--first-keys', nargs='+', help='keys pressed one by one before anything else (esc leaves the GNOME overview)')
    parser.add_argument('--real-profile', action='store_true', help='a disposable guest: no private configuration folders')
    parser.add_argument('--ask-region', help='keep a frame once the fixture is up, then wait for "X1 Y1 X2 Y2" in this file')
    parser.add_argument('--first-light', action='store_true', help='the real helper: its peak memory and exit, the resident before and 180 s after, its maps')
    parser.add_argument('--helper-watch', default='helper_watch.py'); parser.add_argument('--settle', type=float, default=20)
    parser.add_argument('--repeat-check', action='store_true', help='a region capture first, Repeat last region after the text capture')
    parser.add_argument('--needle', default='put.gd fake helper 1428', help='text that must be in no file of the resident afterwards')
    parser.add_argument('--frame', action='store_true', help='keep one frame of the selector per trigger (X11)')
    return Run(parser.parse_args()).run()


if __name__ == '__main__':
    sys.exit(main())
