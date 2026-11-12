#!/usr/bin/env python3
"""Scroll capture of live web pages against the browser's own full-page picture
(PR #1398, fix round 7). Runs on a builder, in the desktop session's environment.

  live7.py browser start firefox|chromium     a fresh profile, maximized, and the viewport's place on the screen
  live7.py browser stop
  live7.py run SITE MODE NAME [--driver]      one capture and its reference; MODE half|top
  live7.py resident start|stop                a private resident of the installed package
  live7.py verify DIR                         compare capture.png with reference.png

No key or button is injected: the browser is driven through its own remote
protocol (Marionette, DevTools), the capture turns the wheel itself.
"""
import base64
import hashlib
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

P = Path(os.environ.get('SF7', str(Path.home() / 'work/sf7')))
sys.path.insert(0, str(P / 'tools'))
SITES = {
    'pr': 'https://github.com/patrick-hudson/put.gd-desktop/pull/1398',
    'wiki': 'https://en.wikipedia.org/wiki/Linux',
    'py': 'https://docs.python.org/3/library/stdtypes.html',
    'mdn': 'https://developer.mozilla.org/en-US/docs/Web/CSS/position',
    'repo': 'https://github.com/patrick-hudson/put.gd-desktop',
}
MARIONETTE, DEVTOOLS = 28291, 28292
INFO = '''return {url:location.href,title:document.title,x:window.mozInnerScreenX,y:window.mozInnerScreenY,w:innerWidth,h:innerHeight,
 dpr:devicePixelRatio,clientWidth:document.documentElement.clientWidth,scrollY:Math.round(scrollY),
 docHeight:Math.max(document.documentElement.scrollHeight,document.body?document.body.scrollHeight:0),
 pendingImages:[...document.images].filter(i=>!i.complete).length,images:document.images.length,
 signedOut:!document.querySelector('meta[name="user-login"]')||!document.querySelector('meta[name="user-login"]').content};'''


def session_env():
    import record_run
    env, desktop = record_run.session_environment()
    return env, desktop


class Marionette:
    def __init__(self):
        self.s = socket.create_connection(('127.0.0.1', MARIONETTE), 5)
        self.s.settimeout(180)
        self.i = 0
        self.recv()
        self.cmd('WebDriver:NewSession', {})

    def recv(self):
        b = b''
        while not b.endswith(b':'):
            c = self.s.recv(1)
            if not c:
                raise RuntimeError('marionette closed')
            b += c
        n = int(b[:-1])
        b = b''
        while len(b) < n:
            b += self.s.recv(n - len(b))
        return json.loads(b)

    def cmd(self, method, params=None):
        self.i += 1
        b = json.dumps([0, self.i, method, params or {}]).encode()
        self.s.sendall(str(len(b)).encode() + b':' + b)
        r = self.recv()
        if r[2]:
            raise RuntimeError(r[2])
        return r[3]

    def js(self, script):
        v = self.cmd('WebDriver:ExecuteScript', {'script': script, 'args': [], 'newSandbox': True, 'sandbox': 'default', 'line': 0, 'filename': 'live7'})
        return v.get('value', v) if isinstance(v, dict) else v

    def navigate(self, url):
        self.cmd('WebDriver:Navigate', {'url': url})

    def maximize(self):
        self.cmd('WebDriver:MaximizeWindow')

    def shot_full(self, path, limit=64000):
        info = self.js(INFO)
        if info['docHeight'] <= min(limit, 65000):
            r = self.cmd('WebDriver:TakeScreenshot', {'id': None, 'highlights': [], 'full': True})
            s = r.get('value', r) if isinstance(r, dict) else r
            Path(path).write_bytes(base64.b64decode(s))
            return
        # Taller than one screenshot may be: the same snapshot call in tiles, from the browser's own context.
        from PIL import Image
        import io
        width, height = int(info['w']), min(int(info['docHeight']), limit)
        out = Image.new('RGB', (width, height), 'white')
        self.cmd('Marionette:SetContext', {'value': 'chrome'})
        try:
            y = 0
            while y < height:
                h = min(2500, height - y)  # small tiles, one at a time: a tall snapshot is heavy on the GPU
                time.sleep(0.4)
                v = self.cmd('WebDriver:ExecuteAsyncScript', {'script': '''
                    const [y, w, h, done] = arguments;
                    (async () => {
                      const bc = gBrowser.selectedBrowser.browsingContext;
                      const snap = await bc.currentWindowGlobal.drawSnapshot(new DOMRect(0, y, w, h), 1, "rgb(255,255,255)");
                      const c = document.createElementNS("http://www.w3.org/1999/xhtml", "canvas");
                      c.width = w; c.height = h; c.getContext("2d").drawImage(snap, 0, 0);
                      return c.toDataURL("image/png");
                    })().then(done, e => done("error: " + e));''', 'args': [y, width, h], 'newSandbox': True, 'sandbox': 'default', 'line': 0, 'filename': 'live7'})
                data = v.get('value', v) if isinstance(v, dict) else v
                if not str(data).startswith('data:image/png;base64,'):
                    raise RuntimeError(str(data)[:300])
                out.paste(Image.open(io.BytesIO(base64.b64decode(data.split(',', 1)[1]))).convert('RGB'), (0, y))
                y += h
        finally:
            self.cmd('Marionette:SetContext', {'value': 'content'})
        out.save(path)


class DevTools:
    """A minimal DevTools client: one page target over a WebSocket, standard library only."""

    def __init__(self):
        tabs = json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % DEVTOOLS, timeout=5))
        page = next(t for t in tabs if t.get('type') == 'page')
        path = '/' + page['webSocketDebuggerUrl'].split('/', 3)[3]
        self.s = socket.create_connection(('127.0.0.1', DEVTOOLS), 5)
        self.s.settimeout(180)
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall(('GET %s HTTP/1.1\r\nHost: 127.0.0.1:%d\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\n\r\n' % (path, DEVTOOLS, key)).encode())
        head = b''
        while b'\r\n\r\n' not in head:
            head += self.s.recv(1)
        if b' 101 ' not in head.split(b'\r\n')[0]:
            raise RuntimeError('devtools refused the websocket: %r' % head[:200])
        self.i = 0

    def _read(self, n):
        b = b''
        while len(b) < n:
            c = self.s.recv(min(1 << 20, n - len(b)))
            if not c:
                raise RuntimeError('devtools closed')
            b += c
        return b

    def _send(self, text):
        data = text.encode()
        mask = os.urandom(4)
        head = bytes([0x81])
        if len(data) < 126:
            head += bytes([0x80 | len(data)])
        elif len(data) < 65536:
            head += bytes([0x80 | 126]) + struct.pack('>H', len(data))
        else:
            head += bytes([0x80 | 127]) + struct.pack('>Q', len(data))
        self.s.sendall(head + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

    def _recv(self):
        message = b''
        while True:
            a, b = self._read(2)
            n = b & 0x7f
            if n == 126:
                n = struct.unpack('>H', self._read(2))[0]
            elif n == 127:
                n = struct.unpack('>Q', self._read(8))[0]
            data = self._read(n)
            op = a & 0x0f
            if op == 9:  # ping
                continue
            if op == 8:
                raise RuntimeError('devtools closed the websocket')
            message += data
            if a & 0x80:
                return json.loads(message)

    def cmd(self, method, params=None):
        self.i += 1
        self._send(json.dumps({'id': self.i, 'method': method, 'params': params or {}}))
        deadline = time.time() + 90
        while True:
            if time.time() > deadline:
                raise RuntimeError('devtools: no answer to %s in 90 s' % method)
            r = self._recv()
            if r.get('id') == self.i:
                if 'error' in r:
                    raise RuntimeError(r['error'])
                return r.get('result', {})

    def js(self, script):
        r = self.cmd('Runtime.evaluate', {'expression': '(function(){%s})()' % script, 'returnByValue': True, 'awaitPromise': True})
        if 'exceptionDetails' in r:
            raise RuntimeError(r['exceptionDetails'])
        return r['result'].get('value')

    def navigate(self, url):
        self.cmd('Page.enable')
        self.cmd('Page.navigate', {'url': url})
        for _ in range(120):
            time.sleep(0.5)
            if self.js('return document.readyState') == 'complete':
                return

    def maximize(self):
        w = self.cmd('Browser.getWindowForTarget')
        self.cmd('Browser.setWindowBounds', {'windowId': w['windowId'], 'bounds': {'windowState': 'maximized'}})

    def shot_full(self, path, limit=64000):
        # The document from its first row to its last, as it is laid out at its top: what the page pins in the
        # viewport is put back in the flow (sticky) or left out (fixed), and the viewport is photographed screen by
        # screen at known scroll positions. (A capture "beyond the viewport" lays the page out again at another
        # width, and on a page with a banner it never came back.)
        from PIL import Image
        import io
        info = self.js(INFO)
        width, vh, height = int(info['clientWidth']), int(info['h']), min(int(info['docHeight']), limit)
        self.js('''for(const e of document.querySelectorAll('*')){const p=getComputedStyle(e).position;
          if(p==='sticky')e.style.setProperty('position','relative','important');
          else if(p==='fixed')e.style.setProperty('visibility','hidden','important');}return 0;''')
        time.sleep(1.0)
        height = min(int(self.js(INFO)['docHeight']), limit)
        out = Image.new('RGB', (width, height), 'white')
        y = 0
        while y < height:
            self.js('window.scrollTo({top:%d,behavior:"instant"});return 0;' % y)
            time.sleep(0.35)
            at = int(round(self.js('return scrollY')))
            r = self.cmd('Page.captureScreenshot', {'format': 'png'})
            tile = Image.open(io.BytesIO(base64.b64decode(r['data']))).convert('RGB')
            out.paste(tile.crop((0, 0, width, min(tile.height, height - at))), (0, at))
            if at + vh >= height or at < y:
                break
            y = at + vh
        out.save(path)


def connect():
    kind = (P / 'browser.kind').read_text().strip()
    return (Marionette() if kind == 'firefox' else DevTools()), kind


def screen_png(path):
    import rfb
    port = int(os.environ.get('SF7_VNC', '5901' if os.uname().nodename == 'fedora' else '5900'))
    v = rfb.RFB(port)
    v.screenshot(Path(path))
    v.sock.close()


def browser_start(kind):
    env, desktop = session_env()
    prof = P / ('profile-' + kind)
    if prof.exists():
        raise SystemExit('profile exists: stop the browser and delete it by manifest first')
    prof.mkdir(mode=0o700)
    log = open(P / (kind + '.log'), 'w')
    if kind == 'firefox':
        (prof / 'user.js').write_text(''.join('user_pref(%s,%s);\n' % (json.dumps(k), json.dumps(v)) for k, v in {
            'marionette.port': MARIONETTE, 'browser.aboutwelcome.enabled': False, 'browser.shell.checkDefaultBrowser': False,
            'browser.startup.homepage_override.mstone': 'ignore', 'browser.sessionstore.resume_from_crash': False,
            'datareporting.policy.dataSubmissionEnabled': False, 'browser.tabs.warnOnClose': False}.items()))
        binary = shutil.which('firefox') or shutil.which('firefox-esr')
        proc = subprocess.Popen([binary, '--new-instance', '--no-remote', '--marionette', '--remote-allow-system-access', '--profile', str(prof), 'about:blank'],
                                env=dict(env, MOZ_DBUS_REMOTE='0', MOZ_NO_REMOTE='1'), stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    else:
        binary = shutil.which('chromium') or shutil.which('chromium-browser') or shutil.which('google-chrome')
        proc = subprocess.Popen([binary, '--user-data-dir=' + str(prof), '--remote-debugging-port=%d' % DEVTOOLS, '--no-first-run', '--no-default-browser-check',
                                 '--password-store=basic', '--start-maximized', '--disable-search-engine-choice-screen', 'about:blank'],
                                env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    (P / 'browser.pid').write_text(str(proc.pid))
    (P / 'browser.kind').write_text(kind)
    for _ in range(60):
        time.sleep(1)
        try:
            b, _ = connect()
            break
        except Exception:
            continue
    else:
        raise SystemExit('the browser did not open its remote port')
    try:
        b.maximize()
    except Exception as e:
        print('maximize:', e)
    time.sleep(3)
    # The viewport's place on the screen, from the screen itself: a page of one colour, and where that colour is.
    b.navigate('data:text/html,<body style="margin:0;background:rgb(255,0,254)">')
    time.sleep(2.5)
    screen_png(P / 'calibration.png')
    from PIL import Image
    import numpy as np
    a = np.asarray(Image.open(P / 'calibration.png').convert('RGB')).astype(int)
    m = (abs(a[:, :, 0] - 255) < 6) & (a[:, :, 1] < 6) & (abs(a[:, :, 2] - 254) < 6)
    ys, xs = np.where(m.any(axis=1))[0], np.where(m.any(axis=0))[0]
    if not len(ys):
        raise SystemExit('the calibration colour is not on the screen')
    rect = [int(xs[0]), int(ys[0]), int(xs[-1] - xs[0] + 1), int(ys[-1] - ys[0] + 1)]
    info = b.js(INFO)
    solid = float(m[rect[1]:rect[1] + rect[3], rect[0]:rect[0] + rect[2]].mean())
    (P / 'viewport.json').write_text(json.dumps({'rect': rect, 'solid': solid, 'info': info, 'screen': [int(a.shape[1]), int(a.shape[0])], 'desktop': desktop, 'kind': kind,
                                                 'version': subprocess.run([binary, '--version'], capture_output=True, text=True, env=env).stdout.strip()}, indent=1))
    print(json.dumps({'rect': rect, 'solid': solid, 'inner': [info['w'], info['h']], 'dpr': info['dpr']}))


def browser_stop():
    pid = int((P / 'browser.pid').read_text())
    try:
        os.kill(pid, 15)
    except ProcessLookupError:
        pass
    for _ in range(40):
        if not Path('/proc/%d' % pid).exists():
            break
        time.sleep(0.25)
    print('stopped', pid, 'gone' if not Path('/proc/%d' % pid).exists() else 'still there')


def rpc(method, params=None):
    env = json.loads((P / 'env.json').read_text())
    r = subprocess.run(['putgd-cli', '--socket', str(P / 'r/putgd/session.sock'), method, json.dumps(params or {})], env=env, text=True, capture_output=True, timeout=90)
    o = json.loads(r.stdout)
    if not o['ok']:
        raise RuntimeError(json.dumps(o))
    return o['result']


def resident(action):
    if action == 'start':
        env, desktop = session_env()
        for n in ['c', 'd', 's', 'cache', 'r', 'archive']:
            (P / n).mkdir(mode=0o700)
        for k, n in [('CONFIG_HOME', 'c'), ('DATA_HOME', 'd'), ('STATE_HOME', 's'), ('CACHE_HOME', 'cache'), ('RUNTIME_DIR', 'r')]:
            env['XDG_' + k] = str(P / n)
        env.update(PIPEWIRE_RUNTIME_DIR='/run/user/%d' % os.getuid(), PULSE_SERVER='unix:/run/user/%d/pulse/native' % os.getuid(), PUTGD_RECORD_DEBUG_LOG=str(P / 'helper.log'))
        (P / 'env.json').write_text(json.dumps(env))
        os.chmod(P / 'env.json', 0o600)
        q = subprocess.Popen(['putgd', '--background'], env=env, stdout=open(P / 'resident.log', 'w'), stderr=subprocess.STDOUT, start_new_session=True)
        (P / 'resident.pid').write_text(str(q.pid))
        for _ in range(150):
            if (P / 'r/putgd/session.sock').exists():
                break
            time.sleep(0.1)
        time.sleep(1)
        s = rpc('settings.get')
        d = s['document']
        d['preferences']['notifications'] = False
        d['archive'].update(keepUploads=True, root=str(P / 'archive'))
        rpc('settings.save', {'document': d, 'expectedRevision': s['metadata']['observedRevision']})
        (P / 'capabilities.json').write_text(json.dumps(rpc('scroll.capabilities'), indent=1))
        (P / 'version.json').write_text(subprocess.run(['putgd-cli', '--version-json'], capture_output=True, text=True).stdout)
        time.sleep(2)
        # Its dashboard would be in the picture: close this resident's own window process.
        for proc in Path('/proc').iterdir():
            if not proc.name.isdigit():
                continue
            try:
                if (proc / 'comm').read_text().strip() == 'putgd-ui' and ('XDG_CONFIG_HOME=' + str(P / 'c')).encode() in (proc / 'environ').read_bytes().split(b'\0'):
                    os.kill(int(proc.name), 15)
            except (OSError, PermissionError):
                pass
        print((P / 'capabilities.json').read_text())
    else:
        try:
            rpc('app.quit')
        except Exception as e:
            print('quit:', e)
        pid = int((P / 'resident.pid').read_text())
        for _ in range(40):
            if not Path('/proc/%d' % pid).exists():
                break
            time.sleep(0.25)
        if Path('/proc/%d' % pid).exists():
            os.kill(pid, 15)
        print('resident stopped')


def wait_loaded(b, seconds):
    end = time.time() + seconds
    last = None
    while time.time() < end:
        info = b.js(INFO)
        key = (info['docHeight'], info['pendingImages'])
        if key == last and info['pendingImages'] == 0:
            return info
        last = key
        time.sleep(1.0)
    return b.js(INFO)


def run(site, mode, name, driver):
    out = P / 'runs' / name
    out.mkdir(parents=True)
    b, kind = connect()
    view = json.loads((P / 'viewport.json').read_text())
    url = SITES.get(site, site)
    b.navigate(url)
    time.sleep(6)
    info = wait_loaded(b, 25)
    # The page as a reader finds it: at its top, or scrolled halfway down. (A browser may
    # restore the place a page was left at when it is opened again: say where to begin.)
    b.js('window.scrollTo({top:0,behavior:"instant"});return 0;')
    time.sleep(1.0)
    if mode == 'half':
        b.js('window.scrollTo({top:%d,behavior:"instant"});return 0;' % ((info['docHeight'] - info['h']) // 2))
        time.sleep(2.5)
    if os.environ.get('SF7_START'):  # lab: begin somewhere down the page
        b.js('window.scrollTo({top:%d,behavior:"instant"});return 0;' % int(os.environ['SF7_START']))
        time.sleep(2.5)
    before = wait_loaded(b, 15)
    if mode == 'top' and not os.environ.get('SF7_START') and before['scrollY'] != 0:
        b.js('window.scrollTo({top:0,behavior:"instant"});return 0;')
        time.sleep(2.5)
        before = wait_loaded(b, 15)
    rect = list(view['rect'])
    # Without the browser's own scrollbar column, where it has one.
    rect[2] = min(rect[2], int(round(before['clientWidth'] * before['dpr'])))
    rect[3] = min(rect[3], int(round(before['h'] * before['dpr'])))
    result = {'name': name, 'site': site, 'url': url, 'mode': mode, 'browser': kind, 'rect': rect, 'fromTop': mode == 'half', 'before': before, 'viewport': view}
    start = time.time()
    if driver:
        env, _ = session_env()
        build = Path(os.environ.get('SF7_BUILD', str(Path.home() / 'work/s1376/src/build/dev')))
        stage = out / 'stage'
        stage.mkdir(mode=0o700)
        env.update(PUTGD_RECORD_DEBUG_LOG=str(out / 'helper.log'), PIPEWIRE_RUNTIME_DIR='/run/user/%d' % os.getuid())
        if os.environ.get('PUTGD_SCROLL_DUMP'):
            env['PUTGD_SCROLL_DUMP'] = os.environ['PUTGD_SCROLL_DUMP']
        cmd = [str(build / 'test_scroll_capture_driver'), '--helper', str(build / 'putgd-record'), '--rect', ','.join(map(str, rect)), '--out', str(stage), '--max-height', '60000'] + (['--from-top'] if mode == 'half' else [])
        r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
        (out / 'driver.log').write_text(r.stdout + '\n--- stderr\n' + r.stderr)
        finished = None
        for line in r.stdout.splitlines():
            try:
                o = json.loads(line)
            except ValueError:
                continue
            if o.get('event') == 'finished':
                finished = o
            if o.get('event') == 'failed' or 'prepare' in o and 'code' in o.get('prepare', {}):
                result['failed'] = o
        result['capture'] = finished
        if finished and Path(finished['path']).exists():
            shutil.copyfile(finished['path'], out / 'capture.png')
        for f in stage.iterdir():
            f.unlink()
        stage.rmdir()
    else:
        s = rpc('settings.get')
        doc = s['document']
        doc['preferences']['scrollCaptureFromTop'] = mode == 'half'
        doc['preferences']['scrollCaptureMaxHeight'] = 60000
        rpc('settings.save', {'document': doc, 'expectedRevision': s['metadata']['observedRevision']})
        log = P / 'helper.log'
        off = log.stat().st_size if log.exists() else 0
        v = rpc('scroll.prepare', {'rect': rect})
        ident = v['id']
        while v['state'] != 'ready':
            time.sleep(0.1)
            v = rpc('scroll.inspect', {'id': ident})
        time.sleep(0.4)
        rpc('scroll.start', {'id': ident})
        ypoll = []
        while True:
            v = rpc('scroll.inspect', {'id': ident})
            if v['state'] in ('done', 'failed', 'cancelled'):
                break
            if os.environ.get('SF7_YPOLL'):  # lab: where the browser says the page stands, unrounded, all the while
                try:
                    ypoll.append([round(time.time(), 3)] + list(b.js('return [scrollY, document.documentElement.scrollHeight, devicePixelRatio];')))
                except Exception as e:
                    ypoll.append([round(time.time(), 3), str(e)[:80]])
            if time.time() - start > 320:
                rpc('scroll.cancel', {'id': ident})
                raise TimeoutError(name)
            time.sleep(0.2)
        result['capture'] = v.get('result') or v
        result['state'] = v
        if ypoll:
            result['ypoll'] = ypoll
        sha = (v.get('result') or {}).get('sha256')
        found = None
        for _ in range(100):
            for f in (P / 'archive').rglob('*.png'):
                if hashlib.sha256(f.read_bytes()).hexdigest() == sha:
                    found = f
                    break
            if found or not sha:
                break
            time.sleep(0.1)
        if found:
            shutil.copyfile(found, out / 'capture.png')
        if log.exists():
            (out / 'helper.log').write_bytes(log.read_bytes()[off:])
    result['seconds'] = round(time.time() - start, 2)
    after = b.js(INFO)
    result['after'] = after
    # The browser's own picture of the whole page, taken right after the capture at the same width, with the
    # page back at its top: a sticky bar is drawn where the page stands, and at the top it is where the document has it.
    try:
        b.js('window.scrollTo({top:0,behavior:"instant"});return 0;')
        time.sleep(2.0)
        # What the page keeps in place in the viewport (position sticky or fixed), as the document has it at its top:
        # a tall image cannot show such a thing the way the browser's own picture does, and the comparison says so.
        pinned = b.js('''const r=[];for(const e of document.querySelectorAll('*')){const s=getComputedStyle(e);if(s.position!=='sticky'&&s.position!=='fixed')continue;
          if(s.display==='none'||s.visibility==='hidden'||+s.opacity===0)continue;const q=e.getBoundingClientRect();if(q.width<1||q.height<1)continue;
          r.push({position:s.position,what:(e.tagName+'.'+String(e.className||'')).slice(0,70),x:Math.round(q.x),y:Math.round(q.y),w:Math.round(q.width),h:Math.round(q.height)});}
          return {vw:innerWidth,vh:innerHeight,list:r.slice(0,80)};''')
        result['pinned'] = pinned
        vw, vh, dpr = pinned['vw'], pinned['vh'], before['dpr']
        exclude = []
        for e in pinned['list']:
            x0, x1 = int((e['x'] - 6) * dpr), int((e['x'] + e['w'] + 6) * dpr)
            if e['h'] >= 150 and e['w'] <= 0.45 * vw:
                exclude.append({'x': [max(0, x0), max(0, x1)], 'why': 'a side bar the page keeps in place (%s, %s): the capture shows it beside every row as the screen did, the browser\'s picture shows it once' % (e['position'], e['what'])})
            elif e['w'] <= 30 and e['h'] >= 0.5 * vh:
                exclude.append({'x': [max(0, x0), max(0, x1)], 'why': 'a strip the page keeps at the edge of the viewport (%s)' % e['what']})
            elif e['position'] == 'fixed' and e['w'] >= 0.5 * vw and e['h'] >= 30 and e['y'] + e['h'] >= vh - 8:
                exclude.append({'y': [int(e['y'] * dpr), int((e['y'] + e['h']) * dpr)], 'why': 'a bar the page keeps at the bottom of the viewport (%s): the browser\'s picture has it over these rows of the first screen, the capture has the page there and the bar once at its end' % e['what']})
                exclude.append({'lastRows': int(e['h'] * dpr), 'why': 'the same bar, once, at the end of the capture'})
        if kind == 'firefox' and rect[2] >= int(round(before['w'] * dpr)) - 1:
            exclude.append({'x': [rect[2] - 8, rect[2]], 'why': 'Firefox\'s overlay scrollbar at the right edge: on the screen while the page scrolls, not in the browser\'s picture'})
        (out / 'exclude.json').write_text(json.dumps(exclude, indent=1))
        # No taller than the capture needs (a capped capture of a very tall page): tall snapshots are heavy on the GPU.
        got = int((result.get('capture') or {}).get('height') or 0)
        b.shot_full(out / 'reference.png', limit=min(64000, got + 1500) if got else 64000)
    except Exception as e:
        result['referenceError'] = str(e)
    result['afterReference'] = b.js(INFO)
    (out / 'result.json').write_text(json.dumps(result, indent=1))
    c = result.get('capture') or {}
    print(json.dumps({'name': name, 'end': c.get('endReason'), 'height': c.get('height'), 'note': c.get('note'), 'truncated': c.get('truncated'), 'topReached': c.get('topReached'),
                      'doc': after['docHeight'], 'seconds': result['seconds'], 'failed': result.get('failed')}))
    # The comparison needs no desktop: with SF7_NOVERIFY it is left for after the desktop is given back.
    if (out / 'capture.png').exists() and (out / 'reference.png').exists() and not os.environ.get('SF7_NOVERIFY'):
        verify(out)


def verify(out):
    """Capture against reference in bands of 64 rows: where the band is in the reference (rows that are equal
    bit for bit say so), and how many of its pixels differ there."""
    import collections
    import numpy as np
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    out = Path(out)
    cap = np.asarray(Image.open(out / 'capture.png').convert('RGB'))
    ref = np.asarray(Image.open(out / 'reference.png').convert('RGB'))
    H, W = cap.shape[:2]
    w = min(W, ref.shape[1])
    exclude = json.loads((out / 'exclude.json').read_text()) if (out / 'exclude.json').exists() else []
    cols = np.ones(w, bool)
    for e in exclude:
        if 'x' in e and 'y' not in e:
            cols[e['x'][0]:e['x'][1]] = False
    for e in list(exclude):
        if 'lastRows' in e:
            exclude.append({'y': [H - e['lastRows'], H], 'why': e['why']})
    keep = np.where(cols)[0]
    sub = keep[::3]

    def keys(a):
        k = []
        for y in range(a.shape[0]):
            row = a[y, sub, :]
            k.append(None if int(row.max()) - int(row.min()) < 24 else hashlib.blake2b(row.tobytes(), digest_size=8).digest())
        return k
    ck, rk = keys(cap[:, :w]), keys(ref[:, :w])
    index = collections.defaultdict(list)
    for y, k in enumerate(rk):
        if k is not None:
            index[k].append(y)

    def diff(y0, y1, dy):
        if y0 + dy < 0 or y1 + dy > ref.shape[0]:
            return None
        # Grey means of 4x4 blocks: the same text drawn for the screen and for the browser's own picture
        # differs in its antialiasing, pixel by pixel, and not in what a block of it looks like.
        ga = cap[y0:y1, :w].astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)
        gb = ref[y0 + dy:y1 + dy, :w].astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)
        hh, ww = (y1 - y0) // 4 * 4, w // 4 * 4
        blocks = np.abs(ga[:hh, :ww].reshape(hh // 4, 4, ww // 4, 4).mean(axis=(1, 3)) - gb[:hh, :ww].reshape(hh // 4, 4, ww // 4, 4).mean(axis=(1, 3))) > 32
        d = np.zeros((y1 - y0, w), bool)
        d[:hh, :ww] = np.repeat(np.repeat(blocks, 4, axis=0), 4, axis=1)
        d[:, ~cols] = False
        for e in exclude:
            if 'y' in e:
                a, b = max(e['y'][0] - y0, 0), min(e['y'][1] - y0, y1 - y0)
                if a < b:
                    x = e.get('x', [0, w])
                    d[a:b, x[0]:x[1]] = False
        return d

    band, shift = 64, 0
    rows, bad, exact, shifted, matchedRows, unknown = [], [], 0, 0, 0, 0
    for y0 in range(0, H, band):
        y1 = min(H, y0 + band)
        votes = collections.Counter()
        for y in range(y0, y1):
            hits = index.get(ck[y]) if ck[y] is not None else None
            if hits and len(hits) <= 4:
                for r in hits:
                    votes[r - y] += 1
        cands = [shift] + [dy for dy, n in votes.most_common(3) if dy != shift]
        best = None
        limit = int(np.count_nonzero(cols)) * (y1 - y0) * 0.002
        for dy in cands:
            d = diff(y0, y1, dy)
            if d is None:
                continue
            n = int(d.sum())
            if best is None or n < best[0]:
                best = (n, dy, d)
            if n <= limit:
                break  # where the band before it was, or the first place its rows name
        if best is None:
            bad.append({'y': [y0, y1], 'why': 'beyond the reference'})
            rows.append([y0, None, -1])
            continue
        n, dy, d = best
        matchedRows += votes.get(dy, 0)
        limit = int(np.count_nonzero(cols)) * (y1 - y0) * 0.002
        if n <= limit:
            exact += dy == 0
            shifted += dy != 0
            shift = dy
            rows.append([y0, dy, n])
        else:
            xs, ys = np.where(d.any(axis=0))[0], np.where(d.any(axis=1))[0]
            bad.append({'y': [y0, y1], 'pixels': n, 'shift': dy, 'votes': votes.get(dy, 0), 'x': [int(xs[0]), int(xs[-1]) + 1], 'rows': [int(ys[0]) + y0, int(ys[-1]) + y0 + 1]})
            rows.append([y0, None, n])
    changes, last = [], 0
    for y0, dy, n in rows:
        if dy is not None and dy != last:
            changes.append([y0, dy])
            last = dy
    v = {'capture': [W, H], 'reference': [int(ref.shape[1]), int(ref.shape[0])], 'comparedColumns': int(np.count_nonzero(cols)), 'bands': len(rows), 'exactBands': exact, 'shiftedBands': shifted, 'badBands': len(bad), 'bad': bad, 'shiftChanges': changes,
         'rowsEqualBitForBit': matchedRows, 'excluded': exclude,
         'rule': 'a band of 64 rows passes when at most 0.2% of its compared pixels lie in 4x4 blocks whose grey mean differs by more than 32, at the place in the reference that its bit-equal rows name (or the band before it had)'}
    (out / 'verification.json').write_text(json.dumps(v, indent=1))
    print(json.dumps({'verify': out.name, 'size': [W, H], 'ref': v['reference'], 'bands': len(rows), 'exact': exact, 'shifted': shifted, 'bad': len(bad), 'shiftChanges': changes[:10], 'bitEqualRows': matchedRows, 'firstBad': bad[:8]}))


def strip(out, y0, y1, name=None):
    """Capture, reference and their difference side by side for rows y0..y1, scaled to a third."""
    import numpy as np
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    out = Path(out)
    v = json.loads((out / 'verification.json').read_text())
    cap = Image.open(out / 'capture.png').convert('RGB')
    ref = Image.open(out / 'reference.png').convert('RGB')
    dy = 0
    for y, s in v['shiftChanges']:
        if y <= y0:
            dy = s
    y1 = min(y1, cap.height)
    a = cap.crop((0, y0, cap.width, y1))
    b = ref.crop((0, y0 + dy, cap.width, y1 + dy))
    d = (np.abs(np.asarray(a).astype(np.int16) - np.asarray(b).astype(np.int16)).max(axis=2) > 40)
    dm = Image.fromarray((d * 255).astype('uint8')).convert('RGB')
    sheet = Image.new('RGB', (cap.width * 3 + 20, y1 - y0), (255, 0, 0))
    sheet.paste(a, (0, 0)); sheet.paste(b, (cap.width + 10, 0)); sheet.paste(dm, (2 * cap.width + 20, 0))
    sheet = sheet.resize((sheet.width // 3, max(1, sheet.height // 3)))
    path = out / (name or 'strip-%d-%d.png' % (y0, y1))
    sheet.save(path)
    print(path)


def close_notices():
    if (P / 'closenotes.sh').exists() and subprocess.run(['pgrep', '-u', str(os.getuid()), '-x', 'plasmashell'], capture_output=True).stdout.strip():
        subprocess.run(['sh', str(P / 'closenotes.sh')], capture_output=True)
        time.sleep(1.5)


def campaign(prefix, browsers, sites, modes, driver):
    """Every site in every mode in each browser, one after the other; a browser is started and stopped here."""
    import traceback
    log = open(P / (prefix + '-campaign.log'), 'a')
    def say(text):
        log.write(time.strftime('%H:%M:%S ') + text + chr(10)); log.flush(); print(text, flush=True)
    for kind in browsers:
        try:
            if (P / ('profile-' + kind)).exists():
                subprocess.run([sys.executable, str(P / 'rmprofile.py'), str(P / ('profile-' + kind))], capture_output=True)
            browser_start(kind)
        except BaseException as e:
            say('browser %s did not start: %s' % (kind, e))
            continue
        for site in sites:
            for mode in modes:
                name = '%s-%s-%s-%s' % (prefix, 'ff' if kind == 'firefox' else 'cr', site, mode)
                if (P / 'runs' / name).exists():
                    say('skip ' + name)
                    continue
                try:
                    close_notices()
                    run(site, mode, name, driver)
                    say('ran ' + name)
                except BaseException:
                    say('ERROR ' + name + ' ' + traceback.format_exc()[-600:])
        try:
            browser_stop()
            subprocess.run([sys.executable, str(P / 'rmprofile.py'), str(P / ('profile-' + kind))], capture_output=True)
        except BaseException as e:
            say('browser stop: %s' % e)
    (P / (prefix + '-campaign.done')).write_text('done')


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:2] == ['browser', 'start']:
        browser_start(a[2])
    elif a[:2] == ['browser', 'stop']:
        browser_stop()
    elif a[0] == 'resident':
        resident(a[1])
    elif a[0] == 'run':
        run(a[1], a[2], a[3], '--driver' in a)
    elif a[0] == 'verify':
        verify(a[1])
    elif a[0] == 'campaign':
        campaign(a[1], a[2].split(','), a[3].split(','), a[4].split(','), '--driver' in a)
    elif a[0] == 'strip':
        strip(a[1], int(a[2]), int(a[3]))
    else:
        raise SystemExit(__doc__)
